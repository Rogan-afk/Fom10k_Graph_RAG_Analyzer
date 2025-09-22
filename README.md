# Corporate Filing Analysis Suite

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Core Components](#core-components)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [Project Directory Structure](#project-directory-structure)

---

## Overview
The **Corporate Filing Analysis Suite** is an enterprise-grade web application designed to transform dense SEC Form 10-K filings into high-fidelity, queryable knowledge graphs. The system intelligently parses PDFs to extract the most relevant sections, uses a high-precision AI model to build a detailed graph of entities and relationships, and provides a multi-tab dashboard for file management, interactive querying, and immersive graph exploration.

This tool is built using a modern Python stack, including **Dash** for the frontend, **LangChain** for orchestrating AI interactions, and **OpenAI's gpt-4o** for state-of-the-art text analysis and graph generation.

---

## Features
- **Interactive Dash Dashboard**: A professional, full-screen, three-tab user interface for a seamless workflow.  
- **Intelligent 10-K Parsing**: Automatically identifies and extracts the most critical sections of a 10-K filing ("Business," "Risk Factors," and "Management's Discussion & Analysis").  
- **High-Detail Knowledge Graph Generation**: Uses OpenAI’s advanced function-calling capabilities to extract comprehensive and accurate graphs of entities (Companies, Executives, Risks, Financials) and relationships.  
- **Immersive Graph Visualization**: Renders the knowledge graph in a large, interactive explorer powered by **visdcc**.  
- **Retrieval-Augmented Generation (RAG) Chat**: Enables natural language conversation with the processed document for insights and data points.  
- **Robust File Management**: Supports PDF uploads, persistent caching of processed text and graphs, and secure deletion of documents with all related artifacts.  
- **Asynchronous Processing**: Long-running AI tasks execute in the background to keep the interface responsive.  

---

## System Architecture
The application is modular and efficient. The frontend, built with **Dash**, communicates with a Python backend orchestrating file management, text processing, and AI interactions. **Caching** ensures fast performance for previously processed documents.

### Architecture Flow
```mermaid
sequenceDiagram
    participant User
    participant "Dash Frontend (app.py)" as App
    participant "Text Processor" as TextProc
    participant "Graph Generator" as GraphGen
    participant "File System (Cache)" as Cache
    participant "OpenAI API" as OpenAI
    participant "Graph RAG" as RAG

    User->>+App: Uploads 10-K PDF
    App->>+Cache: Saves PDF to /uploads
    Cache-->>-App: Confirms Save
    App-->>-User: Updates File Dropdowns

    User->>+App: Selects file & Clicks "Process"
    App->>+TextProc: process_pdf_to_text(pdf_path)
    TextProc->>Cache: Reads PDF
    TextProc-->>Cache: Writes extracted text
    TextProc-->>-App: Returns text

    App->>+GraphGen: generate_knowledge_graph(text)
    GraphGen->>OpenAI: Sends text chunks
    OpenAI-->>GraphGen: Returns structured graph data (JSON)
    GraphGen->>+Cache: Writes graph.json
    GraphGen-->>-App: Returns graph data

    App-->>-User: Displays graph

    User->>App: Asks question in "Query & Analysis"
    App->>+RAG: query(filename, question)
    RAG->>Cache: Checks graph.json
    Cache-->>RAG: Confirms

    RAG->>+OpenAI: Sends Analyst prompt
    OpenAI-->>-RAG: Returns answer
    RAG-->>-App: Returns to frontend
    App-->>-User: Displays Q&A

    User->>App: Deletes file
    App->>Cache: delete_file_and_artifacts(filename)
    Cache-->>App: Confirms
    App-->>User: Refreshes dropdowns
```

---

## Core Components
- **`app.py`**: Main application entry. Initializes Dash, defines UI, and handles interactivity.  
- **`src/graph_generator.py`**: Extracts graphs using OpenAI’s function-calling. Defines Pydantic models.  
- **`src/text_processor.py`**: Parses PDFs with PyMuPDF, extracts relevant sections.  
- **`src/file_manager.py`**: Handles saving, listing, and deleting files & cache.  
- **`src/graph_rag.py`**: Query engine that checks cached files and generates contextual answers.  
- **`assets/styles.css`**: CSS overrides for full-screen immersive graph visualization.  

---

## Setup & Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd corporate-filing-analysis-suite
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
.
env\Scripts ctivate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root and add your OpenAI API key:
```bash
OPENAI_API_KEY="sk-..."
```

### 5. Run the Application
```bash
python app.py
```
The app will run at: **http://127.0.0.1:8050**

---

## Usage

### Document Management
- Upload 10-K PDFs via drag-and-drop or file selector.  
- Process documents with **"Process Document"**.  
- Delete files with **"Delete Selected File"**.  

### Graph Explorer
- View processed documents as interactive graphs.  
- Drag nodes, zoom, and pan for exploration.  

### Query & Analysis
- Select a document.  
- Submit a question to receive AI-driven answers.  

---

## Project Directory Structure
```
corporate-filing-analysis-suite/
├── .env
├── .gitignore
├── app.py
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── file_manager.py
│   ├── graph_generator.py
│   ├── graph_rag.py
│   └── text_processor.py
└── assets/
    └── styles.css
```
