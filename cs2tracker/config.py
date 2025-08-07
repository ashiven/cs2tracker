import json
import re
from configparser import ConfigParser, ParsingError
from urllib.parse import quote, unquote

from cs2tracker.constants import (
    CONFIG_FILE,
    INVENTORY_IMPORT_FILE,
)
from cs2tracker.util.padded_console import get_console

STEAM_MARKET_LISTING_BASEURL_CS2 = "https://steamcommunity.com/market/listings/730/"
STEAM_MARKET_LISTING_REGEX = r"^https://steamcommunity.com/market/listings/\d+/.+$"

CUSTOM_SECTIONS = [
    "Skins",
    "Special Items",
    "Agents",
    "Charms",
    "Patches",
    "Patch Packs",
    "Stickers",
    "Souvenirs",
    "Others",
]

PREEXISTING_SECTIONS = [
    "Cases",
    "Katowice 2014 Sticker Capsule",
    "Cologne 2014 Sticker Capsule",
    "DreamHack 2014 Sticker Capsule",
    "Katowice 2015 Sticker Capsule",
    "Cologne 2015 Sticker Capsule",
    "Cluj-Napoca 2015 Sticker Capsule",
    "Columbus 2016 Sticker Capsule",
    "Cologne 2016 Sticker Capsule",
    "Atlanta 2017 Sticker Capsule",
    "Krakow 2017 Sticker Capsule",
    "Boston 2018 Sticker Capsule",
    "London 2018 Sticker Capsule",
    "Katowice 2019 Sticker Capsule",
    "Berlin 2019 Sticker Capsule",
    "2020 RMR Sticker Capsule",
    "Stockholm 2021 Sticker Capsule",
    "Antwerp 2022 Sticker Capsule",
    "Rio 2022 Sticker Capsule",
    "Paris 2023 Sticker Capsule",
    "Copenhagen 2024 Sticker Capsule",
    "Shanghai 2024 Sticker Capsule",
    "Austin 2025 Sticker Capsule",
]

console = get_console()


