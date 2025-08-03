from abc import ABC, abstractmethod
from enum import Enum
from urllib.parse import unquote

from bs4 import BeautifulSoup
from bs4.element import Tag

from cs2tracker.constants import CAPSULE_PAGES
from cs2tracker.util import get_console
from cs2tracker.util.validated_config import get_config

config = get_config()
console = get_console()


class PriceSource(Enum):
    STEAM = "steam"
    BUFF163 = "buff163"
    SKINPORT = "skinport"


class Parser(ABC):
    @classmethod
    @abstractmethod
    def get_item_page_url(cls, item_href, source=PriceSource.STEAM) -> str:
        """
        Convert an href of a Steam Community Market item to a Parser-specific market
        page URL.

        :param item_href: The href of the item listing, typically ending with the item's
            name.
        :return: A URL string for the Parser market page of the item.
        """

    @classmethod
    @abstractmethod
    def parse_item_price(cls, item_page, item_href, source=PriceSource.STEAM) -> float:
        """
        Parse the price of an item from the given Parser market page and steamcommunity
        item href.

        :param item_page: The HTTP response object containing the item page content.
        :param item_href: The href of the item listing to find the price for.
        :return: The price of the item as a float.
        :raises ValueError: If the item listing or price span cannot be found.
        """


class SteamParser(Parser):
    STEAM_MARKET_SEARCH_PAGE_BASE_URL = "https://steamcommunity.com/market/search?q={}"
    PRICE_INFO = "Owned: {:<10}  {} price: ${:<10}  Total: ${:<10}"
    NEEDS_TIMEOUT = True
    SOURCES = [PriceSource.STEAM]

    @classmethod
    def get_item_page_url(cls, item_href, source=PriceSource.STEAM):
        _ = source

        # For higher efficiency we want to reuse the same page for sticker capsules (scraper uses caching)
        # Therefore, if the provided item is a sticker capsule we return a search page defined in CAPSULE_PAGES
        # where all of the sticker capsules of one section are listed
        for section in config.sections():
            if section in ("Custom Items", "Cases", "User Settings", "App Settings"):
                continue
            if any(item_href == option for option in config.options(section)):
                return CAPSULE_PAGES[section]

        url_encoded_name = item_href.split("/")[-1]
        page_url = cls.STEAM_MARKET_SEARCH_PAGE_BASE_URL.format(url_encoded_name)

        return page_url

    @classmethod
    def parse_item_price(cls, item_page, item_href, source=PriceSource.STEAM):
        _ = source

        item_soup = BeautifulSoup(item_page.content, "html.parser")
        item_listing = item_soup.find("a", attrs={"href": f"{item_href}"})
        if not isinstance(item_listing, Tag):
            raise ValueError(f"Steam: Failed to find item listing for: {item_href}")

        item_price_span = item_listing.find("span", attrs={"class": "normal_price"})
        if not isinstance(item_price_span, Tag):
            raise ValueError(f"Steam: Failed to find price span in item listing for: {item_href}")

        price_str = item_price_span.text.split()[2]
        price = float(price_str.replace("$", ""))

        return price


class SkinLedgerParser(Parser):
    SKINLEDGER_PRICE_LIST = ""
    PRICE_INFO = "Owned: {:<10}  {} price: ${:<10}  Total: ${:<10}"
    NEEDS_TIMEOUT = False
    SOURCES = [PriceSource.STEAM, PriceSource.BUFF163, PriceSource.SKINPORT]

    @classmethod
    def get_item_page_url(cls, item_href, source=PriceSource.STEAM) -> str:
        _ = source
        return super().get_item_page_url(item_href)

    @classmethod
    def parse_item_price(cls, item_page, item_href, source=PriceSource.STEAM) -> float:
        _, _ = item_href, source
        return super().parse_item_price(item_page, item_href)


class ClashParser(Parser):
    CLASH_ITEM_API_BASE_URL = "https://inventory.clash.gg/api/GetItemPrice?id={}"
    PRICE_INFO = "Owned: {:<10}  {} price: ${:<10}  Total: ${:<10}"
    NEEDS_TIMEOUT = True
    SOURCES = [PriceSource.STEAM]

    @classmethod
    def get_item_page_url(cls, item_href, source=PriceSource.STEAM):
        _ = source

        url_encoded_name = item_href.split("/")[-1]
        page_url = cls.CLASH_ITEM_API_BASE_URL.format(url_encoded_name)

        return page_url

    @classmethod
    def parse_item_price(cls, item_page, item_href, source=PriceSource.STEAM):
        _, _ = item_href, source

        data = item_page.json()
        if data.get("success", "false") == "false":
            raise ValueError(f"Clash: Response failed for: {item_href}")

        price = data.get("average_price", None)
        if not price:
            raise ValueError(f"Clash: Failed to find item price for: {item_href}")

        price = float(price)

        return price


class CSGOTrader(Parser):
    CSGOTRADER_PRICE_LIST = "https://prices.csgotrader.app/latest/{}.json"
    PRICE_INFO = "Owned: {:<10}  {:<10}: ${:<10}  Total: ${:<10}"
    NEEDS_TIMEOUT = False
    SOURCES = [PriceSource.STEAM, PriceSource.BUFF163, PriceSource.SKINPORT]

    @classmethod
    def get_item_page_url(cls, item_href, source=PriceSource.STEAM):
        _ = item_href

        page_url = cls.CSGOTRADER_PRICE_LIST.format(source.value)

        return page_url

    @classmethod
    def parse_item_price(cls, item_page, item_href, source=PriceSource.STEAM):
        _ = source

        price_list = item_page.json()

        url_decoded_name = unquote(item_href.split("/")[-1])
        if source in (PriceSource.BUFF163, PriceSource.SKINPORT):
            url_decoded_name = url_decoded_name.replace("Holo-Foil", "Holo/Foil")

        price_info = price_list.get(url_decoded_name, None)
        if not price_info:
            raise ValueError(f"CSGOTrader: Could not find item price info: {url_decoded_name}")

        if source == PriceSource.STEAM:
            price = price_info.get("last_24h")
            if not price:
                price = price_info.get("last_7d")
                if not price:
                    raise ValueError(
                        f"CSGOTrader: Could not find steam price of the past 7 days: {url_decoded_name}"
                    )
        elif source == PriceSource.BUFF163:
            price = price_info.get("starting_at")
            if not price:
                raise ValueError(f"CSGOTrader: Could not find buff163 listing: {url_decoded_name}")
            price = price.get("price")
            if not price:
                raise ValueError(
                    f"CSGOTrader: Could not find recent buff163 price: {url_decoded_name}"
                )
        else:
            price = price_info.get("starting_at")
            if not price:
                raise ValueError(f"CSGOTrader: Could not find skinport listing: {url_decoded_name}")

        price = float(price)
        return price
