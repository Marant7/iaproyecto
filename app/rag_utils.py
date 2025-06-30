from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
import os

def buscar_contexto_pinecone(query, k=3):
    """Busca contexto relevante en Pinecone usando embeddings de OpenAI."""
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = "ofertas-laborales2"
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    pc = Pinecone(api_key=api_key)
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings, pinecone_api_key=api_key)
    docs = vectorstore.similarity_search(query, k=k)
    contexto = "\n\n".join([d.page_content for d in docs])
    return contexto
