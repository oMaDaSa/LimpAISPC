import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from supabase import create_client

load_dotenv(".env")

def ingest():
    documents = TextLoader("src/database/lei_superendividamento.txt", encoding="utf-8").load()

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    SupabaseVectorStore.from_documents(
        docs, 
        embeddings, 
        client=supabase, 
        table_name="documents"
    )

    print("Documentos inseridos")

if __name__ == "__main__":
    ingest()