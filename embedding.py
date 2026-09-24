from dotenv import load_dotenv
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

load_dotenv()  

# Extract text from a file
def extract_text(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Chunk the extracted text
def chunk_text(text):
    # Split the text based on Markdown headers
    header_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[('#','Header 1'),('##','Header 2'),('###','Header 3')],)
    formatted_output = header_splitter.split_text(text)
    print(formatted_output,'\n\n')
    
    # Further split the text into smaller meaningful chunks. There is a chance that the text under each header is too long, so we will split it into smaller chunks.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=9, chunk_overlap=5)
    chunks = text_splitter.split_documents(formatted_output)

    return chunks

doc_text = extract_text("//Users/husaimamailanchytk/Documents/Mailu/Recall/notes.md")
chunks = chunk_text(doc_text)
print(chunks)


