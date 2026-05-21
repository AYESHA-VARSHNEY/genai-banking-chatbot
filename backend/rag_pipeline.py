import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
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
    else:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )


def get_llm():
    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    elif LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
    elif LLM_PROVIDER == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )
    elif LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model="claude-3-haiku-20240307",
            temperature=0.3,
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")


def load_vectorstore():
    from langchain_chroma import Chroma
    embeddings = get_embeddings()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR
    )


SYSTEM_PROMPT = """You are a helpful and professional banking support assistant for a fintech company.
Your role is to assist customers with queries about:
- Personal and home loans
- Credit cards and CIBIL scores
- Bank account policies and savings accounts
- Fixed deposits and investment options
- Banking FAQs and general financial guidance

Use the provided context to answer questions accurately.
If the answer is not in the context, say: "I don't have specific information about that,
but I recommend contacting our support team at 1800-XXX-XXXX."
Be concise, professional, and friendly.

Context from knowledge base:
{context}

Conversation History:
{chat_history}

Customer Question: {question}

Assistant Answer:"""


def get_rag_response(user_message, history):
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    docs = retriever.invoke(user_message)
    context = "\n\n".join([doc.page_content for doc in docs])
    sources = list(set([doc.metadata.get("source", "Knowledge Base") for doc in docs]))

    chat_history_str = ""
    for msg in history[-6:]:
        role = "Customer" if msg["role"] == "user" else "Assistant"
        chat_history_str += f"{role}: {msg['content']}\n"

    prompt = SYSTEM_PROMPT.format(
        context=context if context.strip() else "No specific documents found.",
        chat_history=chat_history_str if chat_history_str else "No previous conversation.",
        question=user_message
    )

    llm = get_llm()
    from langchain.schema import HumanMessage
    response = llm.invoke([HumanMessage(content=prompt)])

    if hasattr(response, "content"):
        reply = response.content
    else:
        reply = str(response)

    return reply, sources