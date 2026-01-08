from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from supabase import create_client
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from core.config import LLM_CONFIG, SUPABASE_CONFIG, PROMPT_TEMPLATE

def format_doc(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def ai_response(user_input: str):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    supabase_client = create_client(SUPABASE_CONFIG["url"], SUPABASE_CONFIG["key"])

    vector_store = SupabaseVectorStore(
        client=supabase_client,
        embedding=embeddings,
        table_name="documents",
        query_name="match_documents"
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": 3, "filter": {}})

    llm= ChatGoogleGenerativeAI(**LLM_CONFIG)

    rag_chain = (
        {
            "context": retriever | format_doc,
            "question": RunnablePassthrough()
        }
        | PROMPT_TEMPLATE
        | llm
        | StrOutputParser()
    )
    
    response = rag_chain.invoke(user_input)
    
    return response