import fitz  # PyMuPDF
import os
import re


def extract_required_information_from_all_pdfs(directory_path):
    all_extracted_info = {}

    # Loop through all files in the specified directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory_path, filename)
            extracted_info = extract_required_information(pdf_path)
            all_extracted_info[filename] = extracted_info

    return all_extracted_info


def extract_required_information(pdf_path):
    tracking_number = None
    tax_period = None
    ssn = None
    font_flag_20_texts = []
    key_value_pairs = {}

    # Regular expressions to match patterns
    tracking_number_pattern = re.compile(r'Tracking Number[:\s]*([\d]+)')
    tax_period_pattern = re.compile(r'Tax Period[:\s]*([\d-]+)|TAX PERIOD[:\s]*([A-Za-z\s\d.,]+)|Tax Period Requested[:\s]*([A-Za-z\s\d.,]+)')
    ssn_pattern = re.compile(r'SSN Provided[:\s]*([\d-]+)|TAXPAYER IDENTIFICATION NUMBER[:\s]*([\d-]+|XXX-XX-\d{4})')
    key_value_pattern = re.compile(r'([A-Za-z\s]+):\s*([A-Za-z0-9\s\-.,]+)')

    # To hold concatenated text
    accumulated_text = ""

    # Open the PDF
    with fitz.open(pdf_path) as pdf:
        # Iterate through each page
        for page_num in range(pdf.page_count):
            page = pdf.load_page(page_num)
            blocks = page.get_text("dict")["blocks"]

            # Iterate through each block to find the required information
            for block in blocks:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text")
                        accumulated_text += text + " "

                        # Collect text with Font Flags equal to 20
                        if span.get("flags") == 20:
                            font_flag_20_texts.append(text)

    # Now search the accumulated text for patterns
    tracking_number_match = tracking_number_pattern.search(accumulated_text)
    if tracking_number_match:
        tracking_number = tracking_number_match.group(1)

    tax_period_match = tax_period_pattern.search(accumulated_text)
    if tax_period_match:
        tax_period_value = tax_period_match.group(1) or tax_period_match.group(2) or tax_period_match.group(3)
        if tax_period_value:
            # Format tax period if it's missing a day (e.g., "December, 2019" -> "December 1, 2019")
            if re.match(r'^[A-Za-z]+, \d{4}$', tax_period_value):
                tax_period = re.sub(r',', ' 1,', tax_period_value)
            else:
                tax_period = tax_period_value

    ssn_match = ssn_pattern.search(accumulated_text)
    if ssn_match:
        ssn = ssn_match.group(1) if ssn_match.group(1) else ssn_match.group(2)

    # Extract all key-value pairs
    for match in key_value_pattern.finditer(accumulated_text):
        key = match.group(1).strip()
        value = match.group(2).strip()
        key_value_pairs[key] = value

        # Specifically handle TAXPAYER IDENTIFICATION NUMBER to set SSN
        if key.lower() == "taxpayer identification number" and not ssn:
            ssn = value

    # Clean up tax_period if it includes extra information like SSN
    if tax_period and "TAXPAYER IDENTIFICATION NUMBER" in tax_period:
        tax_period_parts = tax_period.split("TAXPAYER IDENTIFICATION NUMBER")
        tax_period = tax_period_parts[0].strip()
        if len(tax_period_parts) > 1 and not ssn:
            ssn = tax_period_parts[1].strip()

    return {
        "Tracking Number": tracking_number,
        "Tax Period": tax_period,
        "SSN": ssn,
        "Font Flag 20 Text": font_flag_20_texts,
        "Key-Value Pairs": key_value_pairs,
    }


# Define the path to the 'data' folder
data_folder_path = "data"

# Extract required information from all PDFs in the 'data' folder
extracted_values = extract_required_information_from_all_pdfs(data_folder_path)

# Print the results
for filename, extracted_info in extracted_values.items():
    print(f"Extracted Information from {filename}:")

    if extracted_info["Tracking Number"]:
        print(f"  Tracking Number: {extracted_info['Tracking Number']}")
    else:
        print(f"  Tracking Number: Not found")

    if extracted_info["Tax Period"]:
        print(f"  Tax Period: {extracted_info['Tax Period']}")
    else:
        print(f"  Tax Period: Not found")

    if extracted_info["SSN"]:
        print(f"  SSN: {extracted_info['SSN']}")
    else:
        print(f"  SSN: Not found")

    if extracted_info["Font Flag 20 Text"]:
        print(f"  Font Flag 20 Texts:")
        for value in extracted_info["Font Flag 20 Text"]:
            print(f"    {value}")
    else:
        print(f"  Font Flag 20 Texts: None found")

    if extracted_info["Key-Value Pairs"]:
        print(f"  Key-Value Pairs:")
        for key, value in extracted_info["Key-Value Pairs"].items():
            print(f"    {key}: {value}")
    else:
        print(f"  Key-Value Pairs: None found")

    print("\n")
