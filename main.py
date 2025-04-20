import gradio as gr
from pdf_slides_tool_class import PDFFlashcardGenerator

def run_flashcard_tool(pdf_path, csv_path, anki_path, summary_path, ignore_phrases_text, ignore_pages_text):
    ignore_phrases_file = None
    ignore_pages_file = None
    
    with open("temp_ignore_phrases.txt", "w") as f:
        f.write(ignore_phrases_text)
        ignore_phrases_file = "temp_ignore_phrases.txt"

    with open("temp_ignore_pages.txt", "w") as f:
        f.write(ignore_pages_text)
        ignore_pages_file = "temp_ignore_pages.txt"

    generator = PDFFlashcardGenerator(
        pdf_path=pdf_path,
        csv_path=csv_path,
        anki_path=anki_path,
        summary_path=summary_path,
        ignore_phrases_file=ignore_phrases_file,
        ignore_pages_file=ignore_pages_file
    )
    generator.run()
    return " Flashcards generated!"

gr.Interface(
    fn=run_flashcard_tool,
    inputs=[
        gr.File(label="PDF File"),
        gr.Textbox(label="CSV Output Path", value="flashcards.csv"),
        gr.Textbox(label="Anki Output Path", value="flashcards_for_anki.txt"),
        gr.Textbox(label="Summary Output Path", value="summary.txt"),
        gr.Textbox(label="Ignore Phrases (one per line, or leave empty)", lines=4),
        gr.Textbox(label="Ignore Pages (e.g. 1-3, 5, 7)", lines=2),
    ],
    outputs="text"
).launch()
