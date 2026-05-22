import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "banking_docs"


def get_embeddings():
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    from langchain.embeddings.base import Embeddings
    
    class ChromaDefaultEmbeddings(Embeddings):
        def __init__(self):
            self.ef = DefaultEmbeddingFunction()
        def embed_documents(self, texts):
            return self.ef(texts)
        def embed_query(self, text):
            return self.ef([text])[0]
    
    return ChromaDefaultEmbeddings()
def get_llm():
    if LLM_PROVIDER == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )
    elif LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
    elif LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
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


def get_rag_response(query, chat_history=[]):
    from langchain_chroma import Chroma
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains import create_retrieval_chain
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    
    vectorstore = Chroma(collection_name=COLLECTION_NAME, embedding_function=get_embeddings(), persist_directory=CHROMA_DIR)
    
    # Contextual Memory Fix: Safely format chat history and update query context
    formatted_history = []
    last_topic = ""
    
    for msg in chat_history:
        if isinstance(msg, dict):
            role = msg.get("role", "human")
            content = msg.get("content", "")
            if role in ["user", "human"]:
                formatted_history.append(("human", content))
                # Identify if user mentioned a specific product earlier
                for topic in ["personal loan", "home loan", "credit card", "savings", "fixed deposit"]:
                    if topic in content.lower():
                        last_topic = topic
            else:
                formatted_history.append(("ai", content))
        else:
            formatted_history.append(msg)
            
    # If the user asks a follow-up like "for it", inject the last discussed topic
    refined_query = query
    if any(keyword in query.lower() for keyword in ["for it", "interest rate", "charges", "documents"]) and last_topic:
        refined_query = f"{query} regarding {last_topic}"
        print(f"Refined Query for Database: {refined_query}") # Debugging log for Render
        
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    system_prompt = "You are an expert banking assistant. Answer the user's question using ONLY the provided context. If you don't know the answer, say that you don't have this information.\n\nContext:\n{context}"
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    
    llm = get_llm()
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    response = rag_chain.invoke({"input": refined_query, "chat_history": formatted_history})
    sources = list(set([doc.metadata.get("source", "Unknown") for doc in response.get("context", [])]))
    
    return response["answer"], sources