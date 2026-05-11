# v0.1.0

# { “Depends”: “py-genlayer:15qfivjvy80800rh998pcxmd2m8va1wq2qzqhz850n8ggcr4i9q0” }

from genlayer import *
import json

class CredentialVerifier(gl.Contract):
“””
GenLayer Credential Verification Library

```
Verifies academic degrees and professional certifications
directly from public URLs — no oracle, no trusted third party.

Each validator independently fetches and evaluates the credential page.
Consensus via prompt_non_comparative — AI evaluates equivalence.
"""
state: str

def __init__(self):
    self.state = "pending"

@gl.public.write
def verify(self, credential_url: str, holder_name: str, expected_issuer: str, credential_type: str) -> None:
    """
    Verify a credential page against expected holder, issuer, and type.

    Args:
        credential_url:  Public URL to the credential
        holder_name:     Full name of the credential holder
        expected_issuer: Name of the issuing institution
        credential_type: Type of credential e.g. "AWS Certification"
    """
    def fetch() -> str:
        res = gl.nondet.web.get(credential_url)
        return res.body.decode("utf-8")[:3000]

    result = gl.eq_principle.prompt_non_comparative(
        fetch,
        task="Check this credential page and verify: 1. Is " + holder_name + " visible as holder? 2. Is " + expected_issuer + " visible as issuer? 3. Is " + credential_type + " mentioned? If all match respond: verified: [explanation]. If not respond: rejected: [explanation]",
        criteria="Answer must start with verified: or rejected: followed by brief explanation."
    )
    self.state = str(result).strip()

@gl.public.write
def check_domain(self, url: str, expected_domain: str) -> None:
    """
    Verify a URL belongs to a trusted domain.
    Returns "valid" or "invalid".

    Args:
        url:             URL to verify
        expected_domain: Expected domain e.g. "credly.com"
    """
    def fetch() -> str:
        res = gl.nondet.web.get(url)
        return res.body.decode("utf-8")[:1000]

    result = gl.eq_principle.prompt_non_comparative(
        fetch,
        task="Check if this page is from " + expected_domain + ". Respond only: valid or invalid",
        criteria="Answer must be exactly: valid or invalid"
    )
    self.state = str(result).strip()

@gl.public.write
def extract_info(self, credential_url: str) -> None:
    """
    Extract key info from a credential page.
    Returns "holder_name|issuer|credential_type"

    Args:
        credential_url: Public URL to the credential
    """
    def fetch() -> str:
        res = gl.nondet.web.get(credential_url)
        return res.body.decode("utf-8")[:3000]

    result = gl.eq_principle.prompt_non_comparative(
        fetch,
        task="Extract from this credential page: 1. Full name of holder 2. Issuing institution 3. Credential type. Respond with format: name|issuer|credential_type. Example: John Doe|Amazon Web Services|AWS Solutions Architect",
        criteria="Answer must follow format: name|issuer|credential_type"
    )
    self.state = str(result).strip()

@gl.public.view
def get_state(self) -> str:
    return self.state
```