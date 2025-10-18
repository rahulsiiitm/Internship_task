# 📄 PDF Data Extraction Tool using LLMs

This is a **full-stack web application** designed to extract **structured data from PDF documents** using **Large Language Models (LLMs)**.  
Users can upload one or more PDF files, select a predefined extraction template, and receive a formatted **Excel (.xlsx)** file containing the extracted information.

This project was built to fulfill the requirements of the **internship task**, demonstrating proficiency in:

- Frontend (React)  
- Backend (FastAPI)  
- LLM integration (Google Gemini)  
- Database management (PostgreSQL)

---

## 🚀 Features

- **Modern Frontend:** A clean, responsive, and user-friendly interface built with React.  
- **Drag-and-Drop File Upload:** Supports uploading multiple PDF files simultaneously.  
- **Dynamic Template Selection:** Users can choose between different extraction templates to process various document types.  
- **Powerful Backend:** A robust API built with FastAPI to handle file processing and LLM orchestration.  
- **High-Accuracy LLM Extraction:** Utilizes Google’s **Gemini 2.5 Pro** model with structured prompts for precise data extraction.  
- **Multi-Sheet Excel Output:** Generates a single `.xlsx` file with multiple sheets, matching the structure of the selected template.  
- **Job Status Logging:** All extraction jobs are logged in a **PostgreSQL (Neon)** database to track processing, completion, or failure.  
- **Resilient API Calls:** Includes a retry mechanism to handle transient network errors when communicating with the LLM API.  

---

## 🎥 Project Demo

*A short video demonstrating the complete workflow: PDF upload, template selection, data extraction, and downloading the final Excel file.*

👉 [Link to demo video to be added here]

---

## 🗂️ Folder Structure

```
/
├── backend/                # FastAPI application (Python)
│   ├── .env                # Environment variables (API keys, DB URL)
│   ├── main.py             # Main application logic and API endpoints
│   ├── prompts.py          # Stores the detailed LLM prompts
│   └── requirements.txt
├── frontend/               # React application
│   ├── src/
│   │   ├── App.jsx         # Main UI component
│   │   └── App.css
│   └── ...
├── templates/              # Contains the Excel extraction templates
│   ├── Extraction Template 1.xlsx
│   └── Extraction Template 2.xlsx
├── examples/
│   ├── sample_pdfs/        # Sample PDF files for testing
│   └── output/             # Example .xlsx output files
└── README.md               # This file
```

---

## 🧰 Tech Stack

| Layer | Technologies |
|-------|---------------|
| **Frontend** | React, Tailwind CSS, react-dropzone |
| **Backend** | Python 3.11+, FastAPI, Uvicorn |
| **LLM** | Google Gemini 2.5 Pro |
| **PDF Parsing** | pdfplumber |
| **Excel Generation** | pandas, xlsxwriter |
| **Database** | PostgreSQL (Neon), SQLAlchemy, psycopg2-binary |

---

## ⚙️ Local Setup and Installation

To run this project locally, ensure you have **Python**, **Node.js**, and **npm** installed.

---

### 🖥️ 1. Backend Setup

First, navigate to the backend directory and set up the Python environment:

```bash
# Navigate to the backend folder
cd backend

# Create and activate a virtual environment
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

# Install the required Python packages
pip install -r requirements.txt
```

Then, create the `.env` file:

```bash
# backend/.env
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
DATABASE_URL="YOUR_NEON_POSTGRESQL_CONNECTION_STRING"
```

Run the backend server:

```bash
uvicorn main:app --reload
```

The FastAPI server will be running at:  
👉 **http://localhost:8000**

---

### 🌐 2. Frontend Setup

In a new terminal:

```bash
# Navigate to the frontend folder
cd frontend

# Install npm dependencies
npm install

# Run the React development server
npm run dev
```

The React app will now be accessible at:  
👉 **http://localhost:5173** (or another port if 5173 is busy)

---

## 🔗 API Endpoints

### `POST /extract/`

**Description:**  
Uploads PDF files and triggers the extraction process.

**Request Body:**  
`multipart/form-data`
- `files`: One or more uploaded PDF files  
- `template_id`: A string (`'1'` or `'2'`) indicating which extraction template to use  

**Response:**
- ✅ **Success (200 OK):** A streaming response containing the generated `extracted_data.xlsx` file.  
- ❌ **Error (4xx/5xx):** A JSON object with an error detail message.

---

## 🧭 How to Use

1. Ensure both backend and frontend servers are running.  
2. Open your browser and navigate to **http://localhost:5173**.  
3. Select either **“Template 1”** or **“Template 2”**.  
4. Drag and drop your PDF files or click to select them manually.  
5. Click **“Extract & Download XLSX”**.  
6. Wait for the process to complete — your browser will automatically download the final Excel file.

---

✅ **Made with 💡 by Rahul Sharma**
