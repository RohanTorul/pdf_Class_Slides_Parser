import argparse
import tkinter as tk
from tkinter import filedialog, messagebox
from pdf_slides_tool_class import PDFFlashcardGenerator
import os

def run_cli(args):
    gen = PDFFlashcardGenerator(
        pdf_path=args.pdf,
        csv_path=args.csv,
        anki_path=args.anki,
        summary_path=args.summary,
        ignore_phrases_file=args.ignore,
        ignore_pages_file=args.ignore_pages
    )
    gen.run()
    print(f"✔️ Done! Flashcards: {args.csv}, {args.anki}, Summary: {args.summary}")

def run_gui():
    def browse_file(entry):
        file_path = filedialog.askopenfilename()
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)

    def browse_save_file(entry, default_ext):
        file_path = filedialog.asksaveasfilename(defaultextension=default_ext)
        if file_path:
            entry.delete(0, tk.END)
            entry.insert(0, file_path)

    def run_from_gui():
        pdf_path = pdf_entry.get()
        csv_path = csv_entry.get()
        anki_path = anki_entry.get()
        summary_path = summary_entry.get()
        pages_text = pages_text_entry.get()
        pages_file = pages_file_entry.get()
        regex_text = regex_text_entry.get("1.0", tk.END).strip()
        regex_file = regex_file_entry.get()

        if not pdf_path or not csv_path or not anki_path or not summary_path:
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        # Handle pages ignore input
        ignore_pages_path = None
        if pages_file:
            ignore_pages_path = pages_file
        elif pages_text:
            ignore_pages_path = "temp_pages_ignore.txt"
            with open(ignore_pages_path, "w") as f:
                f.write(pages_text.replace(",", "\n").replace("-", "-"))

        # Handle regex ignore input
        ignore_regex_path = None
        if regex_file:
            ignore_regex_path = regex_file
        elif regex_text:
            ignore_regex_path = "temp_regex_ignore.txt"
            with open(ignore_regex_path, "w") as f:
                f.write(regex_text)

        try:
            gen = PDFFlashcardGenerator(
                pdf_path=pdf_path,
                csv_path=csv_path,
                anki_path=anki_path,
                summary_path=summary_path,
                ignore_phrases_file=ignore_regex_path,
                ignore_pages_file=ignore_pages_path
            )
            gen.run()
            messagebox.showinfo("Done", "Flashcard generation completed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            # Clean up temporary files
            if ignore_pages_path == "temp_pages_ignore.txt" and os.path.exists(ignore_pages_path):
                os.remove(ignore_pages_path)
            if ignore_regex_path == "temp_regex_ignore.txt" and os.path.exists(ignore_regex_path):
                os.remove(ignore_regex_path)

    window = tk.Tk()
    window.title("PDF Flashcard Generator")

    # PDF input
    tk.Label(window, text="PDF file:").grid(row=0, column=0, sticky="e")
    pdf_entry = tk.Entry(window, width=50)
    pdf_entry.grid(row=0, column=1)
    tk.Button(window, text="Browse", command=lambda: browse_file(pdf_entry)).grid(row=0, column=2)

    # Output CSV
    tk.Label(window, text="Output CSV:").grid(row=1, column=0, sticky="e")
    csv_entry = tk.Entry(window, width=50)
    csv_entry.grid(row=1, column=1)
    tk.Button(window, text="Save As", command=lambda: browse_save_file(csv_entry, ".csv")).grid(row=1, column=2)

    # Output Anki
    tk.Label(window, text="Output Anki TXT:").grid(row=2, column=0, sticky="e")
    anki_entry = tk.Entry(window, width=50)
    anki_entry.grid(row=2, column=1)
    tk.Button(window, text="Save As", command=lambda: browse_save_file(anki_entry, ".txt")).grid(row=2, column=2)

    # Output Summary
    tk.Label(window, text="Output Summary TXT:").grid(row=3, column=0, sticky="e")
    summary_entry = tk.Entry(window, width=50)
    summary_entry.grid(row=3, column=1)
    tk.Button(window, text="Save As", command=lambda: browse_save_file(summary_entry, ".txt")).grid(row=3, column=2)

    # Ignore Pages: typed
    tk.Label(window, text="Ignore Pages (e.g. 1,3-5,7):").grid(row=4, column=0, sticky="e")
    pages_text_entry = tk.Entry(window, width=50)
    pages_text_entry.grid(row=4, column=1)

    # Ignore Pages: file
    tk.Label(window, text="Or Ignore Pages File:").grid(row=5, column=0, sticky="e")
    pages_file_entry = tk.Entry(window, width=50)
    pages_file_entry.grid(row=5, column=1)
    tk.Button(window, text="Browse", command=lambda: browse_file(pages_file_entry)).grid(row=5, column=2)

    # Ignore Regex: typed
    tk.Label(window, text="Ignore Regex (one per line):").grid(row=6, column=0, sticky="ne")
    regex_text_entry = tk.Text(window, width=38, height=4)
    regex_text_entry.grid(row=6, column=1)

    # Ignore Regex: file
    tk.Label(window, text="Or Ignore Regex File:").grid(row=7, column=0, sticky="e")
    regex_file_entry = tk.Entry(window, width=50)
    regex_file_entry.grid(row=7, column=1)
    tk.Button(window, text="Browse", command=lambda: browse_file(regex_file_entry)).grid(row=7, column=2)

    # Run button
    tk.Button(window, text="Generate Flashcards", command=run_from_gui, bg="lightgreen").grid(row=8, column=1, pady=10)

    window.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF to Flashcards (CLI / GUI)")
    parser.add_argument("--gui", action="store_true", help="Launch GUI mode")
    parser.add_argument("--pdf", help="Path to the PDF file")
    parser.add_argument("--csv", default="flashcards.csv", help="Output CSV file")
    parser.add_argument("--anki", default="flashcards_for_anki.txt", help="Output Anki text file")
    parser.add_argument("--summary", default="pdf_summary.txt", help="Output text summary file")
    parser.add_argument("--ignore", help="Path to text file with regex patterns to ignore")
    parser.add_argument("--ignore-pages", help="Path to text file with pages/ranges to ignore")

    args = parser.parse_args()

    if args.gui:
        run_gui()
    elif args.pdf:
        run_cli(args)
    else:
        parser.print_help()
