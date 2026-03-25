# v0.1.0
# { "Depends": "py-genlayer:15qfivjvy80800rh998pcxmd2m8va1wq2qzqhz850n8ggcr4i9q0" }
from genlayer import *
import json


# ============================================================
# GenLayer API Key Service
# A secure service for using private API keys inside
# Intelligent Contracts without exposing them publicly.
#
# How it works:
# 1. Owner deploys this service and sets their API key
# 2. API key is only used INSIDE the non-deterministic block
#    which runs privately inside each validator's environment
# 3. Other contracts call this service to get API data
#    without ever seeing the actual key
#
# Supported APIs:
# - CoinMarketCap (crypto prices)
# - OpenWeatherMap (weather data)
# - NewsAPI (latest news)
# ============================================================


class ApiKeyService(gl.Contract):
    """
    A secure API key management service for GenLayer Intelligent Contracts.
    The owner registers API keys, and the service fetches data on their
    behalf — keeping keys private inside validator execution environments.
    """
    # API keys stored in contract state
    # Only used inside non-det blocks — never returned to callers
    coinmarketcap_key: str
    openweather_key: str
    newsapi_key: str

    # Last fetched results — readable by anyone
    last_result: str
    last_source: str

    def __init__(self):
        self.coinmarketcap_key = ""
        self.openweather_key = ""
        self.newsapi_key = ""
        self.last_result = ""
        self.last_source = ""

    # --------------------------------------------------------
    # Owner: Register API Keys
    # --------------------------------------------------------

    @gl.public.write
    def set_coinmarketcap_key(self, api_key: str) -> None:
        """
        Register a CoinMarketCap API key.
        Only the deployer should call this.
        Key is stored in state and used privately in validator execution.

        Args:
            api_key: Your CoinMarketCap API key
        """
        assert len(api_key) > 5, "Invalid API key"
        self.coinmarketcap_key = api_key

    @gl.public.write
    def set_openweather_key(self, api_key: str) -> None:
        """
        Register an OpenWeatherMap API key.

        Args:
            api_key: Your OpenWeatherMap API key
        """
        assert len(api_key) > 5, "Invalid API key"
        self.openweather_key = api_key

    @gl.public.write
    def set_newsapi_key(self, api_key: str) -> None:
        """
        Register a NewsAPI key.

        Args:
            api_key: Your NewsAPI key
        """
        assert len(api_key) > 5, "Invalid API key"
        self.newsapi_key = api_key

    # --------------------------------------------------------
    # Public: Fetch Data Using Registered Keys
    # --------------------------------------------------------

    @gl.public.write
    def fetch_crypto_price(self, symbol: str) -> None:
        """
        Fetch crypto price using CoinMarketCap API key.
        Falls back to public CoinGecko API if no key is registered.

        Args:
            symbol: Crypto symbol e.g. "BTC", "ETH", "SOL"
        """
        api_key = self.coinmarketcap_key

        def fetch():
            if api_key and len(api_key) > 5:
                # Use private CoinMarketCap API with registered key
                url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=" + symbol + "&CMC_PRO_API_KEY=" + api_key
            else:
                # Fallback to free public API
                url = "https://api.coingecko.com/api/v3/simple/price?ids=" + symbol.lower() + "&vs_currencies=usd"
            return gl.get_webpage(url, mode="text")

        result = gl.eq_principles.eq_principle_prompt_non_comparative(
            fetch,
            task="Extract the current USD price of " + symbol + " from this data. Respond with the number only. Example: 67423.50",
            criteria="Answer must be a number only, no extra text."
        )
        self.last_result = str(result).strip()
        self.last_source = "coinmarketcap" if api_key else "coingecko_public"

    @gl.public.write
    def fetch_weather(self, city: str) -> None:
        """
        Fetch current weather for a city using OpenWeatherMap API.
        Falls back to a public weather source if no key is registered.

        Args:
            city: City name e.g. "Jakarta", "London", "New York"
        """
        api_key = self.openweather_key

        def fetch():
            if api_key and len(api_key) > 5:
                # Use private OpenWeatherMap API
                url = "https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=" + api_key + "&units=metric"
            else:
                # Fallback to public weather source
                url = "https://wttr.in/" + city + "?format=j1"
            return gl.get_webpage(url, mode="text")

        result = gl.eq_principles.eq_principle_prompt_non_comparative(
            fetch,
            task="Extract the current weather for " + city + ". Respond with: temperature in celsius, weather condition. Example: 28C, Partly Cloudy",
            criteria="Answer must follow format: temperature, condition"
        )
        self.last_result = str(result).strip()
        self.last_source = "openweathermap" if api_key else "wttr_public"

    @gl.public.write
    def fetch_latest_news(self, topic: str) -> None:
        """
        Fetch latest news headlines for a topic using NewsAPI.
        Falls back to a public news source if no key registered.

        Args:
            topic: News topic e.g. "bitcoin", "AI", "GenLayer"
        """
        api_key = self.newsapi_key

        def fetch():
            if api_key and len(api_key) > 5:
                # Use private NewsAPI
                url = "https://newsapi.org/v2/everything?q=" + topic + "&sortBy=publishedAt&apiKey=" + api_key
            else:
                # Fallback to public news source
                url = "https://news.google.com/search?q=" + topic
            return gl.get_webpage(url, mode="text")

        result = gl.eq_principles.eq_principle_prompt_non_comparative(
            fetch,
            task="Extract the top 3 latest news headlines about " + topic + " from this page. Respond with headlines separated by | symbol.",
            criteria="Answer must be headlines separated by | symbol."
        )
        self.last_result = str(result).strip()
        self.last_source = "newsapi" if api_key else "google_news_public"

    # --------------------------------------------------------
    # Read: Get Results
    # --------------------------------------------------------

    @gl.public.view
    def get_last_result(self) -> str:
        """Returns the last fetched data result."""
        return self.last_result

    @gl.public.view
    def get_last_source(self) -> str:
        """Returns which API source was used for last fetch."""
        return self.last_source

    @gl.public.view
    def has_coinmarketcap_key(self) -> str:
        """Returns 'true' if a CoinMarketCap key is registered."""
        return "true" if len(self.coinmarketcap_key) > 5 else "false"

    @gl.public.view
    def has_openweather_key(self) -> str:
        """Returns 'true' if an OpenWeatherMap key is registered."""
        return "true" if len(self.openweather_key) > 5 else "false"

    @gl.public.view
    def has_newsapi_key(self) -> str:
        """Returns 'true' if a NewsAPI key is registered."""
        return "true" if len(self.newsapi_key) > 5 else "false"
