import io
import os
import json
import google.generativeai as genai
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import pdfplumber
from dotenv import load_dotenv
from prompts import TEMPLATE_1_PROMPT, TEMPLATE_2_PROMPT
from xlsxwriter import Workbook


# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://pdf-extraction-backend-b3bx.onrender.com",
    "https://pdftoxl.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure the Gemini API key
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in .env file.")
    else:
        genai.configure(api_key=api_key)
except Exception as e:
    print(f"Error configuring Google API: {e}")


def get_template_prompt(template_id):
    if template_id == '1':
        return TEMPLATE_1_PROMPT
    elif template_id == '2':
        return TEMPLATE_2_PROMPT
    else:
        raise HTTPException(status_code=400, detail="Invalid template ID provided.")


def get_llm_extraction(text, template_id):
    template_prompt = get_template_prompt(template_id)
    full_prompt = f"""
    {template_prompt}

    Here is the text to process:
    ---
    {text}
    ---
    """

    try:
        print("--- SENDING REQUEST TO GEMINI 2.5 PRO ---")
        model = genai.GenerativeModel('gemini-2.5-pro')
        response = model.generate_content(full_prompt)
        
        cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
        
        print("--- RECEIVED RESPONSE FROM GEMINI 2.5 PRO ---")
        print(cleaned_response_text)

        extracted_data = json.loads(cleaned_response_text)
        return extracted_data

    except json.JSONDecodeError as e:
        print(f"Error: LLM returned invalid JSON. Details: {e}")
        print("--- FAULTY RESPONSE TEXT ---")
        print(cleaned_response_text)
        raise HTTPException(status_code=500, detail="LLM returned data in an invalid format. Check the backend console.")
    except Exception as e:
        print(f"Error during LLM extraction: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during LLM extraction: {e}")


@app.post("/extract/")
async def extract_data(files: list[UploadFile] = File(...), template_id: str = Form(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files were uploaded.")

    data_by_sheet = {}

    for file in files:
        if file.content_type != 'application/pdf':
            print(f"Skipping non-PDF file: {file.filename}")
            continue

        try:
            print(f"Processing file: {file.filename}")
            pdf_text = ""
            with pdfplumber.open(io.BytesIO(await file.read())) as pdf:
                for i, page in enumerate(pdf.pages):
                    print(f"Extracting text from page {i+1} of {file.filename}")
                    page_text = page.extract_text(x_tolerance=1)
                    if page_text:
                        pdf_text += page_text + "\n"

            if not pdf_text.strip():
                print(f"Warning: No text could be extracted from {file.filename}.")
                if "Errors" not in data_by_sheet: data_by_sheet["Errors"] = []
                data_by_sheet["Errors"].append({"Source File": file.filename, "Error": "No text could be extracted."})
                continue

            llm_result = get_llm_extraction(pdf_text, template_id)

            for sheet_name, rows in llm_result.items():
                if not isinstance(rows, list): continue
                
                for row in rows:
                    if isinstance(row, dict):
                        row['Source File'] = file.filename
                
                if sheet_name not in data_by_sheet:
                    data_by_sheet[sheet_name] = []
                data_by_sheet[sheet_name].extend(rows)

        except Exception as e:
            print(f"Failed to process file {file.filename}: {e}")
            if "Errors" not in data_by_sheet: data_by_sheet["Errors"] = []
            error_detail = str(e.detail) if isinstance(e, HTTPException) else str(e)
            data_by_sheet["Errors"].append({"Source File": file.filename, "Error": error_detail})

    if not data_by_sheet or all(not data_by_sheet[sheet] for sheet in data_by_sheet if sheet != "Errors"):
        if "Errors" in data_by_sheet and data_by_sheet["Errors"]:
            pass
        else:
            raise HTTPException(status_code=500, detail="Data could not be extracted from any of the files.")

    # Define which sheets should be transposed
    SUMMARY_SHEETS = {
        '1': ["Fund Data", "Fund Manager", "Fund Financial Position"],
        '2': ["Portfolio Summary"]
    }

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, data in data_by_sheet.items():
            if not data: continue
            
            df = None
            # Check if the current sheet is a summary sheet for the selected template
            if sheet_name in SUMMARY_SHEETS.get(template_id, []):
                transposed_data = []
                for row_dict in data:
                    source_file = row_dict.get('Source File', 'N/A')
                    for key, value in row_dict.items():
                        if key != 'Source File':
                            transposed_data.append({'Source File': source_file, 'Metric': key, 'Value': value})
                df = pd.DataFrame(transposed_data)
            else:
                df = pd.DataFrame(data)

            if df.empty: continue

            # Reorder 'Source File' to be the first column
            if 'Source File' in df.columns:
                cols = ['Source File'] + [col for col in df.columns if col != 'Source File']
                df = df[cols]
            
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            # Auto-adjust column widths
            worksheet = writer.sheets[sheet_name]
            for idx, col in enumerate(df):
                series = df[col]
                max_len = max((
                    series.astype(str).map(len).max(),
                    len(str(series.name))
                )) + 2
                worksheet.set_column(idx, idx, max_len)

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=extracted_data.xlsx"}
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to the PDF Extraction API!"}

