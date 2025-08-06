import requests
from requests.exceptions import RequestException

from cs2tracker.config import get_config
from cs2tracker.logs import PriceLogs
from cs2tracker.util.padded_console import get_console

DC_WEBHOOK_USERNAME = "CS2Tracker"
DC_WEBHOOK_AVATAR_URL = "https://img.icons8.com/?size=100&id=uWQJp2tLXUH6&format=png&color=000000"
DC_RECENT_HISTORY_LIMIT = 5

console = get_console()
config = get_config()


class DiscordNotifier:
    @classmethod
    def _construct_recent_calculations_embeds(cls):
        """
        Construct the embeds for the Discord message that will be sent after a price
        calculation has been made.

        :return: A list of embeds for the Discord message.
        """
        dates, totals = PriceLogs.read(newest_first=True, with_symbols=True)

        date_field = [
            {
                "name": "Date",
                "value": "\n".join([date.strftime("%Y-%m-%d") for date in dates][:DC_RECENT_HISTORY_LIMIT]),  # type: ignore
                "inline": True,
            },
        ]
        price_fields = [
            {
                "name": f"{price_source.name.title()} (USD | {config.conversion_currency})",
                "value": "\n".join(
                    [
                        f"{usd_total} | {converted_total}"
                        for usd_total, converted_total in zip(
                            totals[price_source]["USD"][:DC_RECENT_HISTORY_LIMIT],
                            totals[price_source][config.conversion_currency][
                                :DC_RECENT_HISTORY_LIMIT
                            ],
                        )
                    ]
                ),
                "inline": True,
            }
            for price_source in totals
        ][
            :2
        ]  # Limit to the first two price sources because Discord can only display 3 fields per line (Date + 2 Price Sources)

        embeds = [
            {
                "title": "📊 Recent Investment History",
                "color": 5814783,
                "fields": date_field + price_fields,
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
