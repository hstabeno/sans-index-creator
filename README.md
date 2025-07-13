# SANS PDF Index Generator

This script generates a keyword index from a SANS course PDF, grouping page numbers by book. It supports:

- Multiple books in a single PDF
- Skipping unnumbered front and back pages
- Custom wordlist support
- Clean output as `.txt` or `.csv`
- UTF-8-safe parsing and non-printable character removal

---

## 🚀 Features

- ✅ Real **Book(Page)** format like:  
  `kerberos: 1(10, 22, 33) | 2(8, 14)`

- ✅ Supports SANS PDFs with multiple books merged together

- ✅ Allows skipping:
  - Unnumbered **front pages** (`--skip-first`)
  - Extra **appendices or blank pages** (`--skip-last`)

- ✅ Automatically excludes common English words (or your own list)

- ✅ Outputs `.txt` or `.csv`

---

## 📦 Requirements

- Python 3.8+
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF)

```bash
pip install pymupdf requests
```

---

## 🛠️ Usage

```bash
python sans_pdf_indexer.py -i <PDF_FILE> [options]
```

### 🔑 Required Flags

| Flag | Description |
|------|-------------|
| `-i` / `--input-file` | Path to the SANS course PDF |
| `--book-starts` | List of 1-based page numbers where each book starts |
| `--skip-first` | Pages to skip at the beginning of each book |
| `--skip-last` | Pages to skip at the end of each book |

> ⚠️ All lists must be the same length (one value per book).

---

### 🔧 Optional Flags

| Flag | Description |
|------|-------------|
| `-o` / `--output-file` | Output filename (defaults to input name + `.index.txt` or `.csv`) |
| `--csv` | Output in `.csv` format instead of `.txt` |
| `--wordlist` | Path to a `.txt` file of common words to ignore |

---

## 📄 Example

```bash
python sans_pdf_indexer.py -i sans_book.pdf --csv \
  --book-starts 1 168 299 487 620 770 1180 \
  --skip-first 2 2 2 2 0 2 2 \
  --skip-last 0 0 0 0 20 0 0 \
  --wordlist custom_words.txt
```

- `sans_book.pdf` is the full SANS PDF
- Skips front/back matter as needed
- Outputs a clean `sans_book.csv` index file

---

## 🧠 Custom Wordlist Format

Just a plain `.txt` file with one word per line:

```
kerberos
splunk
token
...
```

---

## 📚 Output Examples

### `.txt` Format:
```
kerberos: 1(23, 35) | 2(19, 98) | 4(1)
volatility: 3(5, 17) | 5(12)
```

### `.csv` Format:
```
word,page_refs
kerberos,"1(23, 35) | 2(19, 98)"
volatility,"3(5, 17) | 5(12)"
```

---

## 🛡️ License

MIT License
