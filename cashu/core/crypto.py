import base64
import hashlib
from typing import Dict, List

from cashu.core.secp import PrivateKey, PublicKey
from cashu.core.settings import MAX_ORDER


def derivation_path_newer_than(d1: str, d2: str):
    """
    Returns whether derivation path d1 is newer (deeper down the derivation tree)
    than d2. Used for treating tokens with old keysets differently.
    """
    # NOTE: Derivation paths are still just simple integers for now. This function needs
    # to change once we upgrade to BIP32.

    # the very first derivation path was "" (empty string) so anything is newer than itself
    if d1 == "" and d2 != "":
        return False
    return int(d1) > int(d2)


def derive_keys(master_key: str, derivation_path: str = ""):
    """
    Deterministic derivation of keys for 2^n values.
    TODO: Implement BIP32.
    """
    return {
        2
        ** i: PrivateKey(
            hashlib.sha256((str(master_key) + derivation_path + str(i)).encode("utf-8"))
            .hexdigest()
            .encode("utf-8")[:32],
            raw=True,
        )
        for i in range(MAX_ORDER)
    }


def derive_pubkeys(keys: Dict[int, PrivateKey]):
    return {amt: keys[amt].pubkey for amt in [2**i for i in range(MAX_ORDER)]}


def derive_keyset_id(keys: Dict[str, PublicKey]):
    """Deterministic derivation keyset_id from set of public keys."""
    pubkeys_concat = "".join([p.serialize().hex() for _, p in keys.items()])
    return base64.b64encode(
        hashlib.sha256((pubkeys_concat).encode("utf-8")).digest()
    ).decode()[:12]
