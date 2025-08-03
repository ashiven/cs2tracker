import time
from datetime import datetime

from currency_converter import CurrencyConverter
from requests import RequestException
from requests.adapters import HTTPAdapter, Retry
from requests_cache import CachedSession
from tenacity import RetryError, retry, stop_after_attempt

from cs2tracker.constants import AUTHOR_STRING, BANNER
from cs2tracker.scraper.discord_notifier import DiscordNotifier
from cs2tracker.scraper.parsers import CSGOTrader, PriceSource
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
        self.totals = {
            price_source: {"usd": 0.0, "eur": 0.0} for price_source in self.parser.SOURCES
        }

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
            console.error(f"{last_error.message}")

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
        self.error_stack.clear()
        self.totals = {
            price_source: {"usd": 0.0, "eur": 0.0} for price_source in self.parser.SOURCES
        }

        for section in config.sections():
            if section in ("User Settings", "App Settings"):
                continue
            self._scrape_item_prices(section, update_sheet_callback)

        for price_source, totals in self.totals.items():
            usd_total = totals["usd"]
            eur_total = CurrencyConverter().convert(usd_total, "USD", "EUR")
            self.totals.update({price_source: {"usd": usd_total, "eur": eur_total}})  # type: ignore

        if update_sheet_callback:
            update_sheet_callback(["", ""] + ["", ""] * len(self.parser.SOURCES))
            for price_source, totals in self.totals.items():
                usd_total = totals["usd"]
                eur_total = totals["eur"]
                update_sheet_callback(
                    [
                        f"[{datetime.now().strftime('%Y-%m-%d')}] {price_source.value.title()} Total:",
                        f"${usd_total:.2f}",
                        f"€{eur_total:.2f}",
                        "",
                    ]
                )

        self._print_total()
        self._send_discord_notification()

        # TODO: modify price logs, charts etc for multiple sources (only use steam as source for now)
        steam_usd_total = self.totals[PriceSource.STEAM]["usd"]
        steam_eur_total = self.totals[PriceSource.STEAM]["eur"]
        PriceLogs.save(steam_usd_total, steam_eur_total)

    def _print_total(self):
        """Print the total prices in USD and EUR, formatted with titles and
        separators.
        """
        console.title("USD Total", "green")
        for price_source, totals in self.totals.items():
            usd_total = totals.get("usd")
            console.print(f"{price_source.value.title():<10}: ${usd_total:.2f}")

        console.title("EUR Total", "green")
        for price_source, totals in self.totals.items():
            eur_total = totals.get("eur")
            console.print(f"{price_source.value.title():<10}: €{eur_total:.2f}")

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

    def _scrape_prices_from_all_sources(self, item_href, owned):
        """
        For a given item href and owned count, scrape the item's price from all sources
        available to the currently registered parser.

        :param item_href: The url of the steamcommunity market listing of the item
        :param owned: How many of this item the user owns
        :return: A list of item prices for the different sources
        :raises RequestException: If the request fails.
        :raises RetryError: If the retry limit is reached.
        :raises ValueError: If the parser could not find the item
        """
        prices = []
        for price_source in self.parser.SOURCES:
            try:
                item_page_url = self.parser.get_item_page_url(item_href, price_source)
                item_page = self._get_page(item_page_url)
                price_usd = self.parser.parse_item_price(item_page, item_href, price_source)

                price_usd_owned = round(float(int(owned) * price_usd), 2)
                self.totals[price_source]["usd"] += price_usd_owned

                prices += [price_usd, price_usd_owned]
                console.price(
                    self.parser.PRICE_INFO,
                    owned,
                    price_source.value.title(),
                    price_usd,
                    price_usd_owned,
                )
            except ValueError as error:
                prices += [0.0, 0.0]
                self.error_stack.append(ParsingError(error))
                self._print_error()

        return prices

    def _scrape_item_prices(self, section, update_sheet_callback=None):
        """
        Scrape prices for all items defined in a configuration section that uses hrefs
        as option keys.

        For each item, it prints the item name, owned count, price per item, and total
        price for owned items.

        :param update_sheet_callback: Optional callback function to update a tksheet
            that is displayed in the GUI with the latest scraper price calculation.
        """
        for item_href, owned in config.items(section):
            if self.error_stack and isinstance(self.error_stack[-1], RequestLimitExceededError):
                break
            if int(owned) == 0:
                continue

            item_name = config.option_to_name(item_href, href=True)
            console.title(item_name, "magenta")
            try:
                prices = self._scrape_prices_from_all_sources(item_href, owned)

                if update_sheet_callback:
                    update_sheet_callback([item_name, owned] + prices)

                if (
                    not config.getboolean("App Settings", "use_proxy", fallback=False)
                    and self.parser.NEEDS_TIMEOUT
                ):
                    time.sleep(1)
            except RetryError:
                self.error_stack.append(RequestLimitExceededError())
                self._print_error()
            except Exception as error:
                self.error_stack.append(UnexpectedError(error))
                self._print_error()


if __name__ == "__main__":
    scraper = Scraper()
    console.print(f"[bold yellow]{BANNER}\n{AUTHOR_STRING}\n")
    scraper.scrape_prices()
