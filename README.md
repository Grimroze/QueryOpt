# QueryOpt: AI-Powered SQL Profiler & Optimizer
**[Watch the Full Working Demo on Loom](https://www.loom.com/share/f029005561124eec89b9d7039ae01e70)**
QueryOpt is a robust, local-first developer tool that leverages Large Language Models (LLMs) to automatically analyze, diagnose, and optimize slow PostgreSQL queries. 

## The Journey: From Version 1 to Version 2

**Version 1 (The Idea):** Initially, the concept required the developer to manually extract the SQL query, export the database schema, run the execution plan, and paste everything into a third-party API. This was highly impractical. Developers hesitate to paste their sensitive connection strings or raw schemas into external cloud services due to massive security risks.

**Version 2 (The Reality):** QueryOpt evolved into a **Local-First Architecture**. You run the API locally on your machine. It securely connects to your database using your environment variables, automatically parses your query to find the required tables, fetches the exact schema needed, runs a safe `EXPLAIN` query, and sends only the metadata (no actual row data, no credentials) to the LLM for optimization.

## The Problem

When a database scales from a few thousand to millions of rows, unoptimized queries can bring the entire system to a halt.

```mermaid
graph LR
    A["Small Database (1,000 rows)"] -->|"Unoptimized Query"| B["Fast Execution (< 1ms)"]
    C["Large Database (10M rows)"] -->|"Unoptimized Query (Missing Index)"| D["Severe Bottleneck (Full Table Scan)"]
    C -->|"Optimized Query (Proper Indexing)"| E["Fast Execution (< 10ms)"]
```

## How QueryOpt Works

QueryOpt operates in two distinct modes to suit different security and testing needs.

### 1. Basic Mode (No Database Connection)
Perfect for quick checks. The developer manually provides the SQL query and the table schema.

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant API as QueryOpt API
    participant LLM as LLM Engine
    
    Dev->>API: POST /analyze (Query + Schema Text)
    API->>LLM: Enhanced Prompt Engineering
    LLM-->>API: JSON Analysis (Issues, Indexes, Rewritten Query)
    API-->>Dev: Structured JSON Response
```

### 2. Deep Mode (Automated Profiling)
The flagship feature. Provide just the SQL query, and QueryOpt handles the rest by interfacing directly with your PostgreSQL database.

```mermaid
flowchart LR
    A["Developer (Sends Query)"] --> B["QueryOpt API"]
    B --> C["Database Module (Extracts Tables, Schema, Plan)"]
    C --> D["Local PostgreSQL"]
    D --> C
    C --> B
    B --> E["LLM Service (Llama 3.1)"]
    E --> B
    B --> A
```

## Security & Architecture

Security is the foundational principle of QueryOpt. Your database credentials NEVER leave your machine.

```mermaid
flowchart TB
    subgraph Local_Developer_Environment
        ENV[".env File (DATABASE_URL)"]
        API["QueryOpt Local API"]
        DB["PostgreSQL Database"]
        
        ENV -->|"Reads Locally"| API
        API <-->|"Fetches Schema & Plan"| DB
    end
    
    subgraph External_Network
        LLM["Cloud LLM API"]
    end
    
    API -->|"Sends ONLY: Query Text, Schema Metadata, EXPLAIN Plan"| LLM
    LLM -->|"JSON Response"| API
```

**Data Privacy Guarantees:**
- **No Credentials Sent:** The DATABASE_URL remains strictly local.
- **No Data Leakage:** QueryOpt uses EXPLAIN, not EXPLAIN ANALYZE. It never fetches actual row data, ensuring PII (Personal Identifiable Information) remains absolutely safe.
- **Open Source:** The entire prompt generation logic can be audited locally.

## Technology Stack
- **Backend:** FastAPI, Python, Pydantic
- **Database Integration:** psycopg2-binary
- **AI/LLM Integration:** LangChain, Groq API (Llama-3.1-8b-instant)
- **Architecture:** Local-first REST API

## Quick Start Guide

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup:**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   GROQ_API_KEY=your_groq_api_key
   ```

3. **Run the Server:**
   ```bash
   uvicorn main:app --reload
   ```

4. **Test the API:**
   Navigate to `http://127.0.0.1:8000/docs` in your browser to access the interactive Swagger UI and test the endpoints.
