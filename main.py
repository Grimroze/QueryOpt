"""
FastAPI application entry point for QueryOpt.
Provides endpoints for both Basic (manual schema) and Deep (auto schema) analysis.
"""

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from models import BasicAnalysisRequest, DeepAnalysisRequest, AnalysisResponse
from llm_service import analyze_with_llm
from database import extract_table_names, fetch_table_schema, run_explain_analyze

load_dotenv()

app = FastAPI(
    title="QueryOpt: AI SQL Profiler & Optimizer",
    description="An AI-powered REST API that analyzes slow SQL queries and provides optimized queries and index suggestions.",
    version="2.0.0",
)

@app.get("/")
def home():
    """Health check and API overview."""
    return {
        "project": "QueryOpt",
        "status": "Running",
        "docs": "/docs"
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def basic_analysis(request: BasicAnalysisRequest):
    """
    Basic Mode: The developer provides both the SQL Query and Schema manually.
    No database connection is required.
    """
    try:
        llm_output = analyze_with_llm(
            query=request.query,
            schema=request.schema_text,
            execution_plan=None
        )
        return AnalysisResponse(**llm_output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-deep", response_model=AnalysisResponse)
async def deep_analysis(request: DeepAnalysisRequest):
    """
    Deep Mode: The developer provides only the SQL Query.
    The API automatically connects to the database, fetches the schema, and extracts the EXPLAIN plan.
    """
    try:
        table_names = extract_table_names(request.query)
        if not table_names:
            raise HTTPException(status_code=400, detail="No table names found in the query.")
        
        all_schemas = ""
        for table_name in table_names:
            all_schemas += fetch_table_schema(table_name) + "\n"
        
        execution_plan = run_explain_analyze(request.query)
        
        llm_output = analyze_with_llm(
            query=request.query,
            schema=all_schemas,
            execution_plan=execution_plan
        )
        
        llm_output["execution_plan"] = execution_plan
        return AnalysisResponse(**llm_output)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deep Analysis failed: {str(e)}")
