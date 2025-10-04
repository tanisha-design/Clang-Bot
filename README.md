C-LangBot: AI C Programming Assistant
Overview : 
C-LangBot is an advanced Natural Language Processing (NLP) application designed to serve as an intelligent Q&A assistant for the C programming language.
This project utilizes a Retrieval-Augmented Generation (RAG) pipeline to answer user queries with information strictly grounded in the content of the Programming in ANSI C textbook. It demonstrates the effective use of powerful, self-hosted LLMs for building context-aware, reliable knowledge bots.
The entire interface is presented through a custom, highly interactive Streamlit front end featuring a dark, futuristic aesthetic and smooth UI transitions.


 
 Core Technology Stack

Python 3.x, Streamlit
Application framework and interactive web interface.
RAG Pipeline
LangChain
Orchestrates the entire RAG workflow (document loading, splitting, retrieval, and generation).
programming_in_ansi_c.pdf
Vector Store
Local LLM : TinyLlama (GGUF via CTransformers)

The self-hosted Large Language Model responsible for synthesizing the final, coherent answer.


Getting Started (Local Setup)
Followed these steps to clone the repository, set up environment, and run the C-LangBot locally.

1. Prerequisites
 Python 3.10+ installed on your system.

2. Project Setup
Open your terminal execute the following:

# Clone the repository
# Create and activate the virtual environment

3. Install Dependencies
Install all necessary Python libraries within your activated environment:

4. Configure Local Model & Data
A. Download the LLM Model
B. Add the Knowledge Base

5. Run the Application(streamlit run app.py)

The application will automatically open in your default web browser (http://localhost:8501). The RAG model will take a moment to initialize the first time as it loads the LLM.


Project Structure
C-LangBot/
├── venv/                      # Python Virtual Environment
├── data/                      # Contains the C programming textbook (PDF)
│   └── programming_in_ansi_c.pdf
├── models/                    # Contains the TinyLlama GGUF file
│   └── tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
├── app.py                     # Primary Streamlit UI and chat logic (Frontend)
├── model.py                   # RAG Pipeline: loads data, creates vector store, initializes LLM (Backend)
└── requirements.txt           # List of dependencies
