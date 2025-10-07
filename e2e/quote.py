import web3
import eth_utils
import base64
import json
import eth_account

from dstack_sdk import TappdClient


class Quote:
    """
    CPU-only attestation using Intel TDX.
    This class generates Intel TDX quotes for attestation without GPU involvement.
    """
    def __init__(self):
        self.signing_address = None
        self.intel_quote = None
        self.event_log = None
        self.raw_acct = None

    def init(self):
        if self.raw_acct is None:
            w3 = web3.Web3()
            self.raw_acct = w3.eth.account.create()
            self.signing_address = self.raw_acct.address
            pub_keccak = eth_utils.keccak(
                self.raw_acct._key_obj.public_key.to_bytes()
            ).hex()

            self.intel_quote = self.get_quote(pub_keccak)

        return dict(
            intel_quote=self.intel_quote,
            event_log=self.event_log,
            signing_address=self.signing_address,
        )

    def get_quote(self, pub_keccak: str):
        """Get Intel TDX quote from the TEE"""
        # Initialize the client
        client = TappdClient()

        # Get quote for a message
        result = client.tdx_quote(pub_keccak)
        quote = bytes.fromhex(result.quote)
        self.intel_quote = base64.b64encode(quote).decode("utf-8")
        
        # Store event log if available
        if hasattr(result, 'event_log'):
            self.event_log = json.loads(result.event_log) if isinstance(result.event_log, str) else result.event_log
        
        return result.quote

    def sign(self, content: str):
        """Sign content using ECDSA"""
        return self.raw_acct.sign_message(
            eth_account.messages.encode_defunct(text=content)
        ).signature.hex()


quote = Quote()
quote.init()

if __name__ == "__main__":
    print(
        dict(
            intel_quote=quote.intel_quote,
            event_log=quote.event_log,
            signing_address=quote.signing_address,
        )
    )
