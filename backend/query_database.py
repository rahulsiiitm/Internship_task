import os
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Check if table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'extraction_jobs'
            )
        """))
        table_exists = result.scalar()
        
        if table_exists:
            print("✅ Table exists!\n")
            
            # Get all extraction jobs
            result = conn.execute(text("SELECT * FROM extraction_jobs ORDER BY created_at DESC LIMIT 10"))
            rows = result.fetchall()
            
            if rows:
                print(f"Found {len(rows)} extraction job(s):\n")
                for row in rows:
                    print(f"File: {row[1]}")
                    print(f"Template: {row[2]}")
                    print(f"Status: {row[3]}")
                    print(f"Created: {row[5]}")
                    print(f"Data preview: {row[4][:100]}...")
                    print("-" * 50)
            else:
                print("No extraction jobs found yet")
        else:
            print("❌ Table doesn't exist yet. Run the backend first!")
            
except Exception as e:
    print(f"❌ Error: {e}")