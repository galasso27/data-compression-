import os
import sys
from lzw import estrai_messaggi, lzw_compress, lzw_decompress


def main(alice_file="alice.txt", bob_file="bob.txt"):
    if not os.path.exists(alice_file) and os.path.exists("alixe.txt"):
        alice_file = "alixe.txt"
    alice_str = estrai_messaggi(alice_file)
    bob_str = estrai_messaggi(bob_file)

    compressed_alice, dict_alice = lzw_compress(alice_str)
    compressed_bob, dict_bob = lzw_compress(bob_str)

    dec_alice = lzw_decompress(compressed_alice)
    dec_bob = lzw_decompress(compressed_bob)
    if alice_str == dec_alice and bob_str == dec_bob:
        print("Compressione OK per entrambi i file.")
    else:
        print("Errore nella compressione/decompressione.")

    print("Dizionario Alice (ultimi 10):", list(dict_alice.items())[-10:])
    print("Numero voci dizionario Alice:", len(dict_alice))

    print("Dizionario Bob (ultimi 10):", list(dict_bob.items())[-10:])
    print("Numero voci dizionario Bob:", len(dict_bob))


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        main(sys.argv[1], sys.argv[2])
    else:
        main()
