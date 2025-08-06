import csv
from datetime import datetime

from cs2tracker.config import get_config
from cs2tracker.constants import OUTPUT_FILE
from cs2tracker.scraper.parser import Parser
from cs2tracker.util.currency_conversion import convert, to_symbol

config = get_config()


class PriceLogs:
    @classmethod
    def _append_latest_calculation(cls, date, usd_totals):
        """Append the first price calculation of the day."""
        with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as price_logs:
            price_logs_writer = csv.writer(price_logs)
            price_entries_today = [f"{usd_total:.2f}$" for usd_total in usd_totals]
            price_logs_writer.writerow([date] + price_entries_today)

    @classmethod
    def _replace_latest_calculation(cls, date, usd_totals):
        """Replace the last calculation of today with the most recent one of today."""
        with open(OUTPUT_FILE, "r+", newline="", encoding="utf-8") as price_logs:
            price_logs_reader = csv.reader(price_logs)
            rows = list(price_logs_reader)
            rows_without_today = rows[:-1]
            price_logs.seek(0)
            price_logs.truncate()

            price_logs_writer = csv.writer(price_logs)
            price_logs_writer.writerows(rows_without_today)
            price_entries_today = [f"{usd_total:.2f}$" for usd_total in usd_totals]
            price_logs_writer.writerow([date] + price_entries_today)

    @classmethod
    def save(cls, usd_totals):
        """
        Save the current date and total prices in USD to a CSV file.

        This will append a new entry to the output file if no entry has been made for
        today.

        :param usd_totals: The total prices in USD to save.
        :raises FileNotFoundError: If the output file does not exist.
        :raises IOError: If there is an error writing to the output file.
        """
        with open(OUTPUT_FILE, "r", encoding="utf-8") as price_logs:
            price_logs_reader = csv.reader(price_logs)
            rows = list(price_logs_reader)
            last_log_date = rows[-1][0] if rows else ""

        today = datetime.now().strftime("%Y-%m-%d")
        if last_log_date != today:
            cls._append_latest_calculation(today, usd_totals)
        else:
            cls._replace_latest_calculation(today, usd_totals)

    @classmethod
    def read(cls, newest_first=False, with_symbols=False):
        """
        Parse the output file to extract dates, dollar prices, and the converted
        currency prices. This data is used for drawing the plot of past prices.

        :param newest_first: If True, the dates and totals will be returned in reverse
            order
        :param with_symbols: If True, the prices will be formatted with currency symbols
        :return: A tuple containing dates and a dictionary of totals for each price
            source.
        :raises FileNotFoundError: If the output file does not exist.
        :raises IOError: If there is an error reading the output file.
        """
        conversion_currency = config.conversion_currency
        dates = []
        totals = {
            price_source: {"USD": [], conversion_currency: []} for price_source in Parser.SOURCES
        }

        with open(OUTPUT_FILE, "r", encoding="utf-8") as price_logs:
            price_logs_reader = csv.reader(price_logs)
            for row in price_logs_reader:
                date, *usd_totals = row
                date = datetime.strptime(date, "%Y-%m-%d")

                usd_totals = [float(price_usd.rstrip("$")) for price_usd in usd_totals]
                converted_totals = [
                    convert(price_usd, "USD", conversion_currency) for price_usd in usd_totals
                ]

                dates.append(date)
                for price_source_index, price_source in enumerate(Parser.SOURCES):
                    totals[price_source]["USD"].append(usd_totals[price_source_index])
                    totals[price_source][conversion_currency].append(
                        converted_totals[price_source_index]
                    )

        if newest_first:
            dates.reverse()
            for price_source in Parser.SOURCES:
                totals[price_source]["USD"].reverse()
                totals[price_source][conversion_currency].reverse()

        if with_symbols:
            for price_source in Parser.SOURCES:
                totals[price_source]["USD"] = [
                    f"${price:.2f}" for price in totals[price_source]["USD"]
                ]
                totals[price_source][conversion_currency] = [
                    f"{to_symbol(conversion_currency)}{price:.2f}"
                    for price in totals[price_source][conversion_currency]
                ]

        return dates, totals

    @classmethod
    def validate_file(cls, log_file_path):
        # pylint: disable=expression-not-assigned
        """
        Ensures that the provided price log file has the right format. This should be
        used before importing a price log file to ensure it is valid.

        :param log_file_path: The path to the price log file to validate.
        :return: True if the price log file is valid, False otherwise.
        """
        try:
            with open(log_file_path, "r", encoding="utf-8") as price_logs:
                price_logs_reader = csv.reader(price_logs)
                for row in price_logs_reader:
                    date_str, *usd_totals = row
                    datetime.strptime(date_str, "%Y-%m-%d")
                    [float(price_usd.rstrip("$")) for price_usd in usd_totals]
        except (FileNotFoundError, IOError, ValueError, TypeError):
            return False
        except Exception:
            return False

        return True

    @classmethod
    def empty(cls):
        """Checks if the price history is empty and returns True if it is."""
        with open(OUTPUT_FILE, "r", encoding="utf-8") as price_logs:
            return len(list(price_logs)) == 0
