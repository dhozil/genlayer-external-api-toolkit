# v0.1.0
# { "Depends": "py-genlayer:15qfivjvy80800rh998pcxmd2m8va1wq2qzqhz850n8ggcr4i9q0" }
from genlayer import *
import json


class PriceFeedLib(gl.Contract):
    state: str

    def __init__(self):
        self.state = "ready"

    @gl.public.write
    def fetch_crypto_price(self, symbol: str) -> None:
        """Fetch current crypto price in USD. Example: symbol = 'bitcoin'"""
        def fetch():
            return gl.get_webpage("https://api.coingecko.com/api/v3/simple/price?ids=" + symbol + "&vs_currencies=usd", mode="text")

        result = gl.eq_principles.eq_principle_prompt_non_comparative(
            fetch,
            task="Extract the current USD price of " + symbol + " from this data. Respond with the number only. Example: 67423.50",
            criteria="Answer must be a number only, no extra text."
        )
        self.state = str(result).strip()

    @gl.public.write
    def check_price_above(self, symbol: str, threshold: str) -> None:
        """Check if crypto price is above threshold. Example: symbol='bitcoin', threshold='60000'"""
        def fetch():
            return gl.get_webpage("https://api.coingecko.com/api/v3/simple/price?ids=" + symbol + "&vs_currencies=usd", mode="text")

        result = gl.eq_principles.eq_principle_prompt_non_comparative(
            fetch,
            task="Check if the current price of " + symbol + " is above " + threshold + " USD. Respond only: true or false",
            criteria="Answer must be exactly: true or false"
        )
        self.state = str(result).strip()

    @gl.public.write
    def check_price_below(self, symbol: str, threshold: str) -> None:
        """Check if crypto price is below threshold. Example: symbol='bitcoin', threshold='100000'"""
        def fetch():
            return gl.get_webpage("https://api.coingecko.com/api/v3/simple/price?ids=" + symbol + "&vs_currencies=usd", mode="text")

        result = gl.eq_principles.eq_principle_prompt_non_comparative(
            fetch,
            task="Check if the current price of " + symbol + " is below " + threshold + " USD. Respond only: true or false",
            criteria="Answer must be exactly: true or false"
        )
        self.state = str(result).strip()

    @gl.public.write
    def fetch_stock_price(self, ticker: str) -> None:
        """Fetch current stock price in USD. Example: ticker = 'AAPL'"""
        def fetch():
            return gl.get_webpage("https://finance.yahoo.com/quote/" + ticker, mode="text")

        result = gl.eq_principles.eq_principle_prompt_non_comparative(
            fetch,
            task="Extract the current stock price of " + ticker + " in USD from this page. Respond with the number only. Example: 182.50",
            criteria="Answer must be a number only, no extra text."
        )
        self.state = str(result).strip()

    @gl.public.view
    def get_state(self) -> str:
        return self.state
