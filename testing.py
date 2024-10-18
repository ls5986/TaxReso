import fitz  # PyMuPDF
import os

def extract_bold_text_from_all_pdfs(directory_path):
    all_bold_texts = {}

    # Loop through all files in the specified directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory_path, filename)
            bold_texts = extract_bold_text(pdf_path)
            all_bold_texts[filename] = bold_texts

    return all_bold_texts

def extract_bold_text(pdf_path):
    bold_texts = []

    # Open the PDF
    with fitz.open(pdf_path) as pdf:
        # Iterate through each page
        for page_num in range(pdf.page_count):
            page = pdf.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]

            # Iterate through each block to find spans with bold fonts
            for block in blocks:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        # Debugging output to understand span properties
                        print(f"Text: '{span.get('text')}', Font Flags: {span.get('flags')}")

                        # Check if the text is bold
                        if span.get("flags") & 2:  # Flag 2 usually indicates bold text
                            bold_texts.append(span.get("text"))

    return bold_texts

# Define the path to the 'data' folder
data_folder_path = "data"

# Extract bold text from all PDFs in the 'data' folder
bold_text_values = extract_bold_text_from_all_pdfs(data_folder_path)

# Print the results
for filename, bold_texts in bold_text_values.items():
    print(f"Bolded Values Found in {filename}:")
    if not bold_texts:
        print("No bolded text found.")
    else:
        for value in bold_texts:
            print(value)
    print("\n")
