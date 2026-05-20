import os
from dotenv import load_dotenv

load_dotenv()

# Must match what you set in rag_pipeline.py
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "gemini")
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "banking_docs"


def get_embeddings():
    if EMBEDDING_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY")
        )
    elif EMBEDDING_PROVIDER == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        return GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
    else:  # huggingface — FREE!
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )


def ingest_document(file_path: str) -> int:
    """Load, chunk, embed and store a document. Returns number of chunks."""
    from langchain_chroma import Chroma
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        from langchain_community.document_loaders import TextLoader
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {ext}. Only PDF and TXT supported.")

    documents = loader.load()

    for doc in documents:
        doc.metadata["source"] = os.path.basename(file_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(documents)

    embeddings = get_embeddings()
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )
    vectorstore.add_documents(chunks)

    print(f"Ingested {len(chunks)} chunks from {file_path}")
    return len(chunks)


def ingest_all_from_folder(folder: str = "./data"):
    """Ingest all PDFs and TXTs from a folder."""
    total = 0
    for filename in os.listdir(folder):
        if filename.endswith((".pdf", ".txt")):
            path = os.path.join(folder, filename)
            count = ingest_document(path)
            total += count
    print(f"Total chunks ingested: {total}")
    return total


if __name__ == "__main__":
    ingest_all_from_folder("./data")