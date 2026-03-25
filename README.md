# 🔐 GenLayer API Key Service

A secure service for using private API keys inside GenLayer Intelligent Contracts — without ever exposing them publicly.

> “Use premium APIs inside your contract. Validators use the key privately. Nobody else sees it.”

-----

## 🔍 The Problem

Every useful API requires a key:

- CoinMarketCap — real-time crypto prices
- OpenWeatherMap — live weather data
- NewsAPI — latest headlines

But in traditional smart contracts, everything is public on-chain. You cannot use a private API key without exposing it to everyone.

GenLayer solves this because API keys are only used inside the validator’s private execution environment — the non-deterministic block — and are never returned to external callers.

-----

## ⚙️ How It Works
Owner deploys ApiKeyService
    └─> Registers API keys via set_*_key() methods
    └─> Keys stored in contract state

Anyone calls fetch_crypto_price("BTC")
    └─> Non-det block runs PRIVATELY inside each validator
    └─> Key is used to call CoinMarketCap API internally
    └─> Only the RESULT is returned on-chain
    └─> The key itself is never exposed to callers

Anyone calls get_last_result()
    └─> Returns the fetched price data
    └─> No API key visible anywhere

-----

## 📦 Supported APIs

|API           |Method                      |Free Fallback       |
|--------------|----------------------------|--------------------|
|CoinMarketCap |`fetch_crypto_price(symbol)`|✅ CoinGecko public  |
|OpenWeatherMap|`fetch_weather(city)`       |✅ wttr.in public    |
|NewsAPI       |`fetch_latest_news(topic)`  |✅ Google News public|


> 💡 All methods work even without a registered API key — they fall back to free public sources automatically.

-----

## 🚀 Quick Deploy (GenLayer Studio)

1. Go to [studio.genlayer.com](https://studio.genlayer.com)
1. Create new contract → paste api_key_service.py
1. Deploy — no parameters needed

### Register your API keys (optional):
set_coinmarketcap_key → "your_key_here"
set_openweather_key   → "your_key_here"
set_newsapi_key       → "your_key_here"

### Fetch data:
fetch_crypto_price → symbol: "BTC"
fetch_weather      → city: "Jakarta"
fetch_latest_news  → topic: "bitcoin"

### Read result:
get_last_result() → "67423.50"
get_last_source() → "coinmarketcap"

-----

## 💡 Usage in Another Contract
# Another contract can call this service
class InsuranceContract(gl.Contract):
    state: str

    def __init__(self):
        self.state = "active"

    @gl.public.write
    def check_weather_claim(self, city: str) -> None:
        def fetch():
            url = "https://wttr.in/" + city + "?format=j1"
            return gl.get_webpage(url, mode="text")

        result = gl.eq_principles.eq_principle_prompt_non_comparative(
            fetch,
            task="Is there extreme weather (storm, flood, hurricane) in " + city + "? Respond: yes or no",
            criteria="Answer must be yes or no"
        )
        if str(result).strip() == "yes":
            self.state = "claim_approved"
        else:
            self.state = "claim_rejected"

-----

## 🆚 vs Traditional Approach

|Feature            |Traditional (Ethereum)|GenLayer API Key Service  |
|-------------------|----------------------|--------------------------|
|API key privacy    |❌ Impossible          |✅ Private in validator env|
|External API access|❌ Oracle required     |✅ Direct fetch            |
|Free fallback      |❌                     |✅ Auto fallback           |
|Supported sources  |Fixed oracle feeds    |✅ Any public URL          |
|Language           |Solidity              |✅ Python                  |

-----

## 🧪 Testnet Deployment

Network: GenLayer Testnet Bradbury
Transaction Hash: *(update after deployment)*

-----

## 📄 License

MIT — free to use, fork, and build upon.

-----

## 🏗️ Built With

- [GenLayer](https://genlayer.com) — AI-native blockchain
- [GenVM Python SDK](https://docs.genlayer.com) — Intelligent Contract framework
- Built as part of the [GenLayer Incentivized Builder Program](https://portal.genlayer.foundation)
