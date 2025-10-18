
# PDF Data Extraction Tool using LLMs

This is a **full-stack web application** designed to extract **structured data from PDF documents** using **Large Language Models (LLMs)**. Users can upload one or more PDF files, select a predefined extraction template, and receive a formatted **Excel (.xlsx)** file containing the extracted information.

This project was developed as part of an **internship task**, demonstrating proficiency in:

- Frontend development (React)  
- Backend development (FastAPI)  
- LLM integration (Google Gemini)  
- Database management (PostgreSQL)  

---

## Features

- **Modern Frontend:** Clean, responsive, and user-friendly interface built with React.  
- **Drag-and-Drop File Upload:** Supports multiple PDF uploads simultaneously.  
- **Dynamic Template Selection:** Choose between different extraction templates for various document types.  
- **Robust Backend:** FastAPI-based API to handle file processing and LLM orchestration.  
- **High-Accuracy LLM Extraction:** Uses Google Gemini 2.5 Pro with structured prompts for precise data extraction.  
- **Multi-Sheet Excel Output:** Generates a single `.xlsx` file with multiple sheets according to the selected template.  
- **Job Status Logging:** All extraction jobs are logged in PostgreSQL (Neon) to track processing, completion, or failure.  
- **Resilient API Calls:** Includes retry mechanisms to handle transient network errors with the LLM API.  

---

## Demo

## Demo

A short demo showing the end-to-end workflow (upload PDFs, select template, and download the generated Excel).

Watch the video:  
[Demo: PDF Data Extraction Tool — YouTube](https://www.youtube.com/watch?v=7OCUxzgLaT8)


---

## Folder Structure

```
/
├── backend/                
│   ├── .env                
│   ├── main.py             
│   ├── prompts.py 
│   ├── query_database.py    
│   └── requirements.txt
├── frontend/               
│   ├── src/
│   │   ├── App.jsx         
│   │   ├── App.css
│   │   ├── main.jsx
│   │   ├── index.css
│   └── ...
├── templates/              
│   ├── Extraction Template 1.xlsx
│   └── Extraction Template 2.xlsx
├── examples/
│   ├── sample_pdfs/        
│   └── output/             
└── README.md               
```

---

## Tech Stack

| Layer | Technologies |
|-------|---------------|
| **Frontend** | React, Tailwind CSS, react-dropzone |
| **Backend** | Python 3.11+, FastAPI, Uvicorn |
| **LLM** | Google Gemini 2.5 Pro |
| **PDF Parsing** | pdfplumber |
| **Excel Generation** | pandas, xlsxwriter |
| **Database** | PostgreSQL (Neon), SQLAlchemy, psycopg2-binary |

---

## Local Setup

Ensure **Python**, **Node.js**, and **npm** are installed.

### Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create a `.env` file:

```env
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
DATABASE_URL="YOUR_NEON_POSTGRESQL_CONNECTION_STRING"
```

Run the backend server:

```bash
uvicorn main:app --reload
```

Backend will run at **https://pdf-extraction-backend-b3bx.onrender.com**

---

### Frontend Setup

```bash
cd frontend

# Install npm dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at **http://localhost:5173** (or another available port)

---

## API Endpoints

### `POST /extract/`

**Description:** Upload PDF files and trigger extraction.  

**Request Body:** `multipart/form-data`  
- `files`: One or more PDF files  
- `template_id`: Template selection (`'1'` or `'2'`)  

**Response:**  
- **Success (200 OK):** Returns the generated `extracted_data.xlsx` file.  
- **Error (4xx/5xx):** JSON object with error details.

---

## How to Use

1. Run both backend and frontend servers.  
2. Open **http://localhost:5173** in your browser.  
3. Select a template.  
4. Drag and drop PDF files or select manually.  
5. Click **Extract & Download XLSX**.  
6. Download will start automatically after processing.

---

**Developed by Rahul Sharma**
