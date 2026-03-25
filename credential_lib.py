# v0.1.0
# { "Depends": "py-genlayer:15qfivjvy80800rh998pcxmd2m8va1wq2qzqhz850n8ggcr4i9q0" }
from genlayer import *
import json


# ============================================================
# GenLayer Credential Verification Library
# A reusable library for verifying credentials on-chain.
# No oracle needed — AI validators fetch directly from the web.
#
# Usage in another contract:
#   from credential_lib import verify_credential, verify_domain, extract_credential_info
# ============================================================


def verify_credential(credential_url: str, holder_name: str, expected_issuer: str, credential_type: str) -> str:
    """
    Verify a credential page against expected holder, issuer, and type.
    Returns "verified: explanation" or "rejected: explanation"
    """
    def fetch():
        return gl.get_webpage(credential_url, mode="text")

    result = gl.eq_principles.eq_principle_prompt_non_comparative(
        fetch,
        task="Check this credential page and verify: 1. Is " + holder_name + " visible as holder? 2. Is " + expected_issuer + " visible as issuer? 3. Is " + credential_type + " mentioned? If all match respond: verified: [explanation]. If not respond: rejected: [explanation]",
        criteria="Answer must start with verified: or rejected: followed by brief explanation."
    )
    return str(result).strip()


def verify_domain(url: str, expected_domain: str) -> str:
    """
    Verify that a URL belongs to an expected trusted domain.
    Returns "valid" or "invalid"
    """
    def fetch():
        return gl.get_webpage(url, mode="text")

    result = gl.eq_principles.eq_principle_prompt_non_comparative(
        fetch,
        task="Check if this page is from " + expected_domain + ". Respond only: valid or invalid",
        criteria="Answer must be exactly: valid or invalid"
    )
    return str(result).strip()


def extract_credential_info(credential_url: str) -> str:
    """
    Extract key info from a credential page.
    Returns "holder_name|issuer|credential_type"
    """
    def fetch():
        return gl.get_webpage(credential_url, mode="text")

    result = gl.eq_principles.eq_principle_prompt_non_comparative(
        fetch,
        task="Extract from this credential page: 1. Full name of holder 2. Issuing institution 3. Credential type. Respond with format: name|issuer|credential_type. Example: John Doe|Amazon Web Services|AWS Solutions Architect",
        criteria="Answer must follow format: name|issuer|credential_type"
    )
    return str(result).strip()


# ============================================================
# Example Contract using this library
# ============================================================

class CredentialVerifier(gl.Contract):
    """
    Example contract showing how to use the credential library.
    Deploy this to verify credentials on GenLayer Testnet Bradbury.
    """
    state: str

    def __init__(self):
        self.state = "pending"

    @gl.public.write
    def verify(self, credential_url: str, holder_name: str, expected_issuer: str, credential_type: str) -> None:
        """Verify a credential using the library function."""
        self.state = verify_credential(
            credential_url,
            holder_name,
            expected_issuer,
            credential_type
        )

    @gl.public.write
    def extract_info(self, credential_url: str) -> None:
        """Extract credential info from a URL."""
        self.state = extract_credential_info(credential_url)

    @gl.public.write
    def check_domain(self, url: str, expected_domain: str) -> None:
        """Verify a URL belongs to a trusted domain."""
        self.state = verify_domain(url, expected_domain)

    @gl.public.view
    def get_state(self) -> str:
        return self.state
