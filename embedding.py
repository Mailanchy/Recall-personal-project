# from dotenv import load_dotenv
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
import hashlib
from pathlib import Path
import crud

# load_dotenv() 

# Get hash of file content
def get_hash(file_path):
    with open (file_path, 'rb') as file:
        content = file.read()
    hash_val = hashlib.sha256(content)
    file_hash = hash_val.hexdigest()
    return file_hash

# Extract text from a file
def extract_text(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Chunk the extracted text
def chunk_text(text):
    # Split the text based on Markdown headers
    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[('#','Header 1'),('##','Header 2'),('###','Header 3')],)
    formatted_output = header_splitter.split_text(text)
    
    # Further split the text into smaller meaningful chunks. There is a chance that the text under each header is too long, so we will split it into smaller chunks.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(formatted_output)
    return chunks

if __name__ == "__main__":
    file_path = '//Users/husaimamailanchytk/Documents/Mailu/Recall/test.md'
    file_name = Path(file_path).name # Get the name of the file
    file_hash = get_hash(file_path)
    existing_material = crud.get_material_by_hash(file_hash)
    # existing_material
    if not existing_material: #Check whether the material already exists or not
        material_id = crud.add_material(file_name,file_hash) 
        doc_text = extract_text(file_path)
        chunks = chunk_text(doc_text)
        crud.add_chunks(chunks,material_id) 




