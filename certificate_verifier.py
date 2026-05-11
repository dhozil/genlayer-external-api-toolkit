# v0.1.0
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json


class CertificateVerifier(gl.Contract):
    """
    GenLayer Certificate Verifier

    Verifies academic degrees and professional certifications
    directly from their public badge/certificate URLs.

    Each validator independently fetches the public page and evaluates
    whether the certificate matches the expected holder, issuer, and type.
    Consensus via prompt_non_comparative — AI evaluates equivalence.

    No API keys or secrets are used. All data sources are public URLs.
    """

    state: str

    def __init__(self):
        self.state = "pending"

    @gl.public.write
    def verify(self, certificate_url: str, holder_name: str, expected_issuer: str, certificate_type: str) -> None:
        """
        Verify a public certificate page against expected holder, issuer, and type.

        Args:
            certificate_url: Public URL to the certificate or badge (e.g. credly.com/badges/...)
            holder_name:     Full name of the certificate holder
            expected_issuer: Name of the issuing institution (e.g. "Amazon Web Services")
            certificate_type: Type of certificate (e.g. "AWS Solutions Architect")
        """
        def fetch() -> str:
            res = gl.nondet.web.get(certificate_url)
            return res.body.decode("utf-8")[:3000]

        result = gl.eq_principle.prompt_non_comparative(
            fetch,
            task=(
                "Check this public certificate page and verify: "
                "1. Is " + holder_name + " visible as the certificate holder? "
                "2. Is " + expected_issuer + " visible as the issuing institution? "
                "3. Is " + certificate_type + " mentioned as the certificate type? "
                "If all three match respond: verified: [brief explanation]. "
                "If any do not match respond: rejected: [brief explanation]."
            ),
            criteria="Answer must start with verified: or rejected: followed by a brief explanation."
        )
        self.state = str(result).strip()

    @gl.public.write
    def check_domain(self, url: str, expected_domain: str) -> None:
        """
        Verify a URL belongs to a trusted certificate authority domain.
        Returns "valid" or "invalid".

        Args:
            url:             Public URL to verify
            expected_domain: Expected domain e.g. "credly.com", "coursera.org"
        """
        def fetch() -> str:
            res = gl.nondet.web.get(url)
            return res.body.decode("utf-8")[:1000]

        result = gl.eq_principle.prompt_non_comparative(
            fetch,
            task="Check if this page is served from " + expected_domain + ". Respond only: valid or invalid",
            criteria="Answer must be exactly: valid or invalid"
        )
        self.state = str(result).strip()

    @gl.public.write
    def extract_info(self, certificate_url: str) -> None:
        """
        Extract key information from a public certificate page.
        Returns "holder_name|issuer|certificate_type"

        Args:
            certificate_url: Public URL to the certificate or badge
        """
        def fetch() -> str:
            res = gl.nondet.web.get(certificate_url)
            return res.body.decode("utf-8")[:3000]

        result = gl.eq_principle.prompt_non_comparative(
            fetch,
            task=(
                "Extract from this public certificate page: "
                "1. Full name of the certificate holder "
                "2. Issuing institution "
                "3. Certificate type. "
                "Respond with format: name|issuer|certificate_type. "
                "Example: John Doe|Amazon Web Services|AWS Solutions Architect"
            ),
            criteria="Answer must follow format: name|issuer|certificate_type"
        )
        self.state = str(result).strip()

    @gl.public.view
    def get_state(self) -> str:
        return self.state
