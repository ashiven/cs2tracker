from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
from bs4.element import Tag

STEAM_MARKET_SEARCH_PAGE_BASE_URL = "https://steamcommunity.com/market/search?q={}"


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
    @classmethod
    def get_item_page_url(cls, item_href):
        url_encoded_name = item_href.split("/")[-1]
        page_url = STEAM_MARKET_SEARCH_PAGE_BASE_URL.format(url_encoded_name)

        return page_url

    @classmethod
    def parse_item_price(cls, item_page, item_href):
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
