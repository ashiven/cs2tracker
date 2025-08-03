import time
from datetime import datetime

from currency_converter import CurrencyConverter
from requests import RequestException
from requests.adapters import HTTPAdapter, Retry
from requests_cache import CachedSession
from tenacity import RetryError, retry, stop_after_attempt

from cs2tracker.constants import AUTHOR_STRING, BANNER
from cs2tracker.scraper.discord_notifier import DiscordNotifier
from cs2tracker.scraper.parsers import CSGOTrader
from cs2tracker.util import PriceLogs, get_config, get_console

HTTP_PROXY_URL = "http://{}:@smartproxy.crawlbase.com:8012"
HTTPS_PROXY_URL = "http://{}:@smartproxy.crawlbase.com:8012"

console = get_console()
config = get_config()


class ConfigError:
    def __init__(self):
        self.message = "Invalid configuration. Please fix the config file before running."


class ParsingError:
    def __init__(self, message):
        self.message = message


class RequestLimitExceededError:
    def __init__(self):
        self.message = "Too many requests. Consider using proxies to prevent rate limiting."


class PageLoadError:
    def __init__(self, status_code):
        self.message = f"Failed to load page: {status_code}. Retrying..."


class UnexpectedError:
    def __init__(self, error):
        self.message = f"An unexpected error occurred: {error}"


class Scraper:
    def __init__(self):
        """Initialize the Scraper class."""
        self._start_session()
        self._add_parser(CSGOTrader)

        self.error_stack = []
        self.usd_total = 0
        self.eur_total = 0

    def _start_session(self):
        """Start a requests session with custom headers and retry logic."""
        self.session = CachedSession("scraper_cache", backend="memory")
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }
        )
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504, 520])
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def _add_parser(self, parser):
        """Add a parser for a specific page where item prices should be scraped."""
        self.parser = parser

    def _print_error(self):
        """Print the last error message from the error stack, if any."""
        last_error = self.error_stack[-1] if self.error_stack else None
        if last_error:
            console.error(f"{last_error.message}\n")

    def scrape_prices(self, update_sheet_callback=None):
        """
        Scrape prices for capsules and cases, calculate totals in USD and EUR, and
        print/save the results.

        :param update_sheet_callback: Optional callback function to update a tksheet
            that is displayed in the GUI with the latest scraper price calculation.
        """
        if not config.valid:
            self.error_stack.append(ConfigError())
            self._print_error()
            return

        # Reset totals from the previous run and clear the error stack
        self.usd_total, self.eur_total = 0, 0
        self.error_stack.clear()

        for section in config.sections():
            if section in ("User Settings", "App Settings"):
                continue
            self.usd_total += self._scrape_item_prices(section, update_sheet_callback)
        self.eur_total = CurrencyConverter().convert(self.usd_total, "USD", "EUR")

        if update_sheet_callback:
            update_sheet_callback(["", "", "", ""])
            update_sheet_callback(
                [
                    f"[{datetime.now().strftime('%Y-%m-%d')}] Total:",
                    f"${self.usd_total:.2f}",
                    f"€{self.eur_total:.2f}",
                    "",
                ]
            )

        self._print_total()
        self._send_discord_notification()
        PriceLogs.save(self.usd_total, self.eur_total)

    def _print_total(self):
        """Print the total prices in USD and EUR, formatted with titles and
        separators.
        """
        console.title("USD Total", "green")
        console.print(f"${self.usd_total:.2f}")

        console.title("EUR Total", "green")
        console.print(f"€{self.eur_total:.2f}")

        console.separator("green")

    def _send_discord_notification(self):
        """Send a message to a Discord webhook if notifications are enabled in the
        config file and a webhook URL is provided.
        """
        discord_notifications = config.getboolean(
            "App Settings", "discord_notifications", fallback=False
        )
        webhook_url = config.get("User Settings", "discord_webhook_url", fallback=None)

        if discord_notifications and webhook_url:
            DiscordNotifier.notify(webhook_url)

    @retry(stop=stop_after_attempt(10))
    def _get_page(self, url):
        """
        Get the page content from the given URL, using a proxy if configured. If the
        request fails, it will retry up to 10 times.

        :param url: The URL to fetch the page from.
        :return: The HTTP response object containing the page content.
        :raises RequestException: If the request fails.
        :raises RetryError: If the retry limit is reached.
        """
        use_proxy = config.getboolean("App Settings", "use_proxy", fallback=False)
        proxy_api_key = config.get("User Settings", "proxy_api_key", fallback=None)

        if use_proxy and proxy_api_key:
            page = self.session.get(
                url=url,
                proxies={
                    "http": HTTP_PROXY_URL.format(proxy_api_key),
                    "https": HTTPS_PROXY_URL.format(proxy_api_key),
                },
                verify=False,
            )
        else:
            page = self.session.get(url)

        if not page.ok or not page.content:
            self.error_stack.append(PageLoadError(page.status_code))
            self._print_error()
            raise RequestException(f"Failed to load page: {url}")

        return page

    def _scrape_item_prices(self, section, update_sheet_callback=None):
        """
        Scrape prices for all items defined in a configuration section that uses hrefs
        as option keys.

        For each item, it prints the item name, owned count, price per item, and total
        price for owned items.

        :param update_sheet_callback: Optional callback function to update a tksheet
            that is displayed in the GUI with the latest scraper price calculation.
        """
        item_usd_total = 0
        for item_href, owned in config.items(section):
            if self.error_stack and isinstance(self.error_stack[-1], RequestLimitExceededError):
                break
            if int(owned) == 0:
                continue

            item_name = config.option_to_name(item_href, href=True)
            console.title(item_name, "magenta")
            try:
                item_page_url = self.parser.get_item_page_url(item_href)
                item_page = self._get_page(item_page_url)
                price_usd = self.parser.parse_item_price(item_page, item_href)
                price_usd_owned = round(float(int(owned) * price_usd), 2)
                self.parser.usd_total += price_usd_owned

                console.price(self.parser.PRICE_INFO, owned, price_usd, price_usd_owned)
                if update_sheet_callback:
                    update_sheet_callback([item_name, owned, price_usd, price_usd_owned])

                if (
                    not config.getboolean("App Settings", "use_proxy", fallback=False)
                    and self.parser.NEEDS_TIMEOUT
                ):
                    time.sleep(1)
            except ValueError as error:
                self.error_stack.append(ParsingError(error))
                self._print_error()
            except RetryError:
                self.error_stack.append(RequestLimitExceededError())
                self._print_error()
            except Exception as error:
                self.error_stack.append(UnexpectedError(error))
                self._print_error()

        return item_usd_total


if __name__ == "__main__":
    scraper = Scraper()
    console.print(f"[bold yellow]{BANNER}\n{AUTHOR_STRING}\n")
    scraper.scrape_prices()
