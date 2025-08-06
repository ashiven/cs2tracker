import time
from datetime import datetime

from requests import RequestException
from requests.adapters import HTTPAdapter, Retry
from requests_cache import CachedSession
from tenacity import RetryError, retry, stop_after_attempt

from cs2tracker.config import get_config
from cs2tracker.constants import AUTHOR_STRING, BANNER
from cs2tracker.logs import PriceLogs
from cs2tracker.scraper.discord_notifier import DiscordNotifier
from cs2tracker.scraper.parser import Parser
from cs2tracker.util.currency_conversion import convert, to_symbol
from cs2tracker.util.padded_console import get_console

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


class SheetNotFoundError:
    def __init__(self):
        self.message = "Could not find sheet to update."


class Scraper:
    def __init__(self):
        """Initialize the Scraper class."""
        self._start_session()
        self.error_stack = []

        # We set the conversion currency as an attribute of the Scraper instance
        # and only update it from the config at the start of the scraping process.
        # This allows us to use the same conversion currency throughout the scraping
        # process and prevents issues with changing the conversion currency while scraping.
        self.conversion_currency = config.conversion_currency
        self.totals = {
            price_source: {
                "USD": 0.0,
                self.conversion_currency: 0.0,
            }
            for price_source in Parser.SOURCES
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

    def _error(self, error):
        """Add an error to the error stack and print the last error message from the
        error stack.
        """
        self.error_stack.append(error)
        console.error(f"{error.message}")

    def _prepare_new_run(self):
        """
        Reset totals for the next run and get the most recent conversion currency from
        the config.

        This way, we don't have to create a new Scraper instance for each run.
        """
        self.error_stack.clear()
        self.conversion_currency = config.conversion_currency
        self.totals = {
            price_source: {
                "USD": 0.0,
                self.conversion_currency: 0.0,
            }
            for price_source in Parser.SOURCES
        }

    def scrape_prices(self, update_sheet_callback=None):
        """
        Scrape prices for capsules and cases, calculate totals in USD and conversion
        currency, and print/save the results.

        :param update_sheet_callback: Optional callback function to update a tksheet
            that is displayed in the GUI with the latest scraper price calculation.
        """
        if not config.valid:
            self._error(ConfigError())
            return

        self._prepare_new_run()

        for section in config.sections():
            if section in ("User Settings", "App Settings"):
                continue
            self._scrape_item_prices(section, update_sheet_callback)

        self._convert_totals()
        self._print_totals(update_sheet_callback)
        self._send_discord_notification()

        usd_totals = [self.totals[price_source]["USD"] for price_source in Parser.SOURCES]
        PriceLogs.save(usd_totals)

    def _convert_totals(self):
        """
        Convert the total prices from USD to the configured conversion currency and
        update the totals dictionary.

        with the converted totals.
        """
        for price_source, totals in self.totals.items():
            usd_total = totals["USD"]
            converted_total = convert(usd_total, "USD", self.conversion_currency)
            self.totals.update({price_source: {"USD": usd_total, self.conversion_currency: converted_total}})  # type: ignore

    def _print_totals(self, update_sheet_callback=None):
        """
        Print the total prices in USD and converted currency, formatted with titles and
        separators.

        :param update_sheet_callback: Optional callback function to update a tksheet
            with the final totals.
        """
        console.title("USD Total", "green")
        for price_source, totals in self.totals.items():
            usd_total = totals["USD"]
            console.print(f"{price_source.name.title():<10}: ${usd_total:.2f}")

        console.title(f"{self.conversion_currency} Total", "green")
        for price_source, totals in self.totals.items():
            converted_total = totals[self.conversion_currency]
            console.print(
                f"{price_source.name.title():<10}: {to_symbol(self.conversion_currency)}{converted_total:.2f}"
            )

        if update_sheet_callback and not (
            self.error_stack and isinstance(self.error_stack[-1], SheetNotFoundError)
        ):
            update_sheet_callback(["", ""] + ["", ""] * len(Parser.SOURCES))
            for price_source, totals in self.totals.items():
                usd_total = totals["USD"]
                converted_total = totals[self.conversion_currency]
                update_sheet_callback(
                    [
                        f"[{datetime.now().strftime('%Y-%m-%d')}] {price_source.name.title()} Total:",
                        f"${usd_total:.2f}",
                        f"{to_symbol(self.conversion_currency)}{converted_total:.2f}",
                        "",
                    ]
                )

    def _send_discord_notification(self):
        """Send a message to a Discord webhook if notifications are enabled in the
        config file and a webhook URL is provided.
        """
        discord_webhook_url = config.discord_webhook_url

        if config.discord_notifications and discord_webhook_url:
            DiscordNotifier.notify(discord_webhook_url)

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
        proxy_api_key = config.proxy_api_key

        if config.use_proxy and proxy_api_key:
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
            self._error(PageLoadError(page.status_code))
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
        for price_source in Parser.SOURCES:
            try:
                item_page_url = Parser.get_item_page_url(item_href, price_source)
                item_page = self._get_page(item_page_url)
                price_usd = Parser.parse_item_price(item_page, item_href, price_source)

                price_usd_owned = round(float(int(owned) * price_usd), 2)
                self.totals[price_source]["USD"] += price_usd_owned

                prices += [price_usd, price_usd_owned]
                console.price(
                    Parser.PRICE_INFO,
                    owned,
                    price_source.name.title(),
                    price_usd,
                    price_usd_owned,
                )
            except ValueError as error:
                prices += [0.0, 0.0]
                self._error(ParsingError(error))

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
            if self.error_stack and isinstance(
                self.error_stack[-1], (RequestLimitExceededError, SheetNotFoundError)
            ):
                break
            if int(owned) == 0:
                continue

            item_name = config.option_to_name(item_href, href=True)
            console.title(item_name, "magenta")
            try:
                prices = self._scrape_prices_from_all_sources(item_href, owned)

                if update_sheet_callback:
                    try:
                        update_sheet_callback([item_name, owned] + prices)
                    except Exception:
                        self._error(SheetNotFoundError())

                if not config.use_proxy and Parser.NEEDS_TIMEOUT:
                    time.sleep(1)
            except RetryError:
                self._error(RequestLimitExceededError())
            except Exception as error:
                self._error(UnexpectedError(error))


if __name__ == "__main__":
    scraper = Scraper()
    console.print(f"[bold yellow]{BANNER}\n{AUTHOR_STRING}\n")
    scraper.scrape_prices()
