import os
import io
import json
import pandas as pd
import pdfplumber
import google.generativeai as genai
from typing import List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# --- Setup and Configuration ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in .env file.")
genai.configure(api_key=api_key)

app = FastAPI()
origins = ["http://localhost:3000", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Prompt Engineering Section ---

def get_template_1_prompt(text_from_pdf: str) -> str:
    """Template 1: Extracts detailed financial tables."""
    json_structure = """
    {
      "schedule_of_investments": [
        { "portfolio_company": "...", "industry": "...", "cost": 0, "fair_value": 0 }
      ],
      "statement_of_operations": [
        { "description": "...", "amount": "..." }
      ]
    }
    """
    return f"""
    You are an expert financial data extractor. Your task is to extract the 'Schedule of Investments' and 'Statement of Operations' tables.
    Your final output must be a single, valid JSON object and nothing else, matching this structure: {json_structure}
    Here is the text to analyze:
    ---
    {text_from_pdf}
    ---
    """

def get_template_2_prompt(text_from_pdf: str) -> str:
    """Template 2: Extracts document summary information."""
    json_structure = """
    {
      "fund_name": "Name of the fund",
      "document_type": "Type of the document (e.g., Financial Statement)",
      "period_ending": "The date the reporting period ends",
      "auditor_name": "The name of the auditing firm"
    }
    """
    return f"""
    You are an expert data extractor focused on metadata. Your task is to extract high-level summary information from the document.
    Your final output must be a single, valid JSON object and nothing else, matching this structure: {json_structure}
    Here is the text to analyze:
    ---
    {text_from_pdf}
    ---
    """

# --- Helper Function ---
def clean_llm_json_output(raw_text: str) -> dict:
    try:
        if raw_text.strip().startswith("```json"):
            clean_text = raw_text.strip()[7:-3]
        else:
            clean_text = raw_text.strip()
        return json.loads(clean_text)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from LLM response: {raw_text}")
        return {}

# --- Main API Endpoint ---
@app.post("/generate-excel-multi/")
async def generate_excel_multi(
    files: List[UploadFile] = File(...), 
    template_id: str = Form(...)
):
    """
    Processes multiple PDF files using a selected template and aggregates
    the results into a single multi-sheet Excel file.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    model = genai.GenerativeModel('gemini-pro-latest')
    output_stream = io.BytesIO()

    with pd.ExcelWriter(output_stream, engine='openpyxl') as writer:
        # Loop through each uploaded file
        for i, file in enumerate(files):
            try:
                # 1. Extract text from the current PDF
                pdf_stream = io.BytesIO(await file.read())
                extracted_text = ""
                with pdfplumber.open(pdf_stream) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            extracted_text += page_text + "\n"
                
                if not extracted_text.strip():
                    continue # Skip empty files

                # 2. Select the correct prompt based on template_id
                if template_id == 'template1':
                    prompt = get_template_1_prompt(extracted_text)
                elif template_id == 'template2':
                    prompt = get_template_2_prompt(extracted_text)
                else:
                    raise HTTPException(status_code=400, detail="Invalid template ID.")

                # 3. Call LLM and process the data
                response = model.generate_content(prompt)
                data = clean_llm_json_output(response.text)
                
                # 4. Write extracted data to a new sheet for this file
                # The sheet name will be a truncated version of the filename
                sheet_name = f"File_{i+1}_{file.filename[:20]}"
                
                all_dfs = {}
                for key, value in data.items():
                    if isinstance(value, list):
                        all_dfs[key] = pd.DataFrame(value)
                    elif isinstance(value, dict):
                         all_dfs[key] = pd.DataFrame([value])

                # Create a temporary Excel writer for this file's data to merge into one sheet
                temp_stream = io.BytesIO()
                with pd.ExcelWriter(temp_stream, engine='openpyxl') as temp_writer:
                    for df_name, df in all_dfs.items():
                        df.to_excel(temp_writer, sheet_name=df_name, index=False)
                
                # For simplicity, we'll convert the main data to a DataFrame
                # A more complex approach would be to write each sub-table to the sheet
                main_df = pd.DataFrame.from_dict(data, orient='index').transpose()
                main_df.to_excel(writer, sheet_name=sheet_name, index=False)

            except Exception as e:
                # If one file fails, we can skip it or handle the error
                print(f"Failed to process {file.filename}: {e}")
                continue

    output_stream.seek(0)
    headers = {'Content-Disposition': f'attachment; filename="aggregated_extraction.xlsx"'}
    return StreamingResponse(output_stream, headers=headers, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')