from currency_converter import CurrencyConverter

from cs2tracker.config import get_config

config = get_config()


converter = CurrencyConverter()
CURRENCY_SYMBOLS = {
    "EUR": "€",
    "KRW": "₩",
    "ISK": "kr",
    "HKD": "HK$",
    "SKK": "Sk",
    "SEK": "kr",
    "NOK": "kr",
    "HUF": "Ft",
    "LTL": "Lt",
    "ZAR": "R",
    "PHP": "₱",
    "GBP": "£",
    "MXN": "$",
    "CYP": "£",
    "LVL": "Ls",
    "DKK": "kr",
    "NZD": "NZ$",
    "TRY": "₺",
    "USD": "$",
    "RON": "lei",
    "RUB": "₽",
    "EEK": "kr",
    "CHF": "CHF",
    "MYR": "RM",
    "ILS": "₪",
    "PLN": "zł",
    "BRL": "R$",
    "BGN": "лв",
    "THB": "฿",
    "INR": "₹",
    "ROL": "lei",
    "AUD": "A$",
    "CNY": "¥",
    "HRK": "kn",
    "MTL": "Lm",
    "IDR": "Rp",
    "JPY": "¥",
    "CAD": "C$",
}
CURRENCY_SYMBOLS = {currency: symbol for currency, symbol in CURRENCY_SYMBOLS.items() if currency in converter.currencies}  # type: ignore


def convert(amount, source_currency, target_currency):
    """
    Convert an amount from source currency to target currency.

    :param amount: The amount to convert.
    :param source_currency: The currency to convert from.
    :param target_currency: The currency to convert to.
    :return: The converted amount in the target currency.
    """
    try:
        if target_currency == "EUR":
            converted_amount = converter.convert(amount, source_currency, target_currency)
        else:
            # The currency converter always needs the target or origin currency to be EUR
            # Therefore we need an intermediate conversion step if the target currency is not EUR
            intermediate_amount = converter.convert(amount, source_currency, "EUR")
            converted_amount = converter.convert(intermediate_amount, "EUR", target_currency)

        return round(converted_amount, 2)
    except Exception:
        return 0.0


def to_symbol(currency):
    """
    Convert a currency code to its symbol.

    :param currency: The currency code to convert.
    :return: The symbol of the currency.
    """
    if currency in CURRENCY_SYMBOLS:
        return CURRENCY_SYMBOLS[currency]
    return currency
