from fastapi import FastAPI
import chromadb
from openai import AzureOpenAI
import os
from dotenv import load_dotenv  # Import the dotenv package

# Load environment variables from the .env file
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="faq_embeddings")

# Initialize OpenAI API
client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), 
    api_version="2024-02-01",
    azure_endpoint="https://ai-proxy.lab.epam.com"
)

embedding_model = "text-embedding-ada-002"
chat_model = "gpt-35-turbo"

# Function to get embeddings
def get_embedding(text):
    response = client.embeddings.create(
        model=embedding_model,
        input=text
    )
    return response.data[0].embedding

# Function to query ChromaDB
def search_faq(query, top_k=3):
    query_embedding = get_embedding(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

    if results and results["metadatas"]:
        faqs = [item['text'] for item in results['metadatas'][0]]
        return faqs if faqs else ["No relevant FAQ found."]
    return ["No relevant FAQ found."]

# Function to generate follow-up answers
def generate_answer(f_query, context):
    response = client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"FAQ Context: {context}\nUser Query: {f_query}"}
        ]
    )
    return response.choices[0].message.content

# API Endpoint: Retrieve relevant FAQs
@app.get("/search/")
async def search(query: str):
    faqs = search_faq(query)
    return {"faqs": faqs}

# API Endpoint: Answer user follow-up question
@app.get("/ask/")
async def ask(query: str, f_query: str):
    faqs = search_faq(query)
    context = faqs[0] if faqs else "No relevant FAQ found."
    answer = generate_answer(f_query, context)
    return {"answer": answer}
