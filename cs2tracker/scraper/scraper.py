import time
from urllib.parse import unquote

from bs4 import BeautifulSoup
from bs4.element import Tag
from currency_converter import CurrencyConverter
from requests import RequestException, Session
from requests.adapters import HTTPAdapter, Retry
from tenacity import RetryError, retry, stop_after_attempt

from cs2tracker.constants import AUTHOR_STRING, BANNER, CAPSULE_INFO, CASE_HREFS
from cs2tracker.scraper.discord_notifier import DiscordNotifier
from cs2tracker.util import PaddedConsole, PriceLogs, ValidatedConfig

MAX_LINE_LEN = 72
SEPARATOR = "-"
PRICE_INFO = "Owned: {:<10}  Steam market price: ${:<10}  Total: ${:<10}\n"

HTTP_PROXY_URL = "http://{}:@smartproxy.crawlbase.com:8012"
HTTPS_PROXY_URL = "http://{}:@smartproxy.crawlbase.com:8012"

console = PaddedConsole()


class Scraper:
    def __init__(self):
        """Initialize the Scraper class."""
        self.load_config()
        self._start_session()

        self.usd_total = 0
        self.eur_total = 0

    def load_config(self):
        """Load the configuration file and validate its contents."""
        self.config = ValidatedConfig()

    def _start_session(self):
        """Start a requests session with custom headers and retry logic."""
        self.session = Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }
        )
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504, 520])
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def scrape_prices(self):
        """Scrape prices for capsules and cases, calculate totals in USD and EUR, and
        print/save the results.
        """
        if not self.config.valid:
            console.print(
                "[bold red][!] Invalid configuration. Please fix the config file before running."
            )
            return

        capsule_usd_total = self._scrape_capsule_section_prices()
        case_usd_total = self._scrape_case_prices()
        custom_item_usd_total = self._scrape_custom_item_prices()

        self.usd_total += capsule_usd_total
        self.usd_total += case_usd_total
        self.usd_total += custom_item_usd_total
        self.eur_total = CurrencyConverter().convert(self.usd_total, "USD", "EUR")

        self._print_total()
        PriceLogs.save(self.usd_total, self.eur_total)
        self._send_discord_notification()

        # Reset totals for next run
        self.usd_total, self.eur_total = 0, 0

    def _print_total(self):
        """Print the total prices in USD and EUR, formatted with titles and
        separators.
        """
        usd_title = "USD Total".center(MAX_LINE_LEN, SEPARATOR)
        console.print(f"[bold green]{usd_title}")
        console.print(f"${self.usd_total:.2f}")

        eur_title = "EUR Total".center(MAX_LINE_LEN, SEPARATOR)
        console.print(f"[bold green]{eur_title}")
        console.print(f"€{self.eur_total:.2f}")

        end_string = SEPARATOR * MAX_LINE_LEN
        console.print(f"[bold green]{end_string}\n")

    def _send_discord_notification(self):
        """Send a message to a Discord webhook if notifications are enabled in the
        config file and a webhook URL is provided.
        """
        discord_notifications = self.config.getboolean(
            "App Settings", "discord_notifications", fallback=False
        )
        webhook_url = self.config.get("User Settings", "discord_webhook_url", fallback=None)

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
        use_proxy = self.config.getboolean("App Settings", "use_proxy", fallback=False)
        proxy_api_key = self.config.get("User Settings", "proxy_api_key", fallback=None)

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
            console.print(f"[bold red][!] Failed to load page ({page.status_code}). Retrying...\n")
            raise RequestException(f"Failed to load page: {url}")

        return page

    def _parse_item_price(self, item_page, item_href):
        """
        Parse the price of an item from the given steamcommunity market page and item
        href.

        :param item_page: The HTTP response object containing the item page content.
        :param item_href: The href of the item listing to find the price for.
        :return: The price of the item as a float.
        :raises ValueError: If the item listing or price span cannot be found.
        """
        item_soup = BeautifulSoup(item_page.content, "html.parser")
        item_listing = item_soup.find("a", attrs={"href": f"{item_href}"})
        if not isinstance(item_listing, Tag):
            raise ValueError(f"Failed to find item listing: {item_href}")

        item_price_span = item_listing.find("span", attrs={"class": "normal_price"})
        if not isinstance(item_price_span, Tag):
            raise ValueError(f"Failed to find price span in item listing: {item_href}")

        price_str = item_price_span.text.split()[2]
        price = float(price_str.replace("$", ""))

        return price

    def _scrape_capsule_prices(
        self,
        capsule_section,
        capsule_info,
    ):
        """
        Scrape prices for a specific capsule section, printing the details to the
        console.

        :param capsule_section: The section name in the config for the capsule.
        :param capsule_info: A dictionary containing information about the capsule page,
            hrefs, and names.
        """
        capsule_title = capsule_section.center(MAX_LINE_LEN, SEPARATOR)
        console.print(f"[bold magenta]{capsule_title}\n")

        capsule_usd_total = 0
        try:
            capsule_page = self._get_page(capsule_info["page"])
            for capsule_name, capsule_href in zip(capsule_info["names"], capsule_info["items"]):
                config_capsule_name = capsule_name.replace(" ", "_").lower()
                owned = self.config.getint(capsule_section, config_capsule_name, fallback=0)
                if owned == 0:
                    continue

                price_usd = self._parse_item_price(capsule_page, capsule_href)
                price_usd_owned = round(float(owned * price_usd), 2)

                console.print(f"[bold deep_sky_blue4]{capsule_name}")
                console.print(PRICE_INFO.format(owned, price_usd, price_usd_owned))
                capsule_usd_total += price_usd_owned
        except (RetryError, ValueError):
            console.print(
                "[bold red][!] Too many requests. (Consider using proxies to prevent rate limiting)\n"
            )
        except Exception as error:
            console.print(f"[bold red][!] An unexpected error occurred: {error}\n")

        return capsule_usd_total

    def _scrape_capsule_section_prices(self):
        """Scrape prices for all capsule sections defined in the configuration."""
        capsule_usd_total = 0
        for capsule_section, capsule_info in CAPSULE_INFO.items():
            # Only scrape capsule sections where the user owns at least one item
            if any(int(owned) > 0 for _, owned in self.config.items(capsule_section)):
                capsule_usd_total += self._scrape_capsule_prices(capsule_section, capsule_info)

        return capsule_usd_total

    def _market_page_from_href(self, item_href):
        """
        Convert an href of a Steam Community Market item to a market page URL.

        :param item_href: The href of the item listing, typically ending with the item's
            name.
        :return: A URL string for the Steam Community Market page of the item.
        """
        url_encoded_name = item_href.split("/")[-1]
        page_url = f"https://steamcommunity.com/market/search?q={url_encoded_name}"

        return page_url

    def _scrape_case_prices(self):
        """
        Scrape prices for all cases defined in the configuration.

        For each case, it prints the case name, owned count, price per item, and total
        price for owned items.
        """
        case_usd_total = 0
        for case_index, (config_case_name, owned) in enumerate(self.config.items("Cases")):
            if int(owned) == 0:
                continue

            case_name = config_case_name.replace("_", " ").title()
            case_title = case_name.center(MAX_LINE_LEN, SEPARATOR)
            console.print(f"[bold magenta]{case_title}\n")

            try:
                case_page_url = self._market_page_from_href(CASE_HREFS[case_index])
                case_page = self._get_page(case_page_url)
                price_usd = self._parse_item_price(case_page, CASE_HREFS[case_index])
                price_usd_owned = round(float(int(owned) * price_usd), 2)

                console.print(PRICE_INFO.format(owned, price_usd, price_usd_owned))
                case_usd_total += price_usd_owned

                if not self.config.getboolean("App Settings", "use_proxy", fallback=False):
                    time.sleep(1)
            except (RetryError, ValueError):
                console.print(
                    "[bold red][!] Too many requests. (Consider using proxies to prevent rate limiting)\n"
                )
            except Exception as error:
                console.print(f"[bold red][!] An unexpected error occurred: {error}\n")

        return case_usd_total

    def _scrape_custom_item_prices(self):
        """
        Scrape prices for custom items defined in the configuration.

        For each custom item, it prints the item name, owned count, price per item, and
        total price for owned items.
        """
        custom_item_usd_total = 0
        for custom_item_href, owned in self.config.items("Custom Items"):
            if int(owned) == 0:
                continue

            custom_item_name = unquote(custom_item_href.split("/")[-1])
            custom_item_title = custom_item_name.center(MAX_LINE_LEN, SEPARATOR)
            console.print(f"[bold magenta]{custom_item_title}\n")

            try:
                custom_item_page_url = self._market_page_from_href(custom_item_href)
                custom_item_page = self._get_page(custom_item_page_url)
                price_usd = self._parse_item_price(custom_item_page, custom_item_href)
                price_usd_owned = round(float(int(owned) * price_usd), 2)

                console.print(PRICE_INFO.format(owned, price_usd, price_usd_owned))
                custom_item_usd_total += price_usd_owned

                if not self.config.getboolean("App Settings", "use_proxy", fallback=False):
                    time.sleep(1)
            except (RetryError, ValueError):
                console.print(
                    "[bold red][!] Too many requests. (Consider using proxies to prevent rate limiting)\n"
                )
            except Exception as error:
                console.print(f"[bold red][!] An unexpected error occurred: {error}\n")

        return custom_item_usd_total

    def toggle_use_proxy(self, enabled: bool):
        """
        Toggle the use of proxies for requests. This will update the configuration file.

        :param enabled: If True, proxies will be used; if False, they will not be used.
        """
        self.config.toggle_use_proxy(enabled)

    def toggle_discord_webhook(self, enabled: bool):
        """
        Toggle the use of a Discord webhook to notify users of price calculations.

        :param enabled: If True, the webhook will be used; if False, it will not be
            used.
        """
        self.config.toggle_discord_webhook(enabled)


if __name__ == "__main__":
    scraper = Scraper()
    console.print(f"[bold yellow]{BANNER}\n{AUTHOR_STRING}\n")
    scraper.scrape_prices()
