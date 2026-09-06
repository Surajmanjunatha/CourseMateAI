#load pdf
#split into chunks
#create the embeddings
#store into chroma
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

data = PyPDFLoader("uploaded_books/deep_learning_fundamentals.pdf") #to load pdfs use PyPdfloader / to load text use TextLoader
docs = data.load()

splitter = RecursiveCharacterTextSplitter(
     chunk_size = 1000,
     chunk_overlap = 200
)

chunks = splitter.split_documents(docs)

embedding_model = HuggingFaceEmbeddings()

vectorstore = Chroma.from_documents(
     documents = chunks,
     embedding=embedding_model,
     persist_directory="chroma_db"
)