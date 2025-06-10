import re

def estrai_messaggi(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    messaggi = []
    for line in lines:
        if ':' in line:
            _, contenuto = line.strip().split(":", 1)
            messaggi.append(contenuto.strip())
    return " ".join(messaggi)

def lzw_compress(text):
    # Dizionario iniziale: tutti i singoli caratteri ASCII
    dict_size = 256
    dictionary = {chr(i): i for i in range(dict_size)}
    
    w = ""
    compressed = []
    
    for c in text:
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            compressed.append(dictionary[w])
            dictionary[wc] = dict_size
            dict_size += 1
            w = c

    if w:
        compressed.append(dictionary[w])

    # Invertiamo il dizionario per averlo: codice → stringa
    reverse_dict = {v: k for k, v in dictionary.items()}
    return compressed, reverse_dict

# === Uso con i tuoi file ===
alice_txt = "alice.txt"
bob_txt = "bob.txt"

alice_str = estrai_messaggi(alice_txt)
bob_str = estrai_messaggi(bob_txt)

compressed_alice, dict_alice = lzw_compress(alice_str)
compressed_bob, dict_bob = lzw_compress(bob_str)

def lzw_decompress(compressed, initial_dict=None):
    # Dizionario iniziale: tutti i singoli caratteri ASCII
    dict_size = 256
    dictionary = {i: chr(i) for i in range(dict_size)} if initial_dict is None else dict(initial_dict)

    result = []
    w = chr(compressed[0])
    result.append(w)

    for k in compressed[1:]:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + w[0]  # caso speciale
        else:
            raise ValueError(f"Token {k} non trovato nel dizionario.")

        result.append(entry)

        # Aggiunge una nuova entrata al dizionario
        dictionary[dict_size] = w + entry[0]
        dict_size += 1

        w = entry

    return "".join(result)



originale = estrai_messaggi("bob.txt")
compressed, _ = lzw_compress(originale)
decompressed = lzw_decompress(compressed)

if originale == decompressed:
    print("Compressione OK: decompressione corretta.")
else:
    print("Errore: il testo ricostruito è diverso da quello originale.")

def normalizza(s):
    return " ".join(s.split())

if normalizza(originale) == normalizza(decompressed):
    print("Compressione OK (con normalizzazione).")
else:
    print("Differenze trovate anche dopo la normalizzazione.")

print("Dizionario Alice (ultimi 10):", list(dict_alice.items())[-10:])
print("Dizionario Bob (ultimi 10):", list(dict_bob.items())[-10:])


print("Numero voci dizionario Alice:", len(dict_alice))
print("Numero voci dizionario Bob:", len(dict_bob))