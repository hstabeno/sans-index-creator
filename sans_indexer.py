#!/usr/bin/env python3
import argparse
import requests
import fitz  # PyMuPDF
import csv
from collections import defaultdict
import string

def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate keyword index from a SANS PDF.")
    parser.add_argument("-i", "--input-file", required=True, help="Input PDF file")
    parser.add_argument("-o", "--output-file", help="Output file (.txt or .csv)")
    parser.add_argument("--csv", action="store_true", help="Output index as CSV")
    parser.add_argument("--book-starts", nargs='+', type=int, required=True,
                        help="Start PDF page numbers for each book (1-based)")
    parser.add_argument("--skip-first", nargs='+', type=int, required=True,
                        help="Pages to skip at the start of each book (e.g. blank/unnumbered)")
    parser.add_argument("--skip-last", nargs='+', type=int, required=True,
                        help="Pages to skip at the end of each book")
    parser.add_argument("--wordlist", help="Optional path to a custom word list (.txt)")
    return parser.parse_args()

def fetch_common_words(custom_path=None):
    if custom_path:
        print(f"[*] Loading custom word list from: {custom_path}")
        with open(custom_path, "r", encoding="utf-8") as f:
            return set(word.strip().lower() for word in f if word.strip())
    else:
        print("[*] Downloading default English word list...")
        url = "https://raw.githubusercontent.com/dwyl/english-words/master/words.txt"
        return set(requests.get(url).text.lower().split())

def remove_non_utf8(text):
    clean = text.encode("utf-8", "ignore").decode("utf-8", "ignore")
    return ''.join(c for c in clean if c in string.printable or c.isspace())

def extract_book_pages(pdf_path, book_starts, skip_first, skip_last):
    print(f"[*] Extracting valid book pages from: {pdf_path}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    book_count = len(book_starts)

    if not (len(skip_first) == len(skip_last) == book_count):
        raise ValueError("Length of --book-starts, --skip-first, and --skip-last must match.")

    book_starts = [b - 1 for b in book_starts]  # Convert 1-based to 0-based

    indexed_pages = []

    for i in range(book_count):
        book_num = i + 1
        start = book_starts[i]
        end = book_starts[i + 1] if i + 1 < book_count else total_pages

        if start < 0 or end > total_pages:
            raise ValueError(f"Book {book_num}: start or end out of bounds.")

        first = start + skip_first[i]
        last = end - skip_last[i]

        for p in range(first, last):
            if p < total_pages:
                page_num_in_book = p - start - skip_first[i] + 1
                raw_text = doc[p].get_text()
                clean_text = remove_non_utf8(raw_text)
                indexed_pages.append((book_num, page_num_in_book, clean_text))
    return indexed_pages

def strip_characters(word):
    chars = "()'\":,”“‘?;-•’—…[]!"
    suffixes = ["'s", "'re", "'ve", "'t", "[0]", "[1]", "[2]", "[3]", "[4]", "[5]", "[6]"]
    word = word.replace("’", "'")
    for suf in suffixes:
        if word.endswith(suf):
            word = word[: -len(suf)]
    return word.strip(chars).rstrip(".")

def word_is_eligible(word, common_words):
    if len(word) < 3 or word[0].isdigit():
        return False
    if word.lower() in common_words or word.lower() + "s" in common_words:
        return False
    if word.startswith("http://") or word.startswith("https://"):
        return False
    return True

def index_words(pages, common_words):
    index = {}
    total_words = []

    for (book, page_num, text) in pages:
        clean_text = ' '.join(text.replace("\n", " ").replace("\t", " ").split())
        words = [strip_characters(w).lower() for w in clean_text.split()]
        filtered = [w for w in words if word_is_eligible(w, common_words)]
        total_words.extend(filtered)
        index[(book, page_num)] = filtered

    return total_words, index

def build_index_results(total_words, index):
    results = []
    unique_words = sorted(set(total_words), key=str.casefold)

    for word in unique_words:
        book_pages = defaultdict(list)
        for (book, page), words_on_page in index.items():
            if word in words_on_page:
                book_pages[book].append(page)

        total_refs = sum(len(p) for p in book_pages.values())
        if total_refs == 0 or total_refs >= 15:
            continue

        formatted = " | ".join(
            f"{book}({', '.join(str(p) for p in sorted(pages))})"
            for book, pages in sorted(book_pages.items())
        )
        results.append((word, formatted))

    return results

def write_txt(results, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for word, ref_string in results:
            f.write(f"{word}: {ref_string}\n")
    print(f"[✔] Written TXT index to {output_file}")

def write_csv(results, output_file):
    with open(output_file, "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["word", "page_refs"])
        for word, ref_string in results:
            writer.writerow([word, ref_string])
    print(f"[✔] Written CSV index to {output_file}")

def main():
    args = parse_arguments()
    default_ext = ".csv" if args.csv else ".index.txt"
    output_file = args.output_file or args.input_file.replace(".pdf", "") + default_ext

    common_words = fetch_common_words(args.wordlist)
    pages = extract_book_pages(args.input_file, args.book_starts, args.skip_first, args.skip_last)

    total_words, index = index_words(pages, common_words)
    print(f"[*] Found {len(set(total_words))} unique words across {len(pages)} indexed pages.")

    results = build_index_results(total_words, index)
    print(f"[*] Writing {len(results)} index entries to: {output_file}")

    if args.csv:
        write_csv(results, output_file)
    else:
        write_txt(results, output_file)

if __name__ == "__main__":
    main()
