import re
from datetime import datetime

TIMESTAMP_RE = re.compile(r"^(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}) ([^:]+): (.*)")

def parse_chat(file_path):
    """Parses a chat log returning a list of (datetime, full_line) tuples."""
    messages = []
    with open(file_path, "r", encoding="utf-8") as f:
        current = None
        for line in f:
            line = line.rstrip("\n")
            m = TIMESTAMP_RE.match(line)
            if m:
                if current:
                    messages.append(current)
                ts_str, speaker, text = m.groups()
                ts = datetime.strptime(ts_str, "%d/%m/%Y %H:%M:%S")
                current = [ts, f"{ts_str} {speaker}: {text}"]
            else:
                if current:
                    current[1] += " " + line.strip()
        if current:
            messages.append(current)
    return messages

def sync_chats(files, output_path="merged_chat.txt"):
    """Merge chats based on timestamp and write ordered messages to a file."""
    all_msgs = []
    for path in files:
        all_msgs.extend(parse_chat(path))
    all_msgs.sort(key=lambda x: x[0])

    seen = set()
    with open(output_path, "w", encoding="utf-8") as out:
        for _, line in all_msgs:
            if line not in seen:
                out.write(line + "\n")
                seen.add(line)
    return output_path

def estrai_messaggi(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    messaggi = []
    for line in lines:
        if ':' in line:
            _, contenuto = line.strip().split(":", 1)
            messaggi.append(contenuto.strip())
    return " ".join(messaggi)

def lzw_compress(text, initial_dict=None):
    """Compress text using LZW. If initial_dict is provided it will be used
    as the starting dictionary."""
    dict_size = 256
    if initial_dict is not None:
        dictionary = dict(initial_dict)
        if dictionary:
            dict_size = max(dictionary.values()) + 1
    else:
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

def build_merged_dictionary(alice_txt="alice.txt", bob_txt="bob.txt"):
    """Return dictionaries obtained from the merged chat of alice and bob."""
    merged_file = sync_chats([alice_txt, bob_txt])
    merged_str = estrai_messaggi(merged_file)
    _, rev_dict = lzw_compress(merged_str)
    fwd_dict = {v: k for k, v in rev_dict.items()}
    return rev_dict, fwd_dict, merged_file

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



def main():
    alice_txt = "alice.txt"
    bob_txt = "bob.txt"

    rev_dict, _, merged_file = build_merged_dictionary(alice_txt, bob_txt)

    originale = estrai_messaggi(merged_file)
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

    print("Dizionario conversazione (ultimi 10):", list(rev_dict.items())[-10:])

    print("Numero voci dizionario conversazione:", len(rev_dict))

if __name__ == "__main__":
    main()
