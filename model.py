from langchain_community.document_loaders import PyPDFLoader # Corrected import for PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings # Corrected import
from langchain_community.vectorstores import FAISS # Corrected import
from langchain.chains import RetrievalQA
from langchain_community.llms import CTransformers # Corrected import

# --- IMPORTANT ---
# RENAME THIS FILE IF YOUR PDF HAS A DIFFERENT NAME
# FIX: Changed path to the absolute path provided by the user and used a raw string (r'...') 
# to prevent Python from interpreting the backslashes as escape characters.
PDF_FILE_PATH = r"C:\Users\Admin\Desktop\ClangBot\C-LangBot\venv\data\Programming in ANSI C (E. Balagurusamy).pdf"
# RENAME THIS FILE IF YOUR GGUF HAS A DIFFERENT NAME
# FIX: Updated MODEL_FILE_PATH to the full absolute path and used a raw string (r'...') 
# to resolve the Unicode Escape Error.
# NEW: Placeholder path for a different model (e.g., TinyLlama)
MODEL_FILE_PATH = r"C:\Users\Admin\Desktop\ClangBot\C-LangBot\venv\models\TinyLlama-1.1B-Chat-v1.0.Q4_K_M.gguf"

def get_rag_chain():
    # 1. Load the document
    try:
        loader = PyPDFLoader(PDF_FILE_PATH)
        documents = loader.load()
    except FileNotFoundError:
        # Re-raise with a more specific error message if the PDF is missing
        raise FileNotFoundError(
            f"Error: The PDF file was not found at the specified path: {PDF_FILE_PATH}. "
            "Please ensure your PDF is correctly named and placed inside the 'data' folder."
        )

    # 2. Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)

    # 3. Create embeddings and vector store
    # Using a common open-source embedding model
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.from_documents(docs, embeddings)

    # 4. Initialize the local LLM
    try:
        llm = CTransformers(
            model=MODEL_FILE_PATH, # Path to your downloaded model
            # CHANGE: Updated model_type from 'phi' to 'llama' for TinyLlama/Llama models
            model_type="llama",      # Specify the model type (e.g., 'llama', 'phi')
            # FIX: Added local_files_only=True and verbose=True to aid in debugging/loading
            local_files_only=True,
            verbose=True,
            config={'max_new_tokens': 256, 'temperature': 0.1}
        )
    except FileNotFoundError:
        # Re-raise with a more specific error message if the Model is missing
        raise FileNotFoundError(
            f"Error: The GGUF model file was not found at the specified path: {MODEL_FILE_PATH}. "
            "Please ensure your model is downloaded and placed inside the 'models' folder."
        )
    except Exception as e:
        # Catch other errors during model loading (e.g., CTransformers specific errors)
        raise Exception(f"Failed to load the local model using CTransformers. Error: {e}")


    # 5. Initialize the retrieval chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={"k": 2}) # Search for 2 relevant chunks
    )
    return qa_chain
