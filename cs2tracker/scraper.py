import csv
import os
import time
from configparser import ConfigParser
from datetime import datetime
from subprocess import DEVNULL, call

from bs4 import BeautifulSoup
from bs4.element import Tag
from currency_converter import CurrencyConverter
from requests import RequestException, Session
from requests.adapters import HTTPAdapter, Retry
from tenacity import RetryError, retry, stop_after_attempt

from cs2tracker.constants import (
    AUTHOR_STRING,
    BANNER,
    BATCH_FILE,
    CAPSULE_INFO,
    CASE_HREFS,
    CONFIG_FILE,
    OS,
    OUTPUT_FILE,
    PROJECT_DIR,
    PYTHON_EXECUTABLE,
    RUNNING_IN_EXE,
    OSType,
)
from cs2tracker.padded_console import PaddedConsole

MAX_LINE_LEN = 72
SEPARATOR = "-"
PRICE_INFO = "Owned: {:<10}  Steam market price: ${:<10}  Total: ${:<10}\n"

HTTP_PROXY_URL = "http://{}:@smartproxy.crawlbase.com:8012"
HTTPS_PROXY_URL = "http://{}:@smartproxy.crawlbase.com:8012"

DC_WEBHOOK_USERNAME = "CS2Tracker"
DC_WEBHOOK_AVATAR_URL = "https://img.icons8.com/?size=100&id=uWQJp2tLXUH6&format=png&color=000000"
DC_RECENT_HISTORY_LIMIT = 5

WIN_BACKGROUND_TASK_NAME = "CS2Tracker Daily Calculation"
WIN_BACKGROUND_TASK_SCHEDULE = "DAILY"
WIN_BACKGROUND_TASK_TIME = "12:00"
WIN_BACKGROUND_TASK_CMD = (
    f"powershell -WindowStyle Hidden -Command \"Start-Process '{BATCH_FILE}' -WindowStyle Hidden\""
)


