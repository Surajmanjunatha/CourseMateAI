````markdown
# 🎓 CourseMate AI

> An AI-powered learning assistant that lets you interact with your course material using Retrieval-Augmented Generation (RAG).

CourseMate AI allows students to upload course material in PDF format and ask questions about its contents. Instead of relying entirely on the LLM's general knowledge, the application retrieves relevant information from the uploaded material and uses it as context to generate grounded answers.

---

## ✨ Features

- 📚 Upload and process PDF course material
- 🔍 Semantic document search using vector embeddings
- 🧠 Retrieval-Augmented Generation (RAG)
- 🤖 Mistral LLM integration
- 🔀 MMR-based document retrieval for diverse results
- 📖 Answers grounded only in the uploaded material
- 💬 Interactive terminal-based chat
- 🖥️ Streamlit web interface
- 💾 Persistent ChromaDB vector store
- 🔐 API keys stored securely using environment variables

---

## 🏗️ Architecture

```text
                    Course Material (PDF)
                            │
                            ▼
                    ┌───────────────┐
                    │  PDF Loader   │
                    │  PyPDFLoader  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Text Splitter │
                    │   Chunking    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  Embeddings   │
                    │ HuggingFace   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   ChromaDB    │
                    │ Vector Store  │
                    └───────┬───────┘
                            │
                    User Question
                            │
                            ▼
                    ┌───────────────┐
                    │ MMR Retriever │
                    │ k=4, fetch=10 │
                    └───────┬───────┘
                            │
                            ▼
                    Relevant Context
                            │
                            ▼
                    ┌───────────────┐
                    │ Mistral LLM   │
                    │   Generation  │
                    └───────┬───────┘
                            │
                            ▼
                       AI Answer
````

---

## 🛠️ Tech Stack

| Technology  | Purpose                                      |
| ----------- | -------------------------------------------- |
| Python      | Application development                      |
| LangChain   | RAG pipeline orchestration                   |
| ChromaDB    | Vector database                              |
| HuggingFace | Text embeddings                              |
| Mistral AI  | LLM-based answer generation                  |
| PyPDF       | PDF document processing                      |
| Streamlit   | Web interface                                |
| uv          | Python environment and dependency management |

---

## 📂 Project Structure

```text
CourseMateAI/
│
├── main.py
├── app.py
├── requirements.txt
├── .gitignore
├── .env.example
│
├── chroma_db/
│   └── Generated vector database
│
├── uploaded_books/
│   └── Uploaded PDF files
│
└── .venv/
    └── Virtual environment
```

> `chroma_db/`, `uploaded_books/`, `.env`, and `.venv/` are excluded from Git using `.gitignore`.

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone <your-repository-url>
```

Navigate into the project:

```bash
cd CourseMateAI
```

---

## 2. Install uv

CourseMate AI uses `uv` for Python environment and dependency management.

Check whether it is installed:

```bash
uv --version
```

If it isn't installed, follow the official `uv` installation instructions.

---

## 3. Create the virtual environment

Python 3.13 is recommended:

```bash
uv venv --python 3.13
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or let `uv` manage the environment automatically using `uv run`.

---

## 4. Install dependencies

```bash
uv pip install -r requirements.txt
```

---

## 5. Configure the Mistral API key

Create a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_mistral_api_key
```

Never commit your `.env` file to GitHub.

A `.env.example` file can be used as a template:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

---

# 📚 Creating the Vector Database

CourseMate AI uses ChromaDB to store the embeddings of the uploaded course material.

The PDF processing pipeline is:

```text
PDF
 ↓
PyPDFLoader
 ↓
Document chunks
 ↓
HuggingFace embeddings
 ↓
ChromaDB
```

The resulting vector database is stored locally in:

```text
chroma_db/
```

Because this directory is generated data, it is excluded from Git.

---

# 💻 Running the Terminal Version

The terminal application is contained in:

```text
main.py
```

Run:

```bash
uv run python main.py
```

You should see:

```text
============================================================
                 🎓 CourseMate AI
============================================================

Your AI-powered course material assistant.

You :

```

Enter a question:

```text
You : What is inheritance in Java?
```

CourseMate AI retrieves relevant sections from the course material and generates an answer using Mistral.

To exit:

```text
You : 0
```

---

# 🖥️ Running the Streamlit Version

The Streamlit application is contained in:

```text
app.py
```

Run:

```bash
uv run streamlit run app.py
```

Streamlit will provide a local URL such as:

```text
http://localhost:8501
```

Open that URL in your browser.

---

# 🔎 How RAG Works

CourseMate AI follows a Retrieval-Augmented Generation pipeline.

### 1. Document Loading

The uploaded PDF is loaded using `PyPDFLoader`.

### 2. Chunking

The document is divided into smaller chunks using:

```python
RecursiveCharacterTextSplitter
```

Current configuration:

```text
Chunk size:    1000
Chunk overlap: 100
```

Chunking makes it possible to retrieve only the relevant sections instead of passing the entire document to the LLM.

### 3. Embeddings

Each chunk is converted into a numerical vector using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

### 4. Vector Storage

The embeddings are stored in ChromaDB.

### 5. Retrieval

When a user asks a question, CourseMate AI uses **Maximal Marginal Relevance (MMR)** retrieval.

Current configuration:

```python
search_type="mmr"

search_kwargs={
    "k": 4,
    "fetch_k": 10,
    "lambda_mult": 0.5
}
```

MMR helps retrieve relevant information while reducing redundancy between retrieved chunks.

### 6. Context Construction

The retrieved chunks are combined into a context passed to the LLM.

### 7. Answer Generation

Mistral receives:

```text
Context + User Question
```

and generates an answer based on the retrieved information.

---

# 🧠 Grounded Responses

CourseMate AI is instructed to use only the retrieved course material.

The system prompt contains:

```text
Use ONLY the provided context to answer the question.

If the answer is not present in the context,
say:

"I could not find the answer in the document."
```

This helps reduce hallucinations and keeps responses grounded in the uploaded material.

---

# 🚧 Future Improvements

Planned improvements include:

* 💬 Conversation-aware RAG
* 🧠 Query rewriting
* 📝 Automatic course summaries
* ❓ AI-generated quizzes
* 🃏 Flashcard generation
* 📊 Learning progress tracking
* 🔖 Source/page citations
* 📚 Support for multiple course materials
* 🔍 Hybrid search
* ⚡ Streaming responses
* 🎯 Reranking retrieved documents
* 🗂️ Course and subject organization
* 🔐 User authentication

---

# 🎯 Project Goal

CourseMate AI aims to make course material easier to understand by combining traditional information retrieval with generative AI.

Instead of asking students to search through hundreds of pages manually:

```text
Student
   │
   │ Question
   ▼
CourseMate AI
   │
   ├── Retrieve relevant content
   │
   ├── Understand context
   │
   └── Generate grounded answer
   │
   ▼
Student gets an answer
```

---

## 📄 License

This project is intended for educational and learning purposes.

```
