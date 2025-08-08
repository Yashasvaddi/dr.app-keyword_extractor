from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, json, uuid
import google.generativeai as genai
from dotenv import load_dotenv
import uvicorn
from datetime import datetime
import pytz

india=pytz.timezone('Asia/Kolkata')

indiantime=datetime.now(india)

datestr=f"Day: {indiantime.strftime('%d')}, Month: {indiantime.strftime('%m')}, Year: {indiantime.strftime('%y')}"

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.getenv('gemini_api_key'))
model = genai.GenerativeModel('gemini-2.5-pro')

# ✅ Define request model
class Transcript(BaseModel):
    text: str

@app.post("/")
def extract_medical_data(payload: Transcript):
    global indiantime
    text = payload.text

    if text:
        print("Code entered backend")

    prompt = f"""
    From the following translated doctor-patient conversation: "{text}.'"
    Extract and return only a well-structured **JSON object** containing the answers for 
    'to_SYMPTOMS: SymptomsCode, Symptoms, SymptomsNameCase, Unit
     to_MEDPRESCRIPTION: MedicineCode, MedicineNameCase, MedicineType, MedicineName, MedicineComposit, Dose, DoseUnit, CustomDoseFlag, Frequency, CustomFrequency, WhenTakeMedicine, CustomWhenMedicine, Period, PeriodUnit, CustomPeriodFlag, BrandName, Qty, QtyUnit, CustomQtyFlag, Remarks, Attribute
     to_COMPLAINT: ComplaintCode, Complaint, ComplaintNameCase, Unit
     to_DIAGNOSIS: DiagnosisCode, Diagnosis, DiagnosisNameCase, Unit
     to_EXAMINATION: ExaminationCode, Examination, ExaminationNameCase, Unit
     to_ALLERGY: AllergyCode, Allergy, AllergyNameCase, Unit'
    """

    # Call Gemini model
    response = model.generate_content(prompt)

    content=response.text.strip()

    # Check if response has valid content
    if not content:
        return {
            "error": "Gemini did not return a valid response.",
            "raw_candidates": str(response)
        }

    # Extract actual text from parts
    # content = response.candidates[0].content.parts[0].text.strip()

    try:
        # Remove markdown json wrapping
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()

        parsed_json = json.loads(content)
    except Exception as e:
        return {
            "error": "Invalid JSON from Gemini",
            "exception": str(e),
            "raw_output": content
        }

    os.makedirs("./outputs", exist_ok=True)
    file_id = uuid.uuid4().hex[:8]
    file_path = f"./outputs/structured_data_{file_id}.json"

    with open(file_path, "w") as f:
        json.dump(parsed_json, f, indent=2)

    return parsed_json
