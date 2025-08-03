from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
from bs4.element import Tag

from cs2tracker.util import get_console

console = get_console()


class Parser(ABC):
    @classmethod
    @abstractmethod
    def get_item_page_url(cls, item_href) -> str:
        """
        Convert an href of a Steam Community Market item to a Parser-specific market
        page URL.

        :param item_href: The href of the item listing, typically ending with the item's
            name.
        :return: A URL string for the Parser market page of the item.
        """
        pass

    @classmethod
    @abstractmethod
    def parse_item_price(cls, item_page, item_href) -> float:
        """
        Parse the price of an item from the given Parser market page and steamcommunity
        item href.

        :param item_page: The HTTP response object containing the item page content.
        :param item_href: The href of the item listing to find the price for.
        :return: The price of the item as a float.
        :raises ValueError: If the item listing or price span cannot be found.
        """
        pass


class SteamParser(Parser):
    STEAM_MARKET_SEARCH_PAGE_BASE_URL = "https://steamcommunity.com/market/search?q={}"
    PRICE_INFO = "Owned: {:<10}  Steam market price: ${:<10}  Total: ${:<10}\n"

    @classmethod
    def get_item_page_url(cls, item_href):
        # For higher efficiency we want to reuse the same page for sticker capsules (scraper uses caching)
        # Therefore if the provided item is a sticker capsule we return a search page defined in CAPSULE_PAGE
        # where all of the sticker capsules of one section are listed

        url_encoded_name = item_href.split("/")[-1]
        page_url = cls.STEAM_MARKET_SEARCH_PAGE_BASE_URL.format(url_encoded_name)

        return page_url

    @classmethod
    def parse_item_price(cls, item_page, item_href):
        item_soup = BeautifulSoup(item_page.content, "html.parser")
        item_listing = item_soup.find("a", attrs={"href": f"{item_href}"})
        if not isinstance(item_listing, Tag):
            raise ValueError(f"Steam: Failed to find item listing: {item_page}")

        item_price_span = item_listing.find("span", attrs={"class": "normal_price"})
        if not isinstance(item_price_span, Tag):
            raise ValueError(f"Steam: Failed to find price span in item listing: {item_page}")

        price_str = item_price_span.text.split()[2]
        price = float(price_str.replace("$", ""))

        return price


class SkinLedgerParser(Parser):
    SKINLEDGER_PRICE_LIST = ""
    PRICE_INFO = "Owned: {:<10}  Clash price: ${:<10}  Total: ${:<10}\n"

    @classmethod
    def get_item_page_url(cls, item_href) -> str:
        return super().get_item_page_url(item_href)

    @classmethod
    def parse_item_price(cls, item_page, item_href) -> float:
        return super().parse_item_price(item_page, item_href)


class ClashParser(Parser):
    CLASH_ITEM_API_BASE_URL = "https://inventory.clash.gg/api/GetItemPrice?id={}"
    PRICE_INFO = "Owned: {:<10}  Clash price: ${:<10}  Total: ${:<10}\n"

    @classmethod
    def get_item_page_url(cls, item_href):
        url_encoded_name = item_href.split("/")[-1]
        page_url = cls.CLASH_ITEM_API_BASE_URL.format(url_encoded_name)

        return page_url

    @classmethod
    def parse_item_price(cls, item_page, item_href):
        # Using an unused variable so the linter doesn't complain
        _ = item_href

        data = item_page.json()
        if data.get("success", "false") == "false":
            raise ValueError(f"Clash: Response failed: {item_page}")

        price = data.get("average_price", None)
        if not price:
            raise ValueError(f"Clash: Failed to find item price: {item_page}")

        price = float(price)

        return price
