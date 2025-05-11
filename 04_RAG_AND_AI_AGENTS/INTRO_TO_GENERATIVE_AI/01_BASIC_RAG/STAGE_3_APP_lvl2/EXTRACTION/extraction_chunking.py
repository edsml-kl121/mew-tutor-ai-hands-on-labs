
from function import save_pdf_content_to_csv, create_chunks_associate_and_save

filename = 'thai_leave_policy'
csv_path = f'{filename}.csv'
pdf_path = f'{filename}.pdf'
new_csv_path = f"{filename}_chunks.csv"
save_pdf_content_to_csv(pdf_path, csv_path)
create_chunks_associate_and_save(csv_path, new_csv_path, filename)