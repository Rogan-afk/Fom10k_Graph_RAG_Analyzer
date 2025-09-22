import fitz  # PyMuPDF
import re
import os

os.makedirs("processed_texts", exist_ok=True)

def process_pdf_to_text(pdf_path: str) -> (str, str):
    """
    Intelligently extracts key sections (Business, Risk Factors, MD&A) from a 10-K PDF,
    saves the result as a .txt file, and returns the extracted text.
    """
    target_sections = {
        "item_1": r"Item\s+1\.\s+Business",
        "item_1a": r"Item\s+1A\.\s+Risk\s+Factors",
        "item_7": r"Item\s+7\.\s+Management’s\s+Discussion\s+and\s+Analysis",
        "end_section": r"Item\s+(1B|2|7A|8)\."
    }
    try:
        doc = fitz.open(pdf_path)
        full_text = "".join(page.get_text() for page in doc)
        doc.close()
        
        if len(full_text.strip()) < 500:
             return None, None

        extracted_content = ""
        for key in ["item_1", "item_1a", "item_7"]:
            start_match = re.search(target_sections[key], full_text, re.IGNORECASE)
            if start_match:
                start_index = start_match.start()
                end_match = re.search(target_sections["end_section"], full_text[start_index + 10:], re.IGNORECASE)
                end_index = (start_index + 10 + end_match.start()) if end_match else len(full_text)
                section_text = full_text[start_index:end_index]
                extracted_content += f"\n\n--- EXTRACTED SECTION: {start_match.group(0)} ---\n\n{section_text}"
        
        if not extracted_content:
            print("Warning: Standard 10-K sections not found. Falling back to first 15 pages.")
            doc = fitz.open(pdf_path)
            extracted_content = "".join(doc.load_page(i).get_text() for i in range(min(len(doc), 15)))
            doc.close()

        txt_filename = f"{os.path.splitext(os.path.basename(pdf_path))[0]}.txt"
        txt_filepath = os.path.join("processed_texts", txt_filename)
        with open(txt_filepath, "w", encoding="utf-8") as f:
            f.write(extracted_content)
        return extracted_content, txt_filepath
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
        return None, None