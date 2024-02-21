import configparser
import csv
import datetime
import os
import time

import requests
from bs4 import BeautifulSoup
from currency_converter import CurrencyConverter
from requests.adapters import HTTPAdapter, Retry
from rich.console import Console
from tenacity import retry, stop_after_attempt

from .constants import (
    CAPSULE_HREFS,
    CAPSULE_NAMES,
    CAPSULE_NAMES_GENERIC,
    CAPSULE_PAGES,
    CASE_HREFS,
    CASE_NAMES,
    CASE_PAGES,
    CONFIG_FILE,
    OUTPUT_FILE,
)

MAX_LINE_LEN = 50
PADDING_LEN = MAX_LINE_LEN // 2 - 1
PADDING = "-" * PADDING_LEN


class Scraper:
    def __init__(self):
        self.api_key = None
        self.use_proxy = False

        self.case_quantities = []
        self.rmr_quantities = []
        self.stockholm_quantities = []
        self.antwerp_quantities = []
        self.rio_quantities = []
        self.paris_quantities = []

        self.total_price = 0
        self.total_price_euro = 0

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

        self.console = Console()

        config = self._parse_config()
        self._set_config(config)

    def scrape_prices(self):
        for capsule_page_url in CAPSULE_PAGES:
            if "rmr" in capsule_page_url:
                capsule_name = "2020 RMR"
                capsule_quantities = self.rmr_quantities
                capsule_hrefs = CAPSULE_HREFS[0:3]
                capsule_names_generic = CAPSULE_NAMES_GENERIC[0:3]
            elif "stockholm" in capsule_page_url:
                capsule_name = "Stockholm"
                capsule_quantities = self.stockholm_quantities
                capsule_hrefs = CAPSULE_HREFS[3:8]
                capsule_names_generic = CAPSULE_NAMES_GENERIC[0:4] + [
                    CAPSULE_NAMES_GENERIC[-1]
                ]
            elif "antwerp" in capsule_page_url:
                capsule_name = "Antwerp"
                capsule_quantities = self.antwerp_quantities
                capsule_hrefs = CAPSULE_HREFS[8:15]
                capsule_names_generic = CAPSULE_NAMES_GENERIC[0:7]
            elif "rio" in capsule_page_url:
                capsule_name = "Rio"
                capsule_quantities = self.rio_quantities
                capsule_hrefs = CAPSULE_HREFS[15:22]
                capsule_names_generic = CAPSULE_NAMES_GENERIC[0:7]
            elif "paris" in capsule_page_url:
                capsule_name = "Paris"
                capsule_quantities = self.paris_quantities
                capsule_hrefs = CAPSULE_HREFS[22:29]
                capsule_names_generic = CAPSULE_NAMES_GENERIC[0:7]

            self._scrape_prices_capsule(
                capsule_page_url,
                capsule_hrefs,
                capsule_name,
                capsule_names_generic,
                capsule_quantities,
            )

        self._scrape_prices_case(
            self.case_quantities, CASE_PAGES, CASE_HREFS, CASE_NAMES
        )

    def print_total(self):
        usd_string = f"{PADDING}USD Total{PADDING}"[:MAX_LINE_LEN]
        self.console.print(f"[bold green]{usd_string}")
        self.console.print(f"${self.total_price:.2f}")

        self.total_price_euro = CurrencyConverter().convert(
            self.total_price, "USD", "EUR"
        )
        eur_string = f"{PADDING}EUR Total{PADDING}"[:MAX_LINE_LEN]
        self.console.print(f"[bold green]{eur_string}")
        self.console.print(f"€{self.total_price_euro:.2f}")
        end_string = f"{PADDING}{PADDING}{PADDING}"[:MAX_LINE_LEN]
        self.console.print(f"[bold green]{end_string}")

    def save_to_file(self):
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d")

        if not os.path.isfile(OUTPUT_FILE):
            open(OUTPUT_FILE, "w").close()

        with open(OUTPUT_FILE, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            last_row = None
            for row in reader:
                last_row = row
            if last_row:
                last_date_str = last_row[0][:10]
            else:
                last_date_str = ""

        if date != last_date_str:
            today = now.strftime("%Y-%m-%d %H:%M:%S")
            total = f"{self.total_price:.2f}$"
            total_euro = f"{self.total_price_euro:.2f}€"
            with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([today, total])
                writer.writerow([today, total_euro])

    def _parse_config(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return config

    def _set_config(self, config):
        self.use_proxy = (
            False if config.get("Proxy API Key", "Use_Proxy") == "False" else True
        )
        self.api_key = config.get("Proxy API Key", "API_Key")

        for capsule_name in CAPSULE_NAMES:
            config_capsule_name = capsule_name.replace(" ", "_")
            if "RMR" in capsule_name:
                self.rmr_quantities.append(
                    int(config.get("2020 RMR", config_capsule_name))
                )
            elif "Stockholm" in capsule_name:
                self.stockholm_quantities.append(
                    int(config.get("Stockholm", config_capsule_name))
                )
            elif "Antwerp" in capsule_name:
                self.antwerp_quantities.append(
                    int(config.get("Antwerp", config_capsule_name))
                )
            elif "Rio" in capsule_name:
                self.rio_quantities.append(int(config.get("Rio", config_capsule_name)))
            elif "Paris" in capsule_name:
                self.paris_quantities.append(
                    int(config.get("Paris", config_capsule_name))
                )

        for case_name in CASE_NAMES:
            config_case_name = case_name.replace(" ", "_")
            self.case_quantities.append(int(config.get("Cases", config_case_name)))

    @retry(stop=stop_after_attempt(10))
    def _get_page(self, url):
        if self.use_proxy:
            page = self.session.get(
                url=url,
                proxies={
                    "http": f"http://{self.api_key}:@smartproxy.crawlbase.com:8012",
                    "https": f"http://{self.api_key}:@smartproxy.crawlbase.com:8012",
                },
                verify=False,
            )
        else:
            page = self.session.get(url)

        return page

    def _scrape_prices_capsule(
        self,
        capsule_page_url,
        capsule_hrefs,
        capsule_name,
        capsule_names_generic,
        capsule_quantities,
    ):
        if any([quantity > 0 for quantity in capsule_quantities]):
            title_string = f"{PADDING}{capsule_name}{PADDING}"[:MAX_LINE_LEN]
            self.console.print(f"[bold magenta]{title_string}")

            page = self._get_page(capsule_page_url)
            soup = BeautifulSoup(page.content, "html.parser")

            for href_index, href in enumerate(capsule_hrefs):
                if capsule_quantities[href_index] > 0:
                    try:
                        listing = soup.find("a", attrs={"href": f"{href}"})
                        retries = 0
                        while not listing and retries < 5:
                            self.console.print(
                                f"[bold red][!] Failed to load page ({page.status_code}). Retrying...\n"
                            )
                            page = self._get_page(capsule_page_url)
                            soup = BeautifulSoup(page.content, "html.parser")
                            listing = soup.find("a", attrs={"href": f"{href}"})
                            retries += 1

                        price_span = listing.find(
                            "span", attrs={"class": "normal_price"}
                        )
                        price_str = price_span.text.split()[2]
                        price = float(price_str.replace("$", ""))
                        price_total = round(
                            float(capsule_quantities[href_index] * price), 2
                        )

                        self.console.print(capsule_names_generic[href_index])
                        self.console.print(
                            f"${price} --> ${price_total} ({capsule_quantities[href_index]})"
                        )

                        self.total_price += price_total

                    except ValueError:
                        self.console.print("[bold red][!] Failed to find price listing")
                        break

    def _scrape_prices_case(
        self, case_quantities, case_page_urls, case_hrefs, case_names
    ):
        for index, case_quantity in enumerate(case_quantities):
            if case_quantity > 0:
                title_string = f"{PADDING}{case_names[index]}{PADDING}"[:MAX_LINE_LEN]
                self.console.print(f"[bold magenta]{title_string}")

                page = self._get_page(case_page_urls[index])
                soup = BeautifulSoup(page.content, "html.parser")

                listing = soup.find("a", attrs={"href": case_hrefs[index]})
                retries = 0
                while not listing and retries < 5:
                    self.console.print(
                        f"[bold red][!] Failed to load page ({page.status_code}). Retrying...\n"
                    )
                    page = self._get_page(case_page_urls[index])
                    soup = BeautifulSoup(page.content, "html.parser")
                    listing = soup.find("a", attrs={"href": case_hrefs[index]})
                    retries += 1

                else:
                    try:
                        price_class = listing.find(
                            "span", attrs={"class": "normal_price"}
                        )
                        price_str = price_class.text.split()[2]
                        price = float(price_str.replace("$", ""))
                        price_total = round(float(case_quantity * price), 2)

                        self.console.print(
                            f"${price} --> ${price_total} ({case_quantity})"
                        )

                        self.total_price += price_total

                    except ValueError:
                        self.console.print("[bold red][!] Failed to find price listing")

                    if not self.use_proxy:
                        time.sleep(1)
