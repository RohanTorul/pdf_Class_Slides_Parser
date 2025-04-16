import pdfplumber
import csv
import re
import argparse
from collections import defaultdict

def is_black_or_white(rgb):
    return rgb in [(0,),(0, 0, 0), (1, 1, 1)]

def is_url(text):
    return re.match(r'https?://\S+|www\.\S+', text)

def write_csv(filename, flashcards):
    with open(filename, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Question", "Answer"])
        writer.writerows(flashcards)

def write_anki_txt(filename, flashcards):
    with open(filename, "w", encoding="utf-8") as txtfile:
        for q, a in flashcards:
            txtfile.write(f"{q}\t{a}\n")

def write_summary(filename, titles_and_sections, key_terms, links, ignored_pages):
    with open(filename, "w", encoding="utf-8") as txtfile:
        txtfile.write("Titles / Subsections:\n")
        for title, page_num in titles_and_sections:
            txtfile.write(f"[Page {page_num}] {title}\n")
        txtfile.write("\n")

        txtfile.write("Key Terms (Bold, Italic, Underline, Colored Phrases):\n")
        for phrase, pages in key_terms.items():
            pages_clean = sorted(set(int(p) for p in pages))
            txtfile.write(f"{phrase} [Pages {', '.join(map(str, pages_clean))}]\n")
        txtfile.write("\n")

        txtfile.write("Links:\n")
        for link, pages in links.items():
            pages_clean = sorted(set(int(p) for p in pages))
            txtfile.write(f"{link} [Pages {', '.join(map(str, pages_clean))}]\n")
        txtfile.write("\n")

        txtfile.write("Ignored Pages:\n")
        txtfile.write(f"{', '.join(map(str, sorted(ignored_pages)))}\n")
        txtfile.write("\n")

def load_ignore_patterns(file_path):
    if not file_path:
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return [re.compile(line.strip()) for line in f if line.strip()]

def is_ignored(phrase, patterns):
    return any(p.fullmatch(phrase) for p in patterns)

def parse_ignore_pages_file(file_path):
    pages = set()
    if not file_path:
        return pages
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if '-' in line:
                start, end = map(int, line.split('-'))
                pages.update(range(start, end + 1))
            else:
                pages.add(int(line))
    return pages

# CLI Argument Parser
parser = argparse.ArgumentParser(description="PDF to Flashcards & Key Terms extractor")
parser.add_argument("pdf_path", help="Path to the PDF file")
parser.add_argument("--csv", default="flashcards.csv", help="Output CSV file")
parser.add_argument("--anki", default="flashcards_for_anki.txt", help="Output Anki text file")
parser.add_argument("--summary", default="pdf_summary.txt", help="Output text summary file")
parser.add_argument("--ignore", help="Path to text file with regex patterns for phrases to ignore")
parser.add_argument("--ignore-pages-file", help="Path to text file with pages/ranges to ignore")
args = parser.parse_args()

ignore_patterns = load_ignore_patterns(args.ignore)
ignore_pages = parse_ignore_pages_file(args.ignore_pages_file)

flashcards = []
titles_and_sections = []
key_terms = defaultdict(list)
links = defaultdict(list)

bullet_point_pattern  = re.compile(r'[\●](.*)\s*')


with pdfplumber.open(args.pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
        if page_num in ignore_pages:
            continue

        words = page.extract_words(use_text_flow=True, extra_attrs=["fontname", "size", "non_stroking_color"])

        phrases = []
        if words:
            current_phrase = []
            last_style = None
            last_top = words[0]['top']

            for word in words:
                text = word['text']
                font = word['fontname']
                color = word['non_stroking_color']
                size = word['size']
                style = (font, color, size)
                top = word['top']

                if (last_style is not None and style != last_style) or abs(top - last_top) > 3:
                    phrases.append((current_phrase, last_style, last_top))
                    current_phrase = []
                current_phrase.append(word)
                last_style = style
                last_top = top

            if current_phrase:
                phrases.append((current_phrase, last_style, last_top))

        for phrase_words, style, top in phrases:
            phrase_text = " ".join(w['text'] for w in phrase_words).strip()
            if not phrase_text or is_ignored(phrase_text, ignore_patterns):
                continue

            font, color, size = style
            color_tuple = tuple(color)

            if size >= 32:
                titles_and_sections.append((phrase_text, page_num))

            if not is_black_or_white(color_tuple):
                key_terms[phrase_text].append(page_num)
            elif any(k in font for k in ["Bold", "Italic", "Underline"]):
                key_terms[phrase_text].append(page_num)

            if is_url(phrase_text):
                links[phrase_text].append(page_num)

        lines = page.extract_text().split('\n') if page.extract_text() else []
        if lines:
            lines = [line.strip() for line in lines if line.strip() and not is_ignored(line.strip(), ignore_patterns)]
            if lines:
                question = lines[0]
                current_answer = ""
                for line in lines[1:]:
                    if bullet_point_pattern.match(line):
                        if current_answer:
                            flashcards.append((f"{question} (Page {page_num})", current_answer.replace("●", "").strip()))
                        current_answer = line  # start a new point
                    else:
                        current_answer += " " + line  # same point, continue

                if current_answer:
                    flashcards.append((f"{question} (Page {page_num})", current_answer.strip()))

write_csv(args.csv, flashcards)
write_anki_txt(args.anki, flashcards)
write_summary(args.summary, titles_and_sections, key_terms, links, ignore_pages)

print(f"👾 Done!\n- Flashcards: {args.csv}, {args.anki}\n- Summary: {args.summary}")
