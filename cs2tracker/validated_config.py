import re
from configparser import ConfigParser

from cs2tracker.constants import CAPSULE_INFO, CONFIG_FILE
from cs2tracker.padded_console import PaddedConsole

console = PaddedConsole()


STEAM_MARKET_LISTING_REGEX = r"^https://steamcommunity.com/market/listings/\d+/.+$"


class ValidatedConfig(ConfigParser):
    def __init__(self):
        """Initialize the ValidatedConfig class."""
        super().__init__(delimiters=("~"), interpolation=None)
        self.optionxform = str  # type: ignore
        super().read(CONFIG_FILE)

        self.valid = False
        self.last_error = None
        self._validate_config()

    def _validate_config_sections(self):
        """Validate that the configuration file has all required sections."""
        if not self.has_section("User Settings"):
            raise ValueError("Missing 'User Settings' section in the configuration file.")
        if not self.has_section("App Settings"):
            raise ValueError("Missing 'App Settings' section in the configuration file.")
        if not self.has_section("Custom Items"):
            raise ValueError("Missing 'Custom Items' section in the configuration file.")
        if not self.has_section("Cases"):
            raise ValueError("Missing 'Cases' section in the configuration file.")
        for capsule_section in CAPSULE_INFO:
            if not self.has_section(capsule_section):
                raise ValueError(f"Missing '{capsule_section}' section in the configuration file.")

    def _validate_config_values(self):
        """Validate that the configuration file has valid values for all sections."""
        try:
            for custom_item_href, custom_item_owned in self.items("Custom Items"):
                if not re.match(STEAM_MARKET_LISTING_REGEX, custom_item_href):
                    raise ValueError(
                        f"Invalid Steam market listing URL in 'Custom Items' section: {custom_item_href}"
                    )

                if int(custom_item_owned) < 0:
                    raise ValueError(
                        f"Invalid value in 'Custom Items' section: {custom_item_href} = {custom_item_owned}"
                    )
            for case_name, case_owned in self.items("Cases"):
                if int(case_owned) < 0:
                    raise ValueError(
                        f"Invalid value in 'Cases' section: {case_name} = {case_owned}"
                    )
            for capsule_section in CAPSULE_INFO:
                for capsule_name, capsule_owned in self.items(capsule_section):
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
        try:
            self._validate_config_sections()
            self._validate_config_values()
            self.valid = True
        except ValueError as error:
            console.print(f"[bold red][!] Config error: {error}")
            self.valid = False
            self.last_error = error

    def write_to_file(self):
        """Write the current configuration to the configuration file."""
        self._validate_config()

        if self.valid:
            with open(CONFIG_FILE, "w", encoding="utf-8") as config_file:
                self.write(config_file)

    def toggle_use_proxy(self, enabled: bool):
        """
        Toggle the use of proxies for requests. This will update the configuration file.

        :param enabled: If True, proxies will be used; if False, they will not be used.
        """
        self.set("App Settings", "use_proxy", str(enabled))
        self.write_to_file()

        console.print(
            f"[bold green]{'[+] Enabled' if enabled else '[-] Disabled'} proxy usage for requests."
        )

    def toggle_discord_webhook(self, enabled: bool):
        """
        Toggle the use of a Discord webhook to notify users of price calculations.

        :param enabled: If True, the webhook will be used; if False, it will not be
            used.
        """
        self.set("App Settings", "discord_notifications", str(enabled))
        self.write_to_file()

        console.print(
            f"[bold green]{'[+] Enabled' if enabled else '[-] Disabled'} Discord webhook notifications."
        )
