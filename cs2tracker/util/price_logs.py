import csv
from datetime import datetime

from cs2tracker.constants import OUTPUT_FILE


class PriceLogs:
    @classmethod
    def _append_latest_calculation(cls, date, usd_total, eur_total):
        """Append the first price calculation of the day."""
        with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as price_logs:
            price_logs_writer = csv.writer(price_logs)
            price_logs_writer.writerow([date, f"{usd_total:.2f}$", f"{eur_total:.2f}€"])

    @classmethod
    def _replace_latest_calculation(cls, date, usd_total, eur_total):
        """Replace the last calculation of today with the most recent one of today."""
        with open(OUTPUT_FILE, "r+", newline="", encoding="utf-8") as price_logs:
            price_logs_reader = csv.reader(price_logs)
            rows = list(price_logs_reader)
            rows_without_today = rows[:-1]
            price_logs.seek(0)
            price_logs.truncate()

            price_logs_writer = csv.writer(price_logs)
            price_logs_writer.writerows(rows_without_today)
            price_logs_writer.writerow([date, f"{usd_total:.2f}$", f"{eur_total:.2f}€"])

    @classmethod
    def save(cls, usd_total, eur_total):
        """
        Save the current date and total prices in USD and EUR to a CSV file.

        This will append a new entry to the output file if no entry has been made for
        today.

        :param usd_total: The total price in USD to save.
        :param eur_total: The total price in EUR to save.
        :raises FileNotFoundError: If the output file does not exist.
        :raises IOError: If there is an error writing to the output file.
        """
        with open(OUTPUT_FILE, "r", encoding="utf-8") as price_logs:
            price_logs_reader = csv.reader(price_logs)
            rows = list(price_logs_reader)
            last_log_date, _, _ = rows[-1] if rows else ("", "", "")

        today = datetime.now().strftime("%Y-%m-%d")
        if last_log_date != today:
            cls._append_latest_calculation(today, usd_total, eur_total)
        else:
            cls._replace_latest_calculation(today, usd_total, eur_total)

    @classmethod
    def read(cls):
        """
        Parse the output file to extract dates, dollar prices, and euro prices. This
        data is used for drawing the plot of past prices.

        :return: A tuple containing three lists: dates, dollar prices, and euro prices.
        :raises FileNotFoundError: If the output file does not exist.
        :raises IOError: If there is an error reading the output file.
        """
        dates, usd_prices, eur_prices = [], [], []
        with open(OUTPUT_FILE, "r", encoding="utf-8") as price_logs:
            price_logs_reader = csv.reader(price_logs)
            for row in price_logs_reader:
                date, price_usd, price_eur = row
                date = datetime.strptime(date, "%Y-%m-%d")
                price_usd = float(price_usd.rstrip("$"))
                price_eur = float(price_eur.rstrip("€"))

                dates.append(date)
                usd_prices.append(price_usd)
                eur_prices.append(price_eur)

        return dates, usd_prices, eur_prices

    @classmethod
    def validate_file(cls, log_file_path):
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
                    date_str, price_usd, price_eur = row
                    datetime.strptime(date_str, "%Y-%m-%d")
                    float(price_usd.rstrip("$"))
                    float(price_eur.rstrip("€"))
        except (FileNotFoundError, IOError, ValueError, TypeError):
            return False
        except Exception:
            return False

        return True
