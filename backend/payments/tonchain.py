import base64
import binascii
import requests
from decimal import Decimal
from django.conf import settings
from django.utils import timezone

NANO = Decimal("1000000000")

def _crc16_xmodem(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc

def normalize_ton_address(value: str) -> str:
    """Return canonical workchain:hex for raw or friendly TON addresses."""
    value = (value or "").strip()
    if ":" in value:
        workchain, account = value.split(":", 1)
        if len(account) != 64:
            raise ValueError("Invalid TON wallet address.")
        int(account, 16)
        return f"{int(workchain)}:{account.lower()}"
    try:
        raw = base64.urlsafe_b64decode(value + "=" * ((4 - len(value) % 4) % 4))
    except (ValueError, binascii.Error):
        raise ValueError("Invalid TON wallet address.")
    if len(raw) != 36 or raw[0] & 0x7F not in (0x11, 0x51):
        raise ValueError("Invalid TON wallet address.")
    if _crc16_xmodem(raw[:34]) != int.from_bytes(raw[34:], "big"):
        raise ValueError("TON address checksum validation failed.")
    workchain = int.from_bytes(raw[1:2], "big", signed=True)
    return f"{workchain}:{raw[2:34].hex()}"

def _get_transactions(receiver):
    base = getattr(settings, "TONCENTER_API_URL", "https://toncenter.com/api/v2").rstrip("/")
    headers = {"Content-Type": "application/json"}
    api_key = getattr(settings, "TONCENTER_API_KEY", "")
    if api_key:
        headers["X-API-Key"] = api_key
    response = requests.post(
        f"{base}/getTransactions",
        json={"address": receiver, "limit": 30},
        headers=headers,
        timeout=12,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(data.get("error", "TON Center transaction lookup failed"))
    return data.get("result", [])

def find_matching_payment(order):
    """Find a finalized incoming mainnet tx matching recipient, sender, amount and memo."""
    transactions = _get_transactions(order.receiver)
    expected_sender = normalize_ton_address(order.wallet)
    expected_receiver = normalize_ton_address(order.receiver)
    minimum_nano = int(order.amount * NANO)
    created_ts = int(order.created_at.timestamp()) - 90

    for tx in transactions:
        if int(tx.get("utime") or 0) < created_ts:
            continue
        incoming = tx.get("in_msg") or {}
        if not incoming:
            continue
        try:
            if normalize_ton_address(incoming.get("destination", "")) != expected_receiver:
                continue
            if normalize_ton_address(incoming.get("source", "")) != expected_sender:
                continue
        except ValueError:
            continue
        try:
            value = int(incoming.get("value") or 0)
        except (ValueError, TypeError):
            continue
        if value != minimum_nano:
            continue

        # TON Center decodes ordinary text comments into `message`. The frontend
        # sends opcode 0 followed by this exact UTF-8 memo in a TON cell.
        comment = incoming.get("message")
        if comment is None:
            continue
        if str(comment).strip() != order.memo:
            continue

        txid = tx.get("transaction_id") or {}
        tx_hash = txid.get("hash") or tx.get("hash")
        if not tx_hash:
            continue
        return str(tx_hash)
    return None
