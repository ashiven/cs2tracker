import csv
import os
import time
from configparser import ConfigParser
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from currency_converter import CurrencyConverter
from requests.adapters import HTTPAdapter, Retry
from rich.console import Console
from tenacity import retry, stop_after_attempt

from .constants import CAPSULE_INFO, CASE_HREFS, CASE_PAGES, CONFIG_FILE, OUTPUT_FILE

MAX_LINE_LEN = 72
SEPARATOR = "-"


class Scraper:
    def __init__(self):
        self.console = Console()
        self.parse_config()
        self._start_session()

        self.usd_total = 0
        self.eur_total = 0

    def parse_config(self):
        self.config = ConfigParser()
        self.config.read(CONFIG_FILE)

    def _start_session(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            }
        )
        retries = Retry(
            total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504, 520]
        )
        self.session.mount("http://", HTTPAdapter(max_retries=retries))
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def scrape_prices(self):
        capsule_usd_total = 0
        for capsule_name, capsule_info in CAPSULE_INFO.items():
            capsule_usd_total += self._scrape_prices_capsule(capsule_name, capsule_info)

        case_usd_total = self._scrape_prices_case()

        self.usd_total += capsule_usd_total
        self.usd_total += case_usd_total
        self.eur_total = CurrencyConverter().convert(self.usd_total, "USD", "EUR")

        self.print_total()
        self.save_to_file()

        # reset totals for next run
        self.usd_total, self.eur_total = 0, 0

    def print_total(self):
        usd_title = "USD Total".center(MAX_LINE_LEN, SEPARATOR)
        self.console.print(f"[bold green]{usd_title}")
        self.console.print(f"${self.usd_total:.2f}")

        eur_title = "EUR Total".center(MAX_LINE_LEN, SEPARATOR)
        self.console.print(f"[bold green]{eur_title}")
        self.console.print(f"€{self.eur_total:.2f}")

        end_string = SEPARATOR * MAX_LINE_LEN
        self.console.print(f"[bold green]{end_string}\n")

    def save_to_file(self):
        if not os.path.isfile(OUTPUT_FILE):
            open(OUTPUT_FILE, "w", encoding="utf-8").close()

        with open(OUTPUT_FILE, "r", encoding="utf-8") as price_logs:
            price_logs_reader = csv.reader(price_logs)
            last_row = None
            for row in price_logs_reader:
                last_row = row
            if last_row:
                last_log_date = last_row[0][:10]
            else:
                last_log_date = ""

        today = datetime.now().strftime("%Y-%m-%d")
        if last_log_date != today:
            with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as price_logs:
                price_logs_writer = csv.writer(price_logs)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                price_logs_writer.writerow([now, f"{self.usd_total:.2f}$"])
                price_logs_writer.writerow([now, f"{self.eur_total:.2f}€"])

    @retry(stop=stop_after_attempt(10))
    def _get_page(self, url):
        use_proxy = self.config.getboolean("settings", "Use_Proxy", fallback=False)
        api_key = self.config.get("settings", "API_Key", fallback="")
        if use_proxy:
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
            self.console.print(
                f"[bold red][!] Failed to load page ({status}). Retrying...\n"
            )
            raise requests.RequestException(f"Failed to load page: {url}")

        return page

    def _parse_capsule_price(self, capsule_page, capsule_href):
        capsule_soup = BeautifulSoup(capsule_page.content, "html.parser")
        capsule_listing = capsule_soup.find("a", attrs={"href": f"{capsule_href}"})
        if not isinstance(capsule_listing, Tag):
            raise ValueError(f"Failed to find capsule listing: {capsule_href}")

        price_span = capsule_listing.find("span", attrs={"class": "normal_price"})
        if not isinstance(price_span, Tag):
            raise ValueError(
                f"Failed to find price span in capsule listing: {capsule_href}"
            )

        price_str = price_span.text.split()[2]
        price = float(price_str.replace("$", ""))

        return price

    def _scrape_prices_capsule(
        self,
        capsule_section,
        capsule_info,
    ):
        capsule_title = capsule_section.center(MAX_LINE_LEN, SEPARATOR)
        self.console.print(f"[bold magenta]{capsule_title}")

        capsule_page = capsule_info["page"]
        capsule_names = capsule_info["names"]
        capsule_hrefs = capsule_info["items"]
        capsule_price_total = 0
        # TODO: only get page if owned > 0 for any item
        capsule_page = self._get_page(capsule_page)
        for capsule_name, capsule_href in zip(capsule_names, capsule_hrefs):
            config_capsule_name = capsule_name.replace(" ", "_")
            owned = self.config.getint(capsule_section, config_capsule_name, fallback=0)

            price_usd = self._parse_capsule_price(capsule_page, capsule_href)
            price_usd_owned = round(float(owned * price_usd), 2)

            self.console.print(f"[bold red]{capsule_name}")
            self.console.print(
                f"Owned: {owned}      Steam market price: ${price_usd}      Total: ${price_usd_owned}"
            )
            capsule_price_total += price_usd_owned

        return capsule_price_total

    def _parse_case_price(self, case_page, case_href):
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

    def _scrape_prices_case(self):
        case_price_total = 0
        for case_index, (config_case_name, owned) in enumerate(
            self.config.items("Cases")
        ):
            if int(owned) == 0:
                continue

            case_name = config_case_name.replace("_", " ")
            case_title = case_name.center(MAX_LINE_LEN, SEPARATOR)
            self.console.print(f"[bold magenta]{case_title}")

            case_page = self._get_page(CASE_PAGES[case_index])
            price_usd = self._parse_case_price(case_page, CASE_HREFS[case_index])
            price_usd_owned = round(float(int(owned) * price_usd), 2)

            self.console.print(
                f"Owned: {owned}      Steam market price: ${price_usd}      Total: ${price_usd_owned}\n"
            )
            case_price_total += price_usd_owned

            if not self.config.getboolean("settings", "Use_Proxy", fallback=False):
                time.sleep(1)

        return case_price_total
