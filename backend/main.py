# main.py (Final Corrected Version)
import os
import json
import io
import cv2
import numpy as np
import easyocr
import database as db
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
reader = easyocr.Reader(['en'])

os.makedirs("processed_images", exist_ok=True)
app.mount("/processed_images", StaticFiles(directory="processed_images"), name="processed_images")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# The fix is in this function signature and the output_filename line
def draw_bounding_box(image_bytes, box, filename):
    """Draws a bounding box on the image and returns the path to the saved image."""
    image_np = np.frombuffer(image_bytes, np.uint8)
    image_cv = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    
    x, y, w, h = box['x'], box['y'], box['width'], box['height']
    cv2.rectangle(image_cv, (x, y), (x + w, y + h), (0, 0, 255), 2)
    
    output_filename = f"annotated_{filename}" # Use the passed filename
    output_path = os.path.join("processed_images", output_filename)
    cv2.imwrite(output_path, image_cv)
    
    return f"http://127.0.0.1:8000/processed_images/{output_filename}"

@app.post("/extract_invoice/")
async def extract_invoice(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = reader.readtext(image_bytes, detail=0)
    invoice_text = " ".join(result)

    if not invoice_text.strip():
        raise HTTPException(status_code=400, detail="OCR failed to extract text.")

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are an expert data extractor. Analyze the text and extract 'vendor_name', 'invoice_date', 'due_date', and 'total_amount'.
                    Also, provide a bounding box for the 'total_amount' with x, y, width, and height.
                    Return ONLY a valid JSON object.
                    Example: {"vendor_name": "...", "total_amount": 199.99, "total_amount_box": {"x": 100, "y": 250, "width": 50, "height": 20}}
                    """
                },
                {"role": "user", "content": f"Invoice text: {invoice_text}"},
            ],
            model="llama-3.1-8b-instant",
            temperature=0,
            max_tokens=300,
            response_format={"type": "json_object"},
        )
        
        extracted_data = json.loads(chat_completion.choices[0].message.content)

        annotated_image_url = None
        if 'total_amount_box' in extracted_data:
             # The fix is here: pass file.filename to the function
             annotated_image_url = draw_bounding_box(image_bytes, extracted_data['total_amount_box'], file.filename)
        
        extracted_data['annotated_image_url'] = annotated_image_url
        
        db.add_invoice(extracted_data)
        return extracted_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI model failed: {str(e)}")

@app.get("/invoices/")
def get_invoices():
    return db.get_all_invoices()    