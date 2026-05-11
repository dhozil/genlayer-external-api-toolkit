# 🛠️ GenLayer External API Toolkit

A collection of reusable Intelligent Contract libraries for fetching live external data on GenLayer — no oracle, no trusted third parties.

> **"Fetch live crypto prices and verify public certificates directly on-chain. Each validator independently fetches the data and reaches consensus."**

-----

## 📦 What's Inside

| File                      | Purpose                                                                   |
|---------------------------|---------------------------------------------------------------------------|
| `price_feed_lib.py`       | Fetch live crypto prices from CoinGecko free public API                   |
| `certificate_verifier.py` | Verify academic degrees and professional certifications from public URLs   |

-----

## 🏗️ Architecture

This toolkit follows the canonical GenLayer pattern for external data:

```
Each validator independently:
    → calls gl.nondet.web.get(url) to fetch a public endpoint
    → processes the response locally
    → reaches consensus via gl.eq_principle.*
```

Both libraries use **fully public endpoints** — CoinGecko free tier requires no authentication, and certificate pages (Credly, Coursera, etc.) are publicly accessible URLs.

For **binary checks** (is price above X?): `gl.eq_principle.strict_eq()` — all validators must agree exactly.

For **qualitative checks** (does the certificate match?): `gl.eq_principle.prompt_non_comparative()` — AI evaluates equivalence across validators.

-----

## 📈 Price Feed Library (`price_feed_lib.py`)

Fetch live crypto prices directly from CoinGecko's free public API. No authentication required.

### Methods

| Method                  | Parameters           | Returns               |
|-------------------------|----------------------|-----------------------|
| `check_price_above`     | `coin_id, threshold` | `"true"` or `"false"` |
| `check_price_below`     | `coin_id, threshold` | `"true"` or `"false"` |
| `fetch_market_cap_rank` | `coin_id`            | rank number as string |
| `fetch_crypto_price`    | `coin_id`            | price in USD          |
| `get_state`             | —                    | last result           |

### Example Usage

```python
# Check if BTC is above $60,000
check_price_above("bitcoin", "60000")   # → "true"

# Check if ETH is below $5,000
check_price_below("ethereum", "5000")   # → "true"

# Get market cap rank
fetch_market_cap_rank("solana")         # → "5"
```

### Use in Another Contract

```python
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json

class AutoLiquidator(gl.Contract):
    state: str

    def __init__(self):
        self.state = "monitoring"

    @gl.public.write
    def check_liquidation(self) -> None:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"

        def fetch() -> str:
            res = gl.nondet.web.get(url)
            data = json.loads(res.body.decode("utf-8"))
            price = float(data["ethereum"]["usd"])
            return "true" if price < 2000.0 else "false"

        result = gl.eq_principle.strict_eq(fetch)
        self.state = "liquidated" if str(result) == "true" else "safe"

    @gl.public.view
    def get_state(self) -> str:
        return self.state
```

-----

## 🎓 Certificate Verifier (`certificate_verifier.py`)

Verify academic degrees and professional certifications from any **public** badge/certificate URL. AI validators independently fetch the page and reach consensus — no oracle needed.

### Methods

| Method         | Parameters                                                             | Returns                                |
|----------------|------------------------------------------------------------------------|----------------------------------------|
| `verify`       | `certificate_url, holder_name, expected_issuer, certificate_type`      | `"verified: ..."` or `"rejected: ..."` |
| `check_domain` | `url, expected_domain`                                                 | `"valid"` or `"invalid"`               |
| `extract_info` | `certificate_url`                                                      | `"name|issuer|type"`                   |
| `get_state`    | —                                                                      | last result                            |

### Example Usage

```python
verify(
    "https://www.credly.com/badges/example",
    "John Doe",
    "Amazon Web Services",
    "AWS Solutions Architect"
)
# → "verified: Name, issuer and certificate type all match."
```

-----

## 🚀 Deploy (GenLayer Studio)

1. Go to [studio.genlayer.com](https://studio.genlayer.com)
2. Create new contract → paste `price_feed_lib.py` or `certificate_verifier.py`
3. Deploy — **no parameters needed**
4. Call any Write method to fetch live data
5. Call `get_state` (Read) to see the result

-----

## 🆚 vs Traditional Oracle Solutions

| Feature               | Chainlink  | Pyth       | GenLayer Toolkit  |
|-----------------------|------------|------------|-------------------|
| Oracle dependency     | ✅ Required | ✅ Required | ❌ Not needed      |
| Custom data sources   | ❌          | ❌          | ✅ Any public URL  |
| Language              | Solidity   | Rust       | ✅ Python          |
| Subjective validation | ❌          | ❌          | ✅ AI-powered      |

-----

## 🧪 Testnet Deployment

**Network:** GenLayer Testnet Bradbury

-----

## 📄 License

MIT — free to use, fork, and build upon.

-----

## 🏗️ Built With

- [GenLayer](https://genlayer.com) — AI-native blockchain
- [GenVM Python SDK](https://docs.genlayer.com) — Intelligent Contract framework
- Built as part of the [GenLayer Incentivized Builder Program](https://portal.genlayer.foundation)