class Scraper:
    def __init__(self):
        """Initialize the Scraper class."""
        self.console = PaddedConsole()
        self.parse_config()
        self._start_session()

        self.usd_total = 0
        self.eur_total = 0

    def _validate_config_sections(self):
        """Validate that the configuration file has all required sections."""
        if not self.config.has_section("User Settings"):
            raise ValueError("Missing 'User Settings' section in the configuration file.")
        if not self.config.has_section("App Settings"):
            raise ValueError("Missing 'App Settings' section in the configuration file.")
        if not self.config.has_section("Custom Items"):
            raise ValueError("Missing 'Custom Items' section in the configuration file.")
        if not self.config.has_section("Cases"):
            raise ValueError("Missing 'Cases' section in the configuration file.")
        for capsule_section in CAPSULE_INFO:
            if not self.config.has_section(capsule_section):
                raise ValueError(f"Missing '{capsule_section}' section in the configuration file.")

    def _validate_config_values(self):
        """Validate that the configuration file has valid values for all sections."""
        try:
            for custom_item_name, custom_item_owned in self.config.items("Custom Items"):
                if " " not in custom_item_owned:
                    raise ValueError(
                        f"Invalid custom item format (<item_name> = <owned_count> <item_url>): {custom_item_name} = {custom_item_owned}"
                    )
                owned, _ = custom_item_owned.split(" ", 1)
                if int(owned) < 0:
                    raise ValueError(
                        f"Invalid value in 'Custom Items' section: {custom_item_name} = {custom_item_owned}"
                    )
            for case_name, case_owned in self.config.items("Cases"):
                if int(case_owned) < 0:
                    raise ValueError(
                        f"Invalid value in 'Cases' section: {case_name} = {case_owned}"
                    )
            for capsule_section in CAPSULE_INFO:
                for capsule_name, capsule_owned in self.config.items(capsule_section):
                    if int(capsule_owned) < 0:
                        raise ValueError(
                            f"Invalid value in '{capsule_section}' section: {capsule_name} = {capsule_owned}"
                        )
        except ValueError as error:
            if "Invalid " in str(error):
                raise
            raise ValueError("Invalid value type. All values must be integers.") from error

    def _validate_config(self):
        """
        Validate the configuration file to ensure all required sections exist with the
        right values.

        :raises ValueError: If any required section is missing or if any value is
            invalid.
        """
        self._validate_config_sections()
        self._validate_config_values()

    def parse_config(self):
        """
        Parse the configuration file to read settings and user-owned items.

        Sets self.valid_config to True if the configuration is valid, and False if it is
        not.
        """
        self.config = ConfigParser(interpolation=None)
        self.config.read(CONFIG_FILE)
        try:
            self._validate_config()
            self.valid_config = True
        except ValueError as error:
            self.console.print(f"[bold red][!] Config error: {error}")
            self.valid_config = False

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
        if not self.valid_config:
            self.console.print(
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
        self._save_price_log()
        self._send_discord_notification()

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

        :raises FileNotFoundError: If the output file does not exist.
        :raises IOError: If there is an error writing to the output file.
        """
        with open(OUTPUT_FILE, "r", encoding="utf-8") as price_logs:
            price_logs_reader = csv.reader(price_logs)
            rows = list(price_logs_reader)
            last_log_date, _, _ = rows[-1] if rows else ("", "", "")

        today = datetime.now().strftime("%Y-%m-%d")
        if last_log_date != today:
            # Append first price calculation of the day
            with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as price_logs:
                price_logs_writer = csv.writer(price_logs)
                price_logs_writer.writerow(
                    [today, f"{self.usd_total:.2f}$", f"{self.eur_total:.2f}€"]
                )
        else:
            # Replace the last calculation of today with the most recent one of today
            with open(OUTPUT_FILE, "r+", newline="", encoding="utf-8") as price_logs:
                price_logs_reader = csv.reader(price_logs)
                rows = list(price_logs_reader)
                rows_without_today = rows[:-1]
                price_logs.seek(0)
                price_logs.truncate()

                price_logs_writer = csv.writer(price_logs)
                price_logs_writer.writerows(rows_without_today)
                price_logs_writer.writerow(
                    [today, f"{self.usd_total:.2f}$", f"{self.eur_total:.2f}€"]
                )

    def read_price_log(self):
        """
        Parse the output file to extract dates, dollar prices, and euro prices. This
        data is used for drawing the plot of past prices.

        :return: A tuple containing three lists: dates, dollar prices, and euro prices.
        :raises FileNotFoundError: If the output file does not exist.
        :raises IOError: If there is an error reading the output file.
        """
        dates, dollars, euros = [], [], []
        with open(OUTPUT_FILE, "r", encoding="utf-8") as price_logs:
            price_logs_reader = csv.reader(price_logs)
            for row in price_logs_reader:
                date, price_usd, price_eur = row
                date = datetime.strptime(date, "%Y-%m-%d")
                price_usd = float(price_usd.rstrip("$"))
                price_eur = float(price_eur.rstrip("€"))

                dates.append(date)
                dollars.append(price_usd)
                euros.append(price_eur)

        return dates, dollars, euros

    def _construct_recent_calculations_embeds(self):
        """
        Construct the embeds for the Discord message that will be sent after a price
        calculation has been made.

        :return: A list of embeds for the Discord message.
        """
        dates, usd_logs, eur_logs = self.read_price_log()
        dates, usd_logs, eur_logs = reversed(dates), reversed(usd_logs), reversed(eur_logs)

        date_history, usd_history, eur_history = [], [], []
        for date, usd_log, eur_log in zip(dates, usd_logs, eur_logs):
            if len(date_history) >= DC_RECENT_HISTORY_LIMIT:
                break
            date_history.append(date.strftime("%Y-%m-%d"))
            usd_history.append(f"${usd_log:.2f}")
            eur_history.append(f"€{eur_log:.2f}")

        date_history = "\n".join(date_history)
        usd_history = "\n".join(usd_history)
        eur_history = "\n".join(eur_history)

        embeds = [
            {
                "title": "📊 Recent Price History",
                "color": 5814783,
                "fields": [
                    {
                        "name": "Date",
                        "value": date_history,
                        "inline": True,
                    },
                    {
                        "name": "USD Total",
                        "value": usd_history,
                        "inline": True,
                    },
                    {
                        "name": "EUR Total",
                        "value": eur_history,
                        "inline": True,
                    },
                ],
            }
        ]

        return embeds

    def _send_discord_notification(self):
        """Send a message to a Discord webhook if notifications are enabled in the
        config file and a webhook URL is provided.
        """
        discord_notifications = self.config.getboolean(
            "App Settings", "discord_notifications", fallback=False
        )
        webhook_url = self.config.get("User Settings", "discord_webhook_url", fallback=None)
        webhook_url = None if webhook_url in ("None", "") else webhook_url

        if discord_notifications and webhook_url:
            embeds = self._construct_recent_calculations_embeds()
            try:
                response = self.session.post(
                    url=webhook_url,
                    json={
                        "embeds": embeds,
                        "username": DC_WEBHOOK_USERNAME,
                        "avatar_url": DC_WEBHOOK_AVATAR_URL,
                    },
                )
                response.raise_for_status()
                self.console.print("[bold steel_blue3][+] Discord notification sent.\n")
            except RequestException as error:
                self.console.print(f"[bold red][!] Failed to send Discord notification: {error}\n")
            except Exception as error:
                self.console.print(f"[bold red][!] An unexpected error occurred: {error}\n")

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
        api_key = self.config.get("User Settings", "api_key", fallback=None)
        api_key = None if api_key in ("None", "") else api_key

        if use_proxy and api_key:
            page = self.session.get(
                url=url,
                proxies={
                    "http": HTTP_PROXY_URL.format(api_key),
                    "https": HTTPS_PROXY_URL.format(api_key),
                },
                verify=False,
            )
        else:
            page = self.session.get(url)

        if not page.ok or not page.content:
            self.console.print(
                f"[bold red][!] Failed to load page ({page.status_code}). Retrying...\n"
            )
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
        self.console.print(f"[bold magenta]{capsule_title}\n")

        capsule_usd_total = 0
        try:
            capsule_page = self._get_page(capsule_info["page"])
            for capsule_name, capsule_href in zip(capsule_info["names"], capsule_info["items"]):
                config_capsule_name = capsule_name.replace(" ", "_")
                owned = self.config.getint(capsule_section, config_capsule_name, fallback=0)
                if owned == 0:
                    continue

                price_usd = self._parse_item_price(capsule_page, capsule_href)
                price_usd_owned = round(float(owned * price_usd), 2)

                self.console.print(f"[bold deep_sky_blue4]{capsule_name}")
                self.console.print(PRICE_INFO.format(owned, price_usd, price_usd_owned))
                capsule_usd_total += price_usd_owned
        except (RetryError, ValueError):
            self.console.print(
                "[bold red][!] Too many requests. (Consider using proxies to prevent rate limiting)\n"
            )
        except Exception as error:
            self.console.print(f"[bold red][!] An unexpected error occurred: {error}\n")

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
            self.console.print(f"[bold magenta]{case_title}\n")

            try:
                case_page_url = self._market_page_from_href(CASE_HREFS[case_index])
                case_page = self._get_page(case_page_url)
                price_usd = self._parse_item_price(case_page, CASE_HREFS[case_index])
                price_usd_owned = round(float(int(owned) * price_usd), 2)

                self.console.print(PRICE_INFO.format(owned, price_usd, price_usd_owned))
                case_usd_total += price_usd_owned

                if not self.config.getboolean("App Settings", "use_proxy", fallback=False):
                    time.sleep(1)
            except (RetryError, ValueError):
                self.console.print(
                    "[bold red][!] Too many requests. (Consider using proxies to prevent rate limiting)\n"
                )
            except Exception as error:
                self.console.print(f"[bold red][!] An unexpected error occurred: {error}\n")

        return case_usd_total

    def _scrape_custom_item_prices(self):
        """
        Scrape prices for custom items defined in the configuration.

        For each custom item, it prints the item name, owned count, price per item, and
        total price for owned items.
        """
        custom_item_usd_total = 0
        for config_custom_item_name, owned_and_href in self.config.items("Custom Items"):
            owned, custom_item_href = owned_and_href.split(" ", 1)
            if int(owned) == 0:
                continue

            custom_item_name = config_custom_item_name.replace("_", " ").title()
            custom_item_title = custom_item_name.center(MAX_LINE_LEN, SEPARATOR)
            self.console.print(f"[bold magenta]{custom_item_title}\n")

            try:
                custom_item_page_url = self._market_page_from_href(custom_item_href)
                custom_item_page = self._get_page(custom_item_page_url)
                price_usd = self._parse_item_price(custom_item_page, custom_item_href)
                price_usd_owned = round(float(int(owned) * price_usd), 2)

                self.console.print(PRICE_INFO.format(owned, price_usd, price_usd_owned))
                custom_item_usd_total += price_usd_owned

                if not self.config.getboolean("App Settings", "use_proxy", fallback=False):
                    time.sleep(1)
            except (RetryError, ValueError):
                self.console.print(
                    "[bold red][!] Too many requests. (Consider using proxies to prevent rate limiting)\n"
                )
            except Exception as error:
                self.console.print(f"[bold red][!] An unexpected error occurred: {error}\n")

        return custom_item_usd_total

    def identify_background_task(self):
        """
        Search the OS for a daily background task that runs the scraper.

        :return: True if a background task is found, False otherwise.
        """
        if OS == OSType.WINDOWS:
            cmd = ["schtasks", "/query", "/tn", WIN_BACKGROUND_TASK_NAME]
            return_code = call(cmd, stdout=DEVNULL, stderr=DEVNULL)
            found = return_code == 0
            return found
        else:
            # TODO: implement finder for cron jobs
            return False

    def _toggle_task_batch_file(self, enabled: bool):
        """
        Create or delete a batch file that runs the scraper.

        :param enabled: If True, the batch file will be created; if False, the batch
            file will be deleted.
        """
        if enabled:
            with open(BATCH_FILE, "w", encoding="utf-8") as batch_file:
                if RUNNING_IN_EXE:
                    # The python executable is set to the executable itself
                    # for executables created with PyInstaller
                    batch_file.write(f"{PYTHON_EXECUTABLE} --only-scrape\n")
                else:
                    batch_file.write(f"cd {PROJECT_DIR}\n")
                    batch_file.write(f"{PYTHON_EXECUTABLE} -m cs2tracker --only-scrape\n")
        else:
            if os.path.exists(BATCH_FILE):
                os.remove(BATCH_FILE)

    def _toggle_background_task_windows(self, enabled: bool):
        """
        Create or delete a daily background task that runs the scraper on Windows.

        :param enabled: If True, the task will be created; if False, the task will be
            deleted.
        """
        self._toggle_task_batch_file(enabled)
        if enabled:
            cmd = [
                "schtasks",
                "/create",
                "/tn",
                WIN_BACKGROUND_TASK_NAME,
                "/tr",
                WIN_BACKGROUND_TASK_CMD,
                "/sc",
                WIN_BACKGROUND_TASK_SCHEDULE,
                "/st",
                WIN_BACKGROUND_TASK_TIME,
            ]
            return_code = call(cmd, stdout=DEVNULL, stderr=DEVNULL)
            if return_code == 0:
                self.console.print("[bold green][+] Background task enabled.")
            else:
                self.console.print("[bold red][!] Failed to enable background task.")
        else:
            cmd = ["schtasks", "/delete", "/tn", WIN_BACKGROUND_TASK_NAME, "/f"]
            return_code = call(cmd, stdout=DEVNULL, stderr=DEVNULL)
            if return_code == 0:
                self.console.print("[bold green][-] Background task disabled.")
            else:
                self.console.print("[bold red][!] Failed to disable background task.")

    def toggle_background_task(self, enabled: bool):
        """
        Create or delete a daily background task that runs the scraper.

        :param enabled: If True, the task will be created; if False, the task will be
            deleted.
        """
        if OS == OSType.WINDOWS:
            self._toggle_background_task_windows(enabled)
        else:
            # TODO: implement toggle for cron jobs
            pass

    def toggle_use_proxy(self, enabled: bool):
        """
        Toggle the use of proxies for requests. This will update the configuration file.

        :param enabled: If True, proxies will be used; if False, they will not be used.
        """
        self.config.set("App Settings", "use_proxy", str(enabled))
        with open(CONFIG_FILE, "w", encoding="utf-8") as config_file:
            self.config.write(config_file)

        self.console.print(
            f"[bold green]{'[+] Enabled' if enabled else '[-] Disabled'} proxy usage for requests."
        )

    def toggle_discord_webhook(self, enabled: bool):
        """
        Toggle the use of a Discord webhook to notify users of price calculations.

        :param enabled: If True, the webhook will be used; if False, it will not be
            used.
        """
        self.config.set("App Settings", "discord_notifications", str(enabled))
        with open(CONFIG_FILE, "w", encoding="utf-8") as config_file:
            self.config.write(config_file)

        self.console.print(
            f"[bold green]{'[+] Enabled' if enabled else '[-] Disabled'} Discord webhook notifications."
        )


if __name__ == "__main__":
    scraper = Scraper()
    scraper.console.print(f"[bold yellow]{BANNER}\n{AUTHOR_STRING}\n")
    scraper.scrape_prices()
