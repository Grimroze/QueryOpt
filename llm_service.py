"""
LLM Integration module using LangChain and Groq.
Constructs prompts and enforces JSON structured output for database analysis.
"""

import os
import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

def analyze_with_llm(query: str, schema: str, execution_plan: str = None) -> dict:
    """
    Analyzes the SQL query using Groq LLM and returns a structured JSON response.
    """
    # Enforce JSON output using model_kwargs
    model = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0.1,
        model_kwargs={"response_format": {"type": "json_object"}}
    )

    plan_section = ""
    if execution_plan:
        plan_section = f"""
    Execution Plan (EXPLAIN output from the database):
    {execution_plan}
    
    Use this execution plan to provide accurate suggestions (e.g., detecting Sequential Scans).
    """

    prompt_text = f"""
    You are a Senior Database Administrator with expertise in PostgreSQL optimization.
    Analyze the following SQL query and database schema for performance issues.

    === DATABASE SCHEMA ===
    {schema}

    === SQL QUERY ===
    {query}
    {plan_section}

    === ANALYSIS INSTRUCTIONS ===
    1. Check for Full Table Scans (Sequential Scans).
    2. Identify unnecessary SELECT * usage.
    3. Suggest proper B-Tree or Hash indexes for WHERE, JOIN, and ORDER BY clauses.

    === RESPONSE FORMAT ===
    You MUST respond in pure JSON format matching exactly this structure:
    {{
        "is_slow": true/false,
        "issue": "Short description of the problem",
        "issue_type": "One of: FULL_TABLE_SCAN, MISSING_INDEX, SELECT_STAR, INEFFICIENT_JOIN, N_PLUS_ONE, NO_ISSUE",
        "optimized_query": "The rewritten, faster SQL query",
        "suggested_indexes": [
            {{
                "index_name": "idx_tablename_columnname",
                "create_statement": "CREATE INDEX idx_tablename_columnname ON tablename(columnname);",
                "reason": "Why this index is needed"
            }}
        ],
        "explanation": "Detailed technical explanation of the issue and solution."
    }}
    """

    messages = [
        SystemMessage(content="You are a PostgreSQL optimization expert. Always respond in valid JSON only."),
        HumanMessage(content=prompt_text)
    ]

    response = model.invoke(messages)
    
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        raise ValueError("LLM did not return a valid JSON format.")
