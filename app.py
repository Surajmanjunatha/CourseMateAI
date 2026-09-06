import os
import streamlit as st

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import ChatMistralAI

# CONFIGURATION

load_dotenv()

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "book_documents"

st.set_page_config(
    page_title="CourseMate AI",
    page_icon="📚",
    layout="wide"
)

# INITIALIZE SESSION STATE

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "book_name" not in st.session_state:
    st.session_state.book_name = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# MODELS

@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

@st.cache_resource
def get_llm():
    return ChatMistralAI(
        model="ministral-3b-latest"
    )

# CREATE VECTOR DATABASE

def create_vectorstore(pdf_path):
     # 1. Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

     # 2. Split document into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

     # 3. Create embedding model
    embedding_model = get_embedding_model()

     # 4. Create Chroma vector database
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_DIR,
        collection_name=COLLECTION_NAME
    )

    return vectorstore, len(chunks)

# LOAD EXISTING VECTOR DATABASE

def load_vectorstore():
    if not os.path.exists(CHROMA_DIR):
        return None

    try:
        embedding_model = get_embedding_model()

        vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embedding_model,
            collection_name=COLLECTION_NAME
        )

        # Check whether the collection actually contains documents
        count = vectorstore._collection.count()

        if count == 0:
            return None

        return vectorstore

    except Exception as e:
        print(f"Error loading Chroma database: {e}")
        return None


# CLEAR VECTOR DATABASE

def clear_database():
    """
    Clears all documents from the Chroma collection.

    IMPORTANT:
    We do NOT delete the chroma_db directory using shutil.rmtree().
    This avoids Windows WinError 32 caused by Chroma's open files.
    """

    try:
        # If database directory doesn't exist, nothing to clear
        if not os.path.exists(CHROMA_DIR):
            return

        embedding_model = get_embedding_model()

        vectorstore = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embedding_model,
            collection_name=COLLECTION_NAME
        )

        # Get all document IDs
        ids = vectorstore._collection.get()["ids"]

        # Delete all documents
        if ids:
            vectorstore._collection.delete(ids=ids)

        print("Chroma database cleared successfully.")

    except Exception as e:
        print(f"Error clearing Chroma database: {e}")

    finally:
        # Clear Streamlit session state
        st.session_state.vectorstore = None
        st.session_state.book_name = None
        st.session_state.messages = []

# SIDEBAR

with st.sidebar:

    st.title("📚 Book RAG")

    st.write(
        "Upload a PDF book and ask questions "
        "about its contents."
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload your book",
        type=["pdf"]
    )

    if uploaded_file is not None:

        st.write(
            f"Selected: **{uploaded_file.name}**"
        )

        if st.button(
            "📥 Process Book",
            use_container_width=True
        ):

          # Remove previous database

            clear_database()

          # Create directory for uploaded books

            os.makedirs(
                "uploaded_books",
                exist_ok=True
            )

            pdf_path = os.path.join(
                "uploaded_books",
                uploaded_file.name
            )

          # Save uploaded PDF

            with open(pdf_path, "wb") as file:
                file.write(
                    uploaded_file.getbuffer()
                )

          # Process book


            with st.spinner(
                "Reading and processing your book..."
            ):

                try:

                    new_vectorstore, chunk_count = (
                        create_vectorstore(pdf_path)
                    )

                    # Store vector database in session
                    st.session_state.vectorstore = (
                        new_vectorstore
                    )

                    # Store book name
                    st.session_state.book_name = (
                        uploaded_file.name
                    )

                    # Clear previous conversation
                    st.session_state.messages = []

                    st.success(
                        f"Book processed successfully!\n\n"
                        f"Created {chunk_count} chunks."
                    )

                except Exception as e:

                    st.error(
                        f"Error processing book:\n\n{e}"
                    )

    st.divider()

# CLEAR BOOK BUTTON

    if st.button(
        "🗑️ Clear Book",
        use_container_width=True
    ):

        clear_database()

        st.success("Book removed.")

        st.rerun()

# LOAD EXISTING DATABASE

if st.session_state.vectorstore is None:

    existing_vectorstore = load_vectorstore()

    if existing_vectorstore is not None:

        st.session_state.vectorstore = (
            existing_vectorstore
        )


# MAIN PAGE

st.title("📚 CourseMate AI")

st.caption(
    "Ask questions about your uploaded book "
    "using Retrieval-Augmented Generation."
)

# CURRENT BOOK

if st.session_state.book_name:

    st.info(
        f"📖 Current book: "
        f"**{st.session_state.book_name}**"
    )

elif st.session_state.vectorstore is not None:

    st.info(
        "📖 A previously created book database "
        "is available."
    )

else:

    st.warning(
        "👈 Upload and process a PDF book from "
        "the sidebar to get started."
    )

# DISPLAY CHAT HISTORY

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# CHAT INPUT

query = st.chat_input(
    "Ask something about your book..."
)


if query:

# MAKE SURE A BOOK HAS BEEN PROCESSED

    if st.session_state.vectorstore is None:

        st.warning(
            "Please upload and process a book first."
        )

        st.stop()

# USER MESSAGE

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    with st.chat_message("user"):

        st.markdown(query)

# ASSISTANT RESPONSE

    with st.chat_message("assistant"):

# RETRIEVE DOCUMENTS

        with st.spinner(
            "Searching the book..."
        ):

            retriever = (
                st.session_state.vectorstore
                .as_retriever(
                    search_type="similarity",
                    search_kwargs={
                        "k": 3
                    }
                )
            )

            docs = retriever.invoke(query)

# CREATE CONTEXT

        context = "\n\n".join(
            doc.page_content
            for doc in docs
        )

# PROMPT

        prompt = f"""
You are a helpful AI assistant.

Answer the user's question using ONLY the
provided context from the uploaded book.

If the answer is not present in the context,
say exactly:

"I could not find the answer in the document."

Do not use outside knowledge.

Context:
-------------------------
{context}
-------------------------

Question:
{query}
"""

# CALL MISTRAL

        with st.spinner(
            "Generating answer..."
        ):

            llm = get_llm()

            response = llm.invoke(prompt)

            answer = response.content

# DISPLAY ANSWER

        st.markdown(answer)

# SAVE ASSISTANT MESSAGE

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
