# Corporate Filing Analysis Suite

## Table of Contents
- [Overview: From Documents to Decisions](#overview-from-documents-to-decisions)
- [What is a Knowledge Graph?](#what-is-a-knowledge-graph)
- [What is RAG?](#what-is-rag)
- [The Power of Combining KG & RAG for 10-Ks](#the-power-of-combining-kg--rag-for-10-ks)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Getting Started: A Beginner-Friendly Guide](#getting-started-a-beginner-friendly-guide)
  - [Step 1: Set Up Your Workspace](#step-1-set-up-your-workspace)
  - [Step 2: Install the Necessary Tools](#step-2-install-the-necessary-tools)
  - [Step 3: Connect to the AI Brain](#step-3-connect-to-the-ai-brain)
  - [Step 4: Launch the Application](#step-4-launch-the-application)
- [How to Use the Suite: A Quick Manual](#how-to-use-the-suite-a-quick-manual)
- [Project Directory Structure](#project-directory-structure)

---

## Overview: From Documents to Decisions
The **Corporate Filing Analysis Suite** is designed to assist in the interpretation of complex financial documents, particularly SEC Form 10-Ks. These filings, often extending hundreds of pages, are transformed into interactive knowledge graphs that allow users to explore entities and their relationships. Instead of manually searching through text, users can visualize connections and pose natural language questions to obtain precise, data-supported insights.

---

## What is a Knowledge Graph?
A **Knowledge Graph (KG)** organizes information as a network of entities (nodes) and their relationships (edges). For Form 10-Ks, the ontology of extracted entities can be expressed as:

\[
\mathcal{E} = \{ \text{Company}, \text{Segment}, \text{Risk}, \text{Financial}, \text{Regulation}, \text{Executive}, \text{Event} \}
\]

Entities are extracted from the document:

\[
\mathcal{V}(D) = \{ v_1, v_2, \ldots, v_n \}, \quad v_k \in \mathcal{E}
\]

Relations between these entities form edges:

\[
R(D) = \{ (v_i, r, v_j) \mid v_i, v_j \in \mathcal{V}(D), r \in \mathcal{R} \}
\]

where the relation set is defined as:

\[
\mathcal{R} = \{ \texttt{OWNS}, \texttt{OPERATES}, \texttt{REPORTS}, \texttt{SUBJECT\_TO}, \texttt{MENTIONS}, \texttt{ASSOCIATED\_WITH} \}
\]

**Examples:**

\[
(\text{UnitedHealth Group}, \texttt{OWNS}, \text{Optum Health}) \\
(\text{UnitedHealth Group}, \texttt{REPORTS}, \text{Revenue = \$372B}) \\
(\text{UnitedHealth Group}, \texttt{SUBJECT\_TO}, \text{Regulatory risk})
\]

The resulting knowledge graph is represented as:

\[
\mathcal{G}(D) = (\mathcal{V}, \mathcal{E})
\]

---

## What is RAG?
**Retrieval-Augmented Generation (RAG)** enhances AI-based responses by combining retrieval and generation. Before generating an answer, the system retrieves contextually relevant data (here, from the knowledge graph) to ensure that outputs are grounded in authoritative sources.

---

## The Power of Combining KG & RAG for 10-Ks
The integration of Knowledge Graphs and RAG offers a significant improvement in analyzing financial filings. While traditional retrieval methods return sentences, the KG-RAG framework provides structured, context-rich answers by leveraging graph connectivity.

**Examples of supported queries:**
- *“What risks are linked to the Optum Health segment?”*
- *“Which executives are associated with the company’s main revenue sources?”*

This approach ensures that insights are both faster and more accurate than conventional search-based methods.

---

## Features
- **Interactive Dashboard**: A professional, multi-tab user interface for streamlined workflows.  
- **Intelligent 10-K Parsing**: Automatic extraction of critical sections for analysis.  
- **Comprehensive Knowledge Graph**: High-precision mapping of entities and their relationships.  
- **Immersive Graph Explorer**: Interactive visualization with zoom, drag, and pan functionality.  
- **Conversational Q&A**: Plain-English queries supported through KG-RAG integration.  
- **Efficient File Management**: PDF uploads, cached storage, and secure deletion of artifacts.  
- **Responsive Performance**: Asynchronous background task execution ensures fluid interactivity.  

---

## System Architecture
The system is structured for modularity and efficiency. The **Dash frontend** serves the interface, while the **Python backend** manages parsing, graph generation, and communication with external APIs.

### Simplified Architecture Diagram
```mermaid
graph TD
    subgraph "User Interface"
        A[Dash Frontend<br>(app.py)]
    end

    subgraph "Backend Services (Python)"
        B[File & Cache Manager<br>file_manager.py]
        C[10-K Text Processor<br>text_processor.py]
        D[Knowledge Graph Engine<br>graph_generator.py]
        E[RAG Chat System<br>graph_rag.py]
    end

    subgraph "External & Storage"
        F[OpenAI API<br>(gpt-4o)]
        G[File System<br>(Uploads & Cache)]
    end

    A --> B & E
    B --> G
    C --> D
    D --> F
    E --> F
    C --> G
    D --> G
```

---

## Getting Started: A Beginner-Friendly Guide

### Step 1: Set Up Your Workspace
Obtain the project files by cloning the repository or downloading as a ZIP archive.

```bash
git clone <your-repository-url>
cd corporate-filing-analysis-suite
```

### Step 2: Install the Necessary Tools
Create and activate a virtual environment:

```bash
# Windows
python -m venv venv
.
env\Scripts ctivate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Step 3: Connect to the AI Brain
Create a `.env` file in the project root with the following entry:

```bash
OPENAI_API_KEY="sk-..."
```

### Step 4: Launch the Application
Run the application locally:

```bash
python app.py
```

Access it at: **http://127.0.0.1:8050**

---

## How to Use the Suite: A Quick Manual

### Document Management
- **Upload**: Import 10-K PDFs.  
- **Process**: Extract text and generate graphs.  
- **Delete**: Remove files and associated cache.  

### Graph Explorer
- **View**: Explore interactive knowledge graphs.  
- **Interact**: Move nodes, zoom, and examine relationships.  

### Query & Analysis
- **Select**: Choose a processed document.  
- **Ask**: Submit questions for graph-based responses.  

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
