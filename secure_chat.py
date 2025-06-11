import hashlib
import secrets
from lzw import lzw_compress, lzw_decompress, build_merged_dictionary


DH_PRIME = int(
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E08"
    "8A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B"
    "302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9"
    "A637ED6B0BFF5CB6F406B7EDCEE386BFB5A899FA5AE9F24117C4B1FE"
    "649286651ECE65381FFFFFFFFFFFFFFFF",
    16,
)
DH_GENERATOR = 2


def generate_dh_key() -> str:
    """Return a shared key obtained via a Diffie-Hellman exchange."""
    p = DH_PRIME
    g = DH_GENERATOR
    a = secrets.randbelow(p - 2) + 1
    b = secrets.randbelow(p - 2) + 1
    A = pow(g, a, p)
    B = pow(g, b, p)
    shared_a = pow(B, a, p)
    shared_b = pow(A, b, p)
    assert shared_a == shared_b
    # Hash the shared secret to obtain a fixed-size key
    return hashlib.sha256(str(shared_a).encode("utf-8")).hexdigest()


def _keystream(key: str, token_str: str) -> bytes:
    """Derive a pseudorandom keystream for a token."""
    data = (key + token_str).encode("utf-8")
    return hashlib.sha256(data).digest()[:4]


def encrypt_message(message: str, base_dict_fwd: dict, key: str):
    """Compress and encrypt a message using a shared dictionary and key."""
    tokens, final_dict = lzw_compress(message, initial_dict=base_dict_fwd)
    encrypted = []
    for t in tokens:
        ks = _keystream(key, final_dict[t])
        token_bytes = t.to_bytes(4, "big")
        enc = bytes(a ^ b for a, b in zip(token_bytes, ks))
        encrypted.append(enc.hex())
    return encrypted


def decrypt_message(encrypted_tokens, base_dict_rev: dict, key: str):
    """Decrypt and decompress tokens using the shared dictionary and key."""
    dictionary = dict(base_dict_rev)
    dict_size = max(dictionary.keys()) + 1 if dictionary else 0
    decrypted_tokens = []
    w = None
    for enc_hex in encrypted_tokens:
        enc_bytes = bytes.fromhex(enc_hex)
        found_code = None
        for code, token_str in dictionary.items():
            ks = _keystream(key, token_str)
            candidate = int.from_bytes(bytes(a ^ b for a, b in zip(enc_bytes, ks)), "big")
            if candidate == code:
                found_code = code
                break
        if found_code is None:
            raise ValueError("Impossibile decifrare token")
        decrypted_tokens.append(found_code)
        entry = dictionary[found_code]
        if w is not None:
            dictionary[dict_size] = w + entry[0]
            dict_size += 1
        w = entry
    return lzw_decompress(decrypted_tokens, initial_dict=base_dict_rev)


if __name__ == "__main__":
    rev_dict, fwd_dict, _ = build_merged_dictionary()

    print("Generazione della chiave tramite Diffie-Hellman...")
    secret_key = generate_dh_key()
    print("Chiave condivisa ottenuta:\n", secret_key)

    msg = input("Inserisci il nuovo messaggio da cifrare: ")

    encrypted = encrypt_message(msg, fwd_dict, secret_key)
    print("Token cifrati:", encrypted)
    decrypted = decrypt_message(encrypted, rev_dict, secret_key)
    print("Messaggio decifrato:", decrypted)
