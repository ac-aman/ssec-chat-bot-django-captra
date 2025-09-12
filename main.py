# import os
# import sqlite3
# import json
# import django
# import pandas as pd

# from dotenv import load_dotenv
# from langchain.schema import Document
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain.chains import ConversationalRetrievalChain
# from langchain_core.messages import HumanMessage, AIMessage

# # NEW: Correct import for Chroma (not deprecated)
# from langchain_chroma import Chroma

# # ----------------------------
# # Load environment variables & Django
# # ----------------------------
# load_dotenv()
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
# django.setup()

# # ----------------------------
# # Load faculty data from SQLite
# # ----------------------------
# conn = sqlite3.connect("db.sqlite3")
# df = pd.read_sql_query("SELECT * FROM faculty_faculty;", conn)
# conn.close()

# # Create Documents for RAG
# docs = []
# for _, row in df.iterrows():
#     text = f"""
#     Name: {row['name']}
#     Designation: {row['designation']}
#     Department: {row['department']}
#     Room No: {row['room_no']}
#     Expertise: {row['expertise']}
#     Experience: {row['years_of_experience']}
#     Qualifications: {row['qualifications']}
#     Email: {row['contact_email']}
#     Phone: {row['contact_phone']}
#     Extra Activities: {row['extra_curriculum']}
#     Description: {row['description']}
#     """
#     docs.append(Document(page_content=text))

# # ----------------------------
# # Split into chunks
# # ----------------------------
# splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
# chunks = splitter.split_documents(docs)

# # ----------------------------
# # Embeddings + Chroma Vector Store
# # ----------------------------
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# vector_store = Chroma(
#     collection_name="faculty_collection",
#     embedding_function=embeddings,
#     persist_directory="my_chroma_db",  # persisted locally
# )

# # Add documents if empty
# if len(vector_store.get()["ids"]) == 0:
#     vector_store.add_documents(chunks)
#     vector_store.persist()

# # ----------------------------
# # Human-like Chat Prompt
# # ----------------------------
# prompt_template = """
# You are Santilal Shah Bot (SSec Bot), a friendly college assistant.
# Answer the user's question based on the context provided. Keep it simple, clear, and friendly.
# If you don't know, politely say you don't know. Keep the answer concise but natural.

# Context: {context}
# Question: {question}
# Answer:
# """

# prompt = ChatPromptTemplate.from_template(prompt_template)

# # ----------------------------
# # LLM + Retriever + Conversational Retrieval Chain
# # ----------------------------
# llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
# retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# qa_chain = ConversationalRetrievalChain.from_llm(
#     llm=llm,
#     retriever=retriever,
#     combine_docs_chain_kwargs={"prompt": prompt},
#     return_source_documents=False,
# )

# # ----------------------------
# # Chat History Persistence (JSON with HumanMessage/AIMessage)
# # ----------------------------
# HISTORY_FILE = "chat_history.json"


# def save_history(history, file_path):
#     """Save history in JSON (role + content)."""
#     serializable = []
#     for msg in history:
#         role = "human" if isinstance(msg, HumanMessage) else "ai"
#         serializable.append({"role": role, "content": msg.content})
#     with open(file_path, "w") as f:
#         json.dump(serializable, f, indent=2)


# def load_history(file_path):
#     """Load history from JSON into HumanMessage/AIMessage list."""
#     if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
#         return []
#     try:
#         with open(file_path, "r") as f:
#             data = json.load(f)
#         history = []
#         for msg in data:
#             if msg["role"] == "human":
#                 history.append(HumanMessage(content=msg["content"]))
#             else:
#                 history.append(AIMessage(content=msg["content"]))
#         return history
#     except json.JSONDecodeError:
#         print("⚠ Corrupted history file. Starting fresh.")
#         return []


# chat_history = load_history(HISTORY_FILE)

# # ----------------------------
# # CLI Chatbot Loop
# # ----------------------------
# print("🤖 Santilal Shah Bot (SSec Bot) - Your college assistant")
# print("Type 'exit' to quit.\n")

# while True:
#     query = input("You: ")
#     if query.lower() in ["exit", "quit"]:
#         print("SSec Bot: Bye! Take care 👋")
#         save_history(chat_history, HISTORY_FILE)
#         break

#     result = qa_chain.invoke({"question": query, "chat_history": chat_history})

#     response = result["answer"]

#     print("SSec Bot:", response.strip(), "\n")

#     # Append to history correctly
#     chat_history.append(HumanMessage(content=query))
#     chat_history.append(AIMessage(content=response))


"""
Example: Gemini LLM with SQLite + Internet Search Agent
- Uses Gemini as the LLM
- Connects to existing db.sqlite3
- Lets you ask natural questions
- Agent decides whether to query DB or search internet
"""

import os
from sqlalchemy import create_engine
from langchain_google_genai import GoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    QuerySQLDataBaseTool,
    InfoSQLDatabaseTool,
)
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import initialize_agent

# --- Step 1: API Key ---
os.environ["GOOGLE_API_KEY"] = "AIzaSyCNvznfcm7fnSHjFgQMmH60MYjXHMyS_RI"

# --- Step 2: Connect to your existing SQLite DB ---
engine = create_engine("sqlite:///db.sqlite3")
db = SQLDatabase(engine)

# --- Step 3: Gemini LLM ---
llm = GoogleGenerativeAI(model="gemini-2.5-flash")

# --- Step 4: SQL Tools ---
sql_info_tool = InfoSQLDatabaseTool(db=db)  # shows schema
sql_query_tool = QuerySQLDataBaseTool(db=db)  # runs queries

# --- Step 5: Internet Search Tool ---
search_tool = DuckDuckGoSearchRun()

# --- Step 6: Create an Agent ---
agent = initialize_agent(
    tools=[sql_info_tool, sql_query_tool, search_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
    handle_parsing_errors=True,
)

# --- Step 7: Ask Questions ---
questions = [
    "Show me all employees in Engineering.",  # should use SQLite
    "What is the average salary of employees?",  # should use SQLite
    "What is acpital of India",  # should use internet
]

for q in questions:
    print(f"\n❓ Question: {q}")
    answer = agent.invoke({"input": q})
    print(f"✅ Answer: {answer['output']}")
