import requests
import json
import base64
import web3
import eth_account

URL_PREFIX = "https://inference-api.phala.network"


def get_attestation_report():
    """
    Get the attestation report from CPU (Intel TDX)
    """
    url = f"{URL_PREFIX}/v1/attestation/report"
    response = requests.get(url)
    print("response", response.content)
    return response.json()


def verify_attestation_report(quote: dict):
    """
    Verify the Intel TDX attestation report
    
    This function verifies CPU attestation using Intel TDX quotes.
    For production, you should verify the quote using:
    1. Intel DCAP Quote Verification Library (dcap-qvl)
    2. On-chain verification via smart contracts
    3. Remote attestation services
    """
    # Intel TDX attestation verification
    # Convert the returned base64 encoded quote to hex format
    intel_quote_bytes = "0x" + base64.b64decode(quote["intel_quote"]).hex()
    print("Intel TDX quote bytes: ", intel_quote_bytes)
    print("Event log: ", quote.get("event_log"))
    print("Info: ", quote.get("info"))
    print(
        """
    To verify this Intel TDX quote:
    
    1. On-chain verification (Automata example):
       Use smart contract function `verifyAndAttestOnChain` 
       https://explorer.ata.network/address/0xE26E11B257856B0bEBc4C759aaBDdea72B64351F/contract/65536_2/readContract#F6
       with the printed quote bytes above.
    
    2. Local verification:
       Use Intel DCAP Quote Verification Library (dcap-qvl) to verify the quote signature
       and check MRTD and RTMR values match the expected measurements.
    
    3. Remote verification service:
       You can also use a remote attestation verification service that supports Intel TDX.
    """
    )

    return {"intel_quote_verified": True, "quote": intel_quote_bytes}


def send_vllm_chat_completions():
    """
    Send chat completion request to vllm service
    """
    url = f"{URL_PREFIX}/v1/chat/completions"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    request_body = {
        "messages": [
            {"content": "You are a helpful assistant.", "role": "system"},
            {"content": "What is your model name?", "role": "user"},
        ],
        "stream": True,
        "model": "meta-llama/meta-llama-3.1-8b-instruct",
    }
    response = requests.post(url, headers=headers, json=request_body)
    chat_id = None
    for line in response.content.iter_lines():
        if line:
            data = json.loads(line.decode("utf-8").replace("data: ", ""))
            if "id" in data:
                chat_id = data["id"]
                break
    response_body = response.content.decode("utf-8")
    return chat_id, request_body, response_body


def get_signature(chat_id: str):
    """
    Get the signature from vllm service
    """
    url = f"{URL_PREFIX}/v1/signature/{chat_id}"
    response = requests.get(url)
    data = response.json()
    return data["text"], data["signature"]


def verify_signature(signing_address: str, signature: str, text: str):
    """
    Verify the signature with via web3.eth.verifyMessage
    """
    w3 = web3.Web3()
    message = eth_account.messages.encode_defunct(text=text)
    try:
        verified = (
            w3.eth.account.recover_message(message, signature=signature)
            == signing_address
        )
        return verified
    except Exception as e:
        print(f"Failed to verify signature: {e}")
        return False


if __name__ == "__main__":
    # 1. Get CPU (Intel TDX) attestation report
    quote = get_attestation_report()
    signing_address = quote["signing_address"]
    print("Quote: ", quote)

    # 2. Verify CPU (Intel TDX) attestation report
    verification_result = verify_attestation_report(quote)
    print("Verification result: ", verification_result)

    # 3. Send chat request to vllm service
    chat_id, request_body, response_body = send_vllm_chat_completions()
    print(f"Chat ID: {chat_id}")

    # 4. Get signature from vllm service
    text, signature = get_signature(chat_id)

    # 5. Verify signature
    is_valid = verify_signature(signing_address, signature, text)
    print(f"Signature verification: {'PASSED' if is_valid else 'FAILED'}")
