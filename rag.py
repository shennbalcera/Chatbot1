# app.py

# --------------------------
# Patch sqlite3 with pysqlite3 (for Chroma)
# --------------------------
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import streamlit as st
import openai as _openai
import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from typing import List
import os
import textwrap

# --------------------------
# Azure OpenAI Configuration (use your values)
# --------------------------
_openai.api_type = "azure"
_openai.api_base = "https://jvtay-mff428jo-eastus2.openai.azure.com/"
_openai.api_version = "2025-01-01-preview"
_openai.api_key = "FOObvelUv1Ubbw0ZlEb3NPCBYDbdXWbLhzyckQAA9cP3Ofhgi8KWJQQJ99BIACHYHv6XJ3w3AAAAACOGoHUz"  

AZURE_DEPLOYMENT_NAME = "gpt-35-turbo"  
openai = _openai  # shorthand

# --------------------------
# Streamlit UI
# --------------------------
st.set_page_config(page_title="TESDA FAQ RAG Chatbot", layout="wide")
st.title("📚 TESDA Customer Support — RAG Chatbot (Streamlit + Azure OpenAI)")

cols = st.columns([3, 1])
left, right = cols

with right:
    st.header("Knowledge Base")
    st.markdown("Scrape TESDA FAQ pages, embed Q/A, and store them in Chroma.")
    if st.button("(Re)build KB from TESDA FAQ pages"):
        st.session_state.rebuild = True

# --------------------------
# Chroma + Embedding setup
# --------------------------
@st.cache_resource
def get_chroma_client():
    return chromadb.Client(
        Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        )
    )

client = get_chroma_client()

@st.cache_resource
def get_sentence_transformer():
    return SentenceTransformer("all-MiniLM-L6-v2")

embedder = get_sentence_transformer()
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2",
    model=embedder
)

COLLECTION_NAME = "tesda_faqs"

def ensure_collection():
    try:
        return client.get_collection(name=COLLECTION_NAME)
    except Exception:
        return client.create_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)

collection = ensure_collection()

# --------------------------
# TESDA Pages (seed URLs)
# --------------------------
TESDA_PAGES = [
    "https://www.tesda.gov.ph/About/Tesda/127",    # Assessment & Certification FAQs
    "https://e-tesda.gov.ph/local/staticpage/view.php?page=FAQ",  # e-TESDA
    "https://www.tesda.gov.ph/About/TESDA/25687",  # Scholarship FAQs
    "https://knowledgebase-bsrs.tesda.gov.ph/"     # BSRS Knowledgebase
]

# --------------------------
# Scraping helpers
# --------------------------
def fetch_text_from_url(url: str) -> str:
    try:
        r = requests.get(url, timeout=12)
        r.raise_for_status()
    except Exception as e:
        st.warning(f"Failed to fetch {url}: {e}")
        return ""
    soup = BeautifulSoup(r.text, "html.parser")

    texts = []
    for qa in soup.select("div.faq, .faq, .faq-item, .question, .faq_list, .panel, .article"):
        texts.append(qa.get_text(separator="\n").strip())

    if not texts:
        main = soup.find("main") or soup.find("article") or soup.find("body")
        texts.append(main.get_text(separator="\n").strip() if main else soup.get_text(separator="\n").strip())

    return "\n\n".join(texts)

def chunk_text(text: str, max_chars=800) -> List[str]:
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks, cur = [], ""
    for p in paragraphs:
        if len(cur) + len(p) + 1 > max_chars:
            chunks.append(cur.strip())
            cur = p
        else:
            cur += "\n" + p
    if cur.strip():
        chunks.append(cur.strip())
    return chunks

def build_kb_from_seed(pages: List[str]):
    col = ensure_collection()
    try:
        col.delete()
        col = client.create_collection(name=COLLECTION_NAME, embedding_function=embedding_fn)
    except Exception:
        col = ensure_collection()

    docs, metas, ids = [], [], []
    for url in pages:
        st.info(f"Fetching {url}")
        text = fetch_text_from_url(url)
        if not text:
            continue
        chunks = chunk_text(text)
        for i, c in enumerate(chunks):
            docs.append(c)
            metas.append({"source": url, "chunk": i})
            ids.append(f"{os.path.basename(url)}_{i}")

    if docs:
        col.add(documents=docs, metadatas=metas, ids=ids)
        client.persist()
        st.success(f"Added {len(docs)} document chunks to Chroma.")
    else:
        st.warning("No documents added.")

if st.session_state.get("rebuild", False):
    build_kb_from_seed(TESDA_PAGES)
    st.session_state.rebuild = False

# --------------------------
# Retrieval + Generation
# --------------------------
def retrieve_docs(query: str, k=4):
    col = ensure_collection()
    results = col.query(query_texts=[query], n_results=k, include=["documents", "metadatas"])
    combined = []
    if results and "documents" in results:
        for d, m in zip(results["documents"][0], results["metadatas"][0]):
            combined.append({"text": d, "source": m.get("source", "unknown")})
    return combined

def build_prompt(question: str, retrieved: List[dict]) -> str:
    context = "\n\n".join([f"Source: {r['source']}\n{r['text']}\n---" for r in retrieved]) or "No context."
    return f"""You are a TESDA support assistant. Use the context to answer.

Context:
{context}

User question:
{question}

Answer:"""

def azure_chat_completion(prompt: str, max_tokens=400) -> str:
    resp = openai.ChatCompletion.create(
        engine=AZURE_DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are a TESDA FAQ assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=max_tokens,
    )
    return resp["choices"][0]["message"]["content"]

# --------------------------
# User Interaction
# --------------------------
st.markdown("### Ask about TESDA (training, assessment, scholarships, etc.)")
q = st.text_input("Your question")
if st.button("Answer"):
    if not q.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching knowledge base..."):
            retrieved = retrieve_docs(q, k=4)
        with st.expander("Retrieved snippets"):
            for i, r in enumerate(retrieved):
                st.markdown(f"**Snippet {i+1} (Source: {r['source']})**")
                st.write(textwrap.shorten(r["text"], width=500, placeholder="..."))
        prompt = build_prompt(q, retrieved)
        with st.spinner("Calling Azure OpenAI..."):
            try:
                answer = azure_chat_completion(prompt)
                st.markdown("### ✅ Answer")
                st.write(answer)
            except Exception as e:
                st.error(f"Azure OpenAI call failed: {e}")