class ValidatedConfig(ConfigParser):
    def __init__(self):
        """Initialize the ValidatedConfig class."""
        super().__init__(delimiters=("~"), interpolation=None)
        self.optionxform = str  # type: ignore

        self.valid = False
        self.last_error = None
        try:
            self.load_from_file()
        except (FileNotFoundError, ParsingError) as error:
            console.error(f"Config error: {error}")
            self.last_error = error

    def delete_display_sections(self):
        """
        Delete all sections that are displayed to the user from the config.

        (This excludes the internal App Settings section)
        """
        use_proxy = self.getboolean("App Settings", "use_proxy", fallback=False)
        discord_notifications = self.getboolean(
            "App Settings", "discord_notifications", fallback=False
        )
        conversion_currency = self.get("App Settings", "conversion_currency", fallback="EUR")

        self.clear()
        self.add_section("App Settings")
        self.set("App Settings", "use_proxy", str(use_proxy))
        self.set("App Settings", "discord_notifications", str(discord_notifications))
        self.set("App Settings", "conversion_currency", conversion_currency)

    def _validate_config_sections(self):
        """Validate that the configuration file has all required sections."""
        for section in CUSTOM_SECTIONS:
            if not self.has_section(section):
                raise ValueError(f"Missing '{section}' section in the configuration file.")
        for section in PREEXISTING_SECTIONS:
            if not self.has_section(section):
                raise ValueError(f"Missing '{section}' section in the configuration file.")

    def _validate_config_values(self):
        # pylint: disable=too-many-branches
        """Validate that the configuration file has valid values for all sections."""
        try:
            for section in self.sections():
                if section == "App Settings":
                    for option in ("use_proxy", "discord_notifications", "conversion_currency"):
                        if not self.has_option(section, option):
                            raise ValueError(f"Reason: Missing '{option}' in '{section}' section.")
                        if option in ("use_proxy", "discord_notifications") and self.get(
                            section, option, fallback=False
                        ) not in ("True", "False"):
                            raise ValueError(
                                f"Reason: Invalid value for '{option}' in '{section}' section."
                            )
                elif section == "User Settings":
                    for option in ("proxy_api_key", "discord_webhook_url"):
                        if not self.has_option(section, option):
                            raise ValueError(f"Reason: Missing '{option}' in '{section}' section.")
                else:
                    for item_href, item_owned in self.items(section):
                        if not re.match(STEAM_MARKET_LISTING_REGEX, item_href):
                            raise ValueError("Reason: Invalid Steam market listing URL.")
                        if int(item_owned) < 0:
                            raise ValueError("Reason: Negative values are not allowed.")
                        if int(item_owned) > 1000000:
                            raise ValueError("Reason: Value exceeds maximum limit of 1,000,000.")
        except ValueError as error:
            # Re-raise the error if it contains "Reason: " to maintain the original message
            # and raise a ValueError if the conversion of a value to an integer fails.
            if "Reason: " in str(error):
                raise
            raise ValueError("Reason: Invalid value type. All values must be integers.") from error

    def _validate_config(self):
        """
        Validate the configuration file to ensure all required sections exist with the
        right values.

        :raises ValueError: If any required section is missing or if any value is
            invalid.
        """
        try:
            self._validate_config_sections()
            self._validate_config_values()
            self.valid = True
        except ValueError as error:
            console.error(f"Config error: {error}")
            self.valid = False
            self.last_error = error

    def load_from_file(self):
        """Load the configuration file and validate it."""
        self.clear()
        self.read(CONFIG_FILE)
        self._validate_config()

    def write_to_file(self):
        """Validate the current configuration and write it to the configuration file if
        it is valid.
        """
        self._validate_config()

        if self.valid:
            with open(CONFIG_FILE, "w", encoding="utf-8") as config_file:
                self.write(config_file)

    def read_from_inventory_file(self):
        """
        Read an inventory file into the configuration.

        This file is generated after a user automatically imports their inventory.
        """
        try:
            with open(INVENTORY_IMPORT_FILE, "r", encoding="utf-8") as inventory_file:
                inventory_data = json.load(inventory_file)

                added_to_config = set()
                for _, item_infos in inventory_data.items():
                    for item_name, item_owned in item_infos.items():
                        option = self.name_to_option(item_name, href=True)
                        for section in self.sections():
                            if option in self.options(section):
                                self.set(section, option, str(item_owned))
                                added_to_config.add(item_name)

                for section, item_infos in inventory_data.items():
                    sorted_item_infos = dict(sorted(item_infos.items()))
                    for item_name, item_owned in sorted_item_infos.items():
                        if item_name not in added_to_config:
                            option = self.name_to_option(item_name, href=True)
                            self.set(section, option, str(item_owned))

            self.write_to_file()
        except (FileNotFoundError, json.JSONDecodeError) as error:
            console.error(f"Error reading inventory file: {error}")
            self.last_error = error
            self.valid = False

    def option_to_name(self, option, href=False):
        """
        Convert an internal option representation to a reader-friendly name.

        :param option: The internal option representation to convert.
        :param custom: If True, the option is for a custom item.
        :return: The reader-friendly name.
        """
        if href:
            if not re.match(STEAM_MARKET_LISTING_REGEX, option):
                raise ValueError(f"Invalid Steam market listing URL: {option}")

            converted_option = unquote(option.split("/")[-1])
        else:
            converted_option = option.replace("_", " ").title()

        return converted_option

    def name_to_option(self, name, href=False):
        """
        Convert a reader-friendly name to an internal option representation.

        :param name: The reader-friendly name to convert.
        :param custom: If True, the name is for a custom item.
        :return: The internal option representation.
        """
        if href:
            converted_name = STEAM_MARKET_LISTING_BASEURL_CS2 + quote(name)
        else:
            converted_name = name.replace(" ", "_").lower()

        return converted_name

    def toggle_app_option(self, option, enabled):
        """
        Toggle the use of proxies for requests. This will update the configuration file.

        :param enabled: If True, proxies will be used; if False, they will not be used.
        """
        self.set("App Settings", option, str(enabled))
        self.write_to_file()

        console.info(f"{'Enabled' if enabled else 'Disabled'} option: {option}.")

    def set_app_option(self, option, value):
        """
        Set an option in the App Settings to a specific value.

        :param option: The option to set.
        :param value: The value to set the option to.
        """
        self.set("App Settings", option, str(value))
        self.write_to_file()

        console.info(f"Set {option} to {value}.")

    def option_exists(self, option, exclude_sections=()):
        """
        Check if an option exists in any section of the configuration.

        :param option: The option to check.
        :param exclude_sections: Sections to exclude from the check.
        :return: True if the option exists, False otherwise.
        """
        for section in [section for section in self.sections() if section not in exclude_sections]:
            if option in self.options(section):
                return True
        return False

    @property
    def use_proxy(self):
        """Check if the application should use proxies for requests."""
        return self.getboolean("App Settings", "use_proxy", fallback=False)

    @property
    def discord_notifications(self):
        """Check if the application should send Discord notifications."""
        return self.getboolean("App Settings", "discord_notifications", fallback=False)

    @property
    def conversion_currency(self):
        """Get the conversion currency for price calculations."""
        return self.get("App Settings", "conversion_currency", fallback="EUR")

    @property
    def proxy_api_key(self):
        """Get the API key for the proxy service."""
        return self.get("User Settings", "proxy_api_key", fallback="")

    @property
    def discord_webhook_url(self):
        """Get the Discord webhook URL for notifications."""
        return self.get("User Settings", "discord_webhook_url", fallback="")


config = ValidatedConfig()


def get_config():
    """Accessor function to retrieve the current configuration."""
    return config
