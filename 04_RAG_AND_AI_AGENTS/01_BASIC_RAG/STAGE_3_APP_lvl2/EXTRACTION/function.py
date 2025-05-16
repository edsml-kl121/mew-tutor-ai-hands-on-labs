# def save_pdf_content_to_csv(pdf_path, csv_path):
#     with pdfplumber.open(pdf_path) as pdf, open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
#         # Define the CSV writer and write the header row
#         csvwriter = csv.writer(csvfile)
#         csvwriter.writerow(['title', 'page_number', 'page_content'])
        
#         for page_num, page in enumerate(pdf.pages):
#             # Extract text from the current page
#             text = page.extract_text()
            
#             # In case the page has text content
#             if text:
#                 # Write the page content, page number, and title to the CSV
#                 csvwriter.writerow(['Work Regulations', page_num + 1, text])
                
#         print(f"CSV file saved: {csv_path}")
import pdfplumber
import csv

# Step 1: Extract text from PDF and save it to a CSV
def save_pdf_content_to_csv(pdf_path, csv_path):

    with pdfplumber.open(pdf_path) as pdf, open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['title', 'page_number', 'page_content'])
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                csvwriter.writerow(['Work Regulations', page_num + 1, text])
        print(f"CSV file saved: {csv_path}")

def associate_chunks_with_pages(csv_path, chunks, overlap=200):
    page_starts = {}
    all_text = ''
    current_page = 1
    
    # Load the CSV and create a map of character positions to page numbers
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            page_text = row['page_content'] + ' '  # Including space to separate pages
            start_pos = len(all_text)
            all_text += page_text
            end_pos = len(all_text)
            for pos in range(start_pos, end_pos):
                page_starts[pos] = current_page
            current_page += 1
    
    # Now, determine the starting page number for each chunk
    chunk_page_numbers = []
    for chunk in chunks:
        start_pos = all_text.find(chunk)
        # Default to the last page if not found
        page_number = page_starts.get(start_pos, current_page - 1)  
        chunk_page_numbers.append(page_number)
    
    return chunk_page_numbers


def load_csv_and_create_chunks(csv_path, chunk_size=1000, overlap=200):
    all_text = ''
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            all_text += row['page_content'] + ' '
    
    chunks = []
    start_index = 0
    while start_index < len(all_text):
        if start_index != 0:
            start_index -= overlap
        end_index = start_index + chunk_size
        if end_index > len(all_text):
            end_index = len(all_text)
        
        chunk = all_text[start_index:end_index]
        chunks.append(chunk)
        start_index += chunk_size
        if start_index >= len(all_text):
            break
    
    return chunks

def create_chunks_associate_and_save(csv_path, new_csv_path='leave_policy_chunks.csv', filename="Work Regulations Chunk", chunk_size=900, overlap=100):
    chunks = load_csv_and_create_chunks(csv_path, chunk_size, overlap)
    chunk_page_numbers = associate_chunks_with_pages(csv_path, chunks, overlap)
    
    with open(new_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['title', 'page_number', 'chunk_content'])
        for i, (page_number, chunk) in enumerate(zip(chunk_page_numbers, chunks)):
            # Convert page_number to string
            csvwriter.writerow([filename, str(page_number), chunk])
    print(f"Chunks have been saved to {new_csv_path}")


