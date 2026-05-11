# v0.1.0

# { “Depends”: “py-genlayer:15qfivjvy80800rh998pcxmd2m8va1wq2qzqhz850n8ggcr4i9q0” }

from genlayer import *
import json

class PriceFeedLib(gl.Contract):
“””
GenLayer Price Feed Library — Architecturally Correct

```
Fetches live crypto prices directly from CoinGecko free public API.
No API keys. No centralized vaults. No shared secrets.

Each validator independently fetches the price.
Binary checks (above/below threshold) use strict_eq — exact consensus.
Raw price uses prompt_non_comparative with numeric criteria — handles
minor differences between validators due to timing.
"""
state: str

def __init__(self):
    self.state = "ready"

@gl.public.write
def check_price_above(self, coin_id: str, threshold: str) -> None:
    """
    Check if crypto price is above a threshold.
    Binary result → strict_eq. All validators must agree.

    Args:
        coin_id:   CoinGecko coin ID e.g. "bitcoin", "ethereum", "solana"
        threshold: USD threshold e.g. "60000"
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=" + coin_id + "&vs_currencies=usd"
    threshold_val = float(threshold)

    def fetch() -> str:
        res = gl.nondet.web.get(url)
        data = json.loads(res.body.decode("utf-8"))
        price = float(list(data.values())[0]["usd"])
        return "true" if price > threshold_val else "false"

    result = gl.eq_principle.strict_eq(fetch)
    self.state = str(result)

@gl.public.write
def check_price_below(self, coin_id: str, threshold: str) -> None:
    """
    Check if crypto price is below a threshold.
    Binary result → strict_eq. All validators must agree.

    Args:
        coin_id:   CoinGecko coin ID e.g. "bitcoin"
        threshold: USD threshold e.g. "100000"
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=" + coin_id + "&vs_currencies=usd"
    threshold_val = float(threshold)

    def fetch() -> str:
        res = gl.nondet.web.get(url)
        data = json.loads(res.body.decode("utf-8"))
        price = float(list(data.values())[0]["usd"])
        return "true" if price < threshold_val else "false"

    result = gl.eq_principle.strict_eq(fetch)
    self.state = str(result)

@gl.public.write
def fetch_market_cap_rank(self, coin_id: str) -> None:
    """
    Fetch market cap rank of a coin from CoinGecko.
    Rank is a stable integer → strict_eq.

    Args:
        coin_id: CoinGecko coin ID e.g. "bitcoin", "ethereum"
    """
    url = "https://api.coingecko.com/api/v3/coins/" + coin_id + "?localization=false&tickers=false&community_data=false&developer_data=false"

    def fetch() -> str:
        res = gl.nondet.web.get(url)
        data = json.loads(res.body.decode("utf-8"))
        rank = data.get("market_cap_rank", "unknown")
        return str(rank)

    result = gl.eq_principle.strict_eq(fetch)
    self.state = str(result)

@gl.public.write
def fetch_crypto_price(self, coin_id: str) -> None:
    """
    Fetch live crypto price in USD.
    Uses prompt_non_comparative — validators may get slightly different
    prices due to timing, AI evaluates if they are numerically close.

    Args:
        coin_id: CoinGecko coin ID e.g. "bitcoin", "ethereum"
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=" + coin_id + "&vs_currencies=usd"

    def fetch() -> str:
        res = gl.nondet.web.get(url)
        data = json.loads(res.body.decode("utf-8"))
        price = float(list(data.values())[0]["usd"])
        return str(price)

    result = gl.eq_principle.prompt_non_comparative(
        fetch,
        task="Extract the numeric price value from this result: " + coin_id,
        criteria="The values must be within 1% of each other to be considered equivalent."
    )
    self.state = str(result)

@gl.public.view
def get_state(self) -> str:
    return self.state
```