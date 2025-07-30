import requests
from requests.exceptions import RequestException

from cs2tracker.util import PriceLogs, get_console

DC_WEBHOOK_USERNAME = "CS2Tracker"
DC_WEBHOOK_AVATAR_URL = "https://img.icons8.com/?size=100&id=uWQJp2tLXUH6&format=png&color=000000"
DC_RECENT_HISTORY_LIMIT = 5

console = get_console()


class DiscordNotifier:
    @classmethod
    def _construct_recent_calculations_embeds(cls):
        """
        Construct the embeds for the Discord message that will be sent after a price
        calculation has been made.

        :return: A list of embeds for the Discord message.
        """
        dates, usd_prices, eur_prices = PriceLogs.read()
        dates, usd_prices, eur_prices = reversed(dates), reversed(usd_prices), reversed(eur_prices)

        date_history, usd_history, eur_history = [], [], []
        for date, usd_log, eur_log in zip(dates, usd_prices, eur_prices):
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

    @classmethod
    def notify(cls, webhook_url):
        """
        Notify users via Discord about recent price calculations.

        :param webhook_url: The Discord webhook URL to send the notification to.
        """
        embeds = cls._construct_recent_calculations_embeds()
        try:
            response = requests.post(
                url=webhook_url,
                json={
                    "embeds": embeds,
                    "username": DC_WEBHOOK_USERNAME,
                    "avatar_url": DC_WEBHOOK_AVATAR_URL,
                },
                timeout=10,
            )
            response.raise_for_status()
            console.print("[bold steel_blue3][+] Discord notification sent.\n")
        except RequestException as error:
            console.error(f"Failed to send Discord notification: {error}\n")
        except Exception as error:
            console.error(f"An unexpected error occurred: {error}\n")
