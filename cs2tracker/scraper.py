import csv
import os
import sys
import time
from configparser import ConfigParser
from datetime import datetime
from subprocess import DEVNULL, call

from bs4 import BeautifulSoup
from bs4.element import Tag
from currency_converter import CurrencyConverter
from requests import RequestException, Session
from requests.adapters import HTTPAdapter, Retry
from rich.console import Console
from tenacity import RetryError, retry, stop_after_attempt

from cs2tracker.constants import (
    CAPSULE_INFO,
    CASE_HREFS,
    CASE_PAGES,
    CONFIG_FILE,
    OUTPUT_FILE,
)

MAX_LINE_LEN = 72
SEPARATOR = "-"
PRICE_INFO = "Owned: {}      Steam market price: ${}      Total: ${}\n"


class Scraper:
    def __init__(self):
        """Initialize the Scraper class."""
        self.console = Console()
        self.parse_config()
        self._start_session()

        self.usd_total = 0
        self.eur_total = 0

    def parse_config(self):
        """Parse the configuration file to read settings and user-owned items."""
        self.config = ConfigParser()
        self.config.read(CONFIG_FILE)

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
        capsule_usd_total = 0
        try:
            capsule_usd_total = self.scrape_capsule_section_prices()
        except (RequestException, AttributeError, RetryError, ValueError):
            self.console.print(
                "[bold red] [!] Failed to scrape capsule prices. (Consider using proxies to prevent rate limiting)\n"
            )

        case_usd_total = 0
        try:
            case_usd_total = self._scrape_case_prices()
        except (RequestException, AttributeError, RetryError, ValueError):
            self.console.print(
                "[bold red][!] Failed to scrape case prices. (Consider using proxies to prevent rate limiting)\n"
            )

        self.usd_total += capsule_usd_total
        self.usd_total += case_usd_total
        self.eur_total = CurrencyConverter().convert(self.usd_total, "USD", "EUR")

        self._print_total()
        self._save_price_log()

        # Reset totals for next run
        self.usd_total, self.eur_total = 0, 0

    def _print_total(self):
        """Print the total prices in USD and EUR, formatted with titles and
        separators.
        """
        usd_title = "USD Total".center(MAX_LINE_LEN, SEPARATOR)
        self.console.print(f"[bold green]{usd_title}")
        self.console.print(f"${self.usd_total:.2f}")

        eur_title = "EUR Total".center(MAX_LINE_LEN, SEPARATOR)
        self.console.print(f"[bold green]{eur_title}")
        self.console.print(f"€{self.eur_total:.2f}")

        end_string = SEPARATOR * MAX_LINE_LEN
        self.console.print(f"[bold green]{end_string}\n")

    def _save_price_log(self):
        """
        Save the current date and total prices in USD and EUR to a CSV file.

        This will append a new entry to the output file if no entry has been made for
        today.
        """
        if not os.path.isfile(OUTPUT_FILE):
            open(OUTPUT_FILE, "w", encoding="utf-8").close()

        with open(OUTPUT_FILE, "r", encoding="utf-8") as price_logs:
            price_logs_reader = csv.reader(price_logs)
            last_log_date = ""
            for row in price_logs_reader:
                last_log_date, _ = row

        today = datetime.now().strftime("%Y-%m-%d")
        if last_log_date != today:
            with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as price_logs:
                price_logs_writer = csv.writer(price_logs)
                price_logs_writer.writerow([today, f"{self.usd_total:.2f}$"])
                price_logs_writer.writerow([today, f"{self.eur_total:.2f}€"])

    def read_price_log(self):
        """
        Parse the output file to extract dates, dollar prices, and euro prices. This
        data is used for drawing the plot of past prices.

        :return: A tuple containing three lists: dates, dollar prices, and euro prices.
        """
        if not os.path.isfile(OUTPUT_FILE):
            open(OUTPUT_FILE, "w", encoding="utf-8").close()

        dates, dollars, euros = [], [], []
        with open(OUTPUT_FILE, "r", encoding="utf-8") as price_logs:
            price_logs_reader = csv.reader(price_logs)
            for row in price_logs_reader:
                date, price_with_currency = row
                date = datetime.strptime(date, "%Y-%m-%d")
                price = float(price_with_currency.rstrip("$€"))
                if price_with_currency.endswith("€"):
                    euros.append(price)
                else:
                    dollars.append(price)
                    # Only append every second date since the dates are the same for euros and dollars
                    # and we want the length of dates to match the lengths of dollars and euros
                    dates.append(date)

        return dates, dollars, euros

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
        use_proxy = self.config.getboolean("Settings", "Use_Proxy", fallback=False)
        api_key = self.config.get("Settings", "API_Key", fallback=None)
        if use_proxy and api_key:
            page = self.session.get(
                url=url,
                proxies={
                    "http": f"http://{api_key}:@smartproxy.crawlbase.com:8012",
                    "https": f"http://{api_key}:@smartproxy.crawlbase.com:8012",
                },
                verify=False,
            )
        else:
            page = self.session.get(url)

        if not page.ok or not page.content:
            status = page.status_code
            self.console.print(f"[bold red][!] Failed to load page ({status}). Retrying...\n")
            raise RequestException(f"Failed to load page: {url}")

        return page

    def _parse_capsule_price(self, capsule_page, capsule_href):
        """
        Parse the price of a capsule from the given page and href.

        :param capsule_page: The HTTP response object containing the capsule page
            content.
        :param capsule_href: The href of the capsule listing to find the price for.
        :return: The price of the capsule as a float.
        :raises ValueError: If the capsule listing or price span cannot be found.
        """
        capsule_soup = BeautifulSoup(capsule_page.content, "html.parser")
        capsule_listing = capsule_soup.find("a", attrs={"href": f"{capsule_href}"})
        if not isinstance(capsule_listing, Tag):
            raise ValueError(f"Failed to find capsule listing: {capsule_href}")

        price_span = capsule_listing.find("span", attrs={"class": "normal_price"})
        if not isinstance(price_span, Tag):
            raise ValueError(f"Failed to find price span in capsule listing: {capsule_href}")

        price_str = price_span.text.split()[2]
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
        self.console.print(f"[bold magenta]{capsule_title}")

        capsule_usd_total = 0
        capsule_page = self._get_page(capsule_info["page"])
        for capsule_name, capsule_href in zip(capsule_info["names"], capsule_info["items"]):
            config_capsule_name = capsule_name.replace(" ", "_")
            owned = self.config.getint(capsule_section, config_capsule_name, fallback=0)
            if owned == 0:
                continue

            price_usd = self._parse_capsule_price(capsule_page, capsule_href)
            price_usd_owned = round(float(owned * price_usd), 2)

            self.console.print(f"[bold deep_sky_blue4]{capsule_name}")
            self.console.print(PRICE_INFO.format(owned, price_usd, price_usd_owned))
            capsule_usd_total += price_usd_owned

        return capsule_usd_total

    def scrape_capsule_section_prices(self):
        """Scrape prices for all capsule sections defined in the configuration."""
        capsule_usd_total = 0
        for capsule_section, capsule_info in CAPSULE_INFO.items():
            # Only scrape capsule sections where the user owns at least one item
            if any(int(owned) > 0 for _, owned in self.config.items(capsule_section)):
                capsule_usd_total += self._scrape_capsule_prices(capsule_section, capsule_info)

        return capsule_usd_total

    def _parse_case_price(self, case_page, case_href):
        """
        Parse the price of a case from the given page and href.

        :param case_page: The HTTP response object containing the case page content.
        :param case_href: The href of the case listing to find the price for.
        :return: The price of the case as a float.
        :raises ValueError: If the case listing or price span cannot be found.
        """
        case_soup = BeautifulSoup(case_page.content, "html.parser")
        case_listing = case_soup.find("a", attrs={"href": case_href})
        if not isinstance(case_listing, Tag):
            raise ValueError(f"Failed to find case listing: {case_href}")

        price_class = case_listing.find("span", attrs={"class": "normal_price"})
        if not isinstance(price_class, Tag):
            raise ValueError(f"Failed to find price class in case listing: {case_href}")

        price_str = price_class.text.split()[2]
        price = float(price_str.replace("$", ""))

        return price

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
            self.console.print(f"[bold magenta]{case_title}")

            case_page = self._get_page(CASE_PAGES[case_index])
            price_usd = self._parse_case_price(case_page, CASE_HREFS[case_index])
            price_usd_owned = round(float(int(owned) * price_usd), 2)

            self.console.print(PRICE_INFO.format(owned, price_usd, price_usd_owned))
            case_usd_total += price_usd_owned

            if not self.config.getboolean("Settings", "Use_Proxy", fallback=False):
                time.sleep(1)

        return case_usd_total

    def identify_background_task(self):
        """
        Search the OS for a daily background task that runs the scraper.

        :return: True if a background task is found, False otherwise.
        """
        if sys.platform.startswith("win"):
            task_name = "CS2Tracker Daily Calculation"
            cmd = ["schtasks", "/query", "/tn", task_name]
            return_code = call(cmd, stdout=DEVNULL, stderr=DEVNULL)
            found = True if return_code == 0 else False
            return found
        else:
            # TODO: implement finder for cron jobs
            pass

    def toggle_background_task(self, enabled: bool):
        """
        Create or delete a daily background task that runs the scraper.

        :param enabled: If True, the task will be created; if False, the task will be
            deleted.
        """
        if sys.platform.startswith("win"):
            task_name = "CS2Tracker Daily Calculation"
            if enabled:
                python_path = sys.executable.replace("\\", "/")
                task_command = f"{python_path} -m cs2tracker.scraper"
                cmd = [
                    "schtasks",
                    "/create",
                    "/tn",
                    task_name,
                    "/tr",
                    task_command,
                    "/sc",
                    "DAILY",
                    "/st",
                    "12:00",
                ]
                return_code = call(cmd, stdout=DEVNULL, stderr=DEVNULL)
                created = True if return_code == 0 else False
                return created
            else:
                cmd = ["schtasks", "/delete", "/tn", task_name, "/f"]
                return_code = call(cmd, stdout=DEVNULL, stderr=DEVNULL)
                deleted = True if return_code == 0 else False
                return deleted
        else:
            # TODO: implement toggle for cron jobs
            pass


if __name__ == "__main__":
    # If this file is run as a script, create a Scraper instance and run the
    # scrape_prices method.
    scraper = Scraper()
    scraper.scrape_prices()
