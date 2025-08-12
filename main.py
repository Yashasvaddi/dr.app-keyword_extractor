from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os, json, uuid
import google.generativeai as genai
from dotenv import load_dotenv
import uvicorn
from openai import OpenAI

load_dotenv()

app = FastAPI()

sum=" "

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client=OpenAI(api_key=os.getenv("openai_api_key"))
# genai.configure(api_key=os.getenv('gemini_api_key'))
# model = genai.GenerativeModel('gemini-2.5-pro')

# ✅ Define request model
class Transcript(BaseModel):
    text: str

@app.post("/summary")
def summary(payload: Transcript):
    global sum
    print("Code entered Summary section")
    text = payload.text

    prompt = f"""
    Summarize the given text: {text}
    The summary must:
    - Contain all the information from the conversation
    - Be easily understandable by a common non-medical person
    - Only output the summary, nothing else
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # You can also use gpt-4o or gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "You are a helpful medical summarization assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    sum=response.choices[0].message.content.strip()
    return {"summary": response.choices[0].message.content.strip()}

@app.post("/")
def extract_medical_data(payload: Transcript):
    global sum
    text = payload.text

    example='''"DoctorID": "00163c3a-06c9-1edf-88aa-376034cb9e31",
    "HospitalID": "00163c3a-06c9-1edf-9c82-285b1805471a",
    "ClinicID": "00163c3a-06c9-1edf-bcd4-ca406b3cd433",
    "UserID": "00163c3a-06c9-1edf-a9f6-b7b7d7dca1ad",
    "Symptoms": "Fever, Cough, Chest Pain",
    "Complaints": "Mild Pain, Chest Pain",
    "Diagnosis": "Cough, Fever",
    "Remarks": "Drink More Water, Avoid Aerated Drinks, Drink At Least 3 Liter",
    "Attribute1": "Remarks - allergy ",
    "Examination": "Stomach Pain, Stomach Itch, Pain",
    "VitalRemarks": "Vitals are Normal",
    "DrRemarks": "Any comments by doctor",
    "Temperature": "102",
    "TemperatureUnit": "F",
    "Weight": "60",
    "WeightUnit": "Kg",
    "Height": "165",
    "HeightUnit": "cm",
    "Preview": True,
    "DrPrivateNotes": "Private Notes - ",
    "PulseRate": "72",
    "PulseRateUnit": "bpm",
    "BpLow": "90",
    "BpHigh": "110",
    "BpUnit": "mmHg",
    "RandomBloodSugar": "120",
    "SugarUnit": "mgdL",
    "SPO2": "98",
    "SPO2Unit": "%",
    "HeartRate": "",
    "HeartRateUnit": "bpm",
    "Systolic": "",
    "SystolicUnit": "mmHg",
    "Diastolic": "",
    "DiastolicUnit": "mmHg",
    "PrescriptionDate": "20250806",
    "PrescriptionTime": "195023",
    "FollowUpDate": "20250806",
    "FollowUpTime": "103000",
    "LabRemarks": "",
    "DigitalRx": True,
    "LanguageKey": "EN",
    "LastUpdatedID": "00163c3a-06c9-1edf-9c82-2121709c0714",
    "LastUpdatedName": "Radha hospital",
    "to_LABPRESCRIPTION": [
        {"TestName": "CT SCAN", "TestNameLower": "CT Scan", "Attribute": ""},
        {"TestName": " CBC", "TestNameLower": " CBC", "Attribute": ""}
    ],
    "to_MEDPRESCRIPTION": [
        {
            "MedicineCode": "00000000",
            "MedicineNameCase": "dolo",
            "MedicineType": "T",
            "MedicineName": "dolo",
            "MedicineComposition": "",
            "Dose": "1 tablet",
            "DoseUnit": "",
            "CustomDoseFlag": False,
            "Frequency": "111",
            "CustomFrequencyFlag": False,
            "WhenTakeMedicine": "",
            "CustomWhenMedicineFlag": False,
            "Period": "",
            "PeriodUnit": "",
            "CustomPeriodFlag": False,
            "BrandName": "",
            "Qty": "0",
            "QtyUnit": "",
            "CustomQtyFlag": False,
            "Remarks": "",
            "Attribute": ""
        },
        {
            "MedicineCode": "00000005",
            "MedicineNameCase": "crocin",
            "MedicineType": "T",
            "MedicineName": "crocin",
            "MedicineComposition": "",
            "Dose": "1 tablet",
            "DoseUnit": "",
            "CustomDoseFlag": False,
            "Frequency": "101",
            "CustomFrequencyFlag": False,
            "WhenTakeMedicine": "After Food",
            "CustomWhenMedicineFlag": True,
            "Period": "2",
            "PeriodUnit": "D",
            "CustomPeriodFlag": False,
            "BrandName": "",
            "Qty": "4",
            "QtyUnit": "",
            "CustomQtyFlag": False,
            "Remarks": "",
            "Attribute": ""
        }
    ],
    "to_REFDOCTOR": [
        {
            "RefDrMasterID": "00163c3a-06c9-1edf-b2c8-39fb27dd0ab2",
            "Name": "Dr. Ramesh",
            "NameUpper": "DR. RAMESH",
            "PhoneNo": "7829927196",
            "WhatsAppNo": "",
            "Email": "",
            "SpecilizationID": "29"
        }
    ],
    "to_SYMPTOMS": [
        {"SymptomsCode": "00000000", "Symptoms": "FEVER", "SymptomsNameCase": "Fever", "Unit": "D"},
        {"SymptomsCode": "00000000", "Symptoms": "COUGH", "SymptomsNameCase": "Cough", "Unit": "D"},
        {"SymptomsCode": "00000000", "Symptoms": "CHEST PAIN", "SymptomsNameCase": "Chest Pain", "Unit": "D"}
    ],
    "to_MEDHISTORY": [
        {"MedicalCode": "00000001", "Medical": "PEANUTS", "MedicalNameCase": "Peanuts", "Severity": "HIGH", "Duration": "2", "FromDate": "20241010", "Unit": "M"},
        {"MedicalCode": "00000000", "Medical": "CANCER", "MedicalNameCase": "Cancer", "Unit": "D"},
        {"MedicalCode": "00000000", "Medical": "ACCIDENT", "MedicalNameCase": "Accident", "Unit": "D"}
    ],
    "to_COMPLAINT": [
        {"ComplaintCode": "00000001", "Complaint": "MILD PAIN", "ComplaintNameCase": "Mild Pain", "Unit": "D"},
        {"ComplaintCode": "00000013", "Complaint": "CHEST PAIN", "ComplaintNameCase": "Chest Pain", "Unit": "D"}
    ],
    "to_DIAGNOSIS": [
        {"DiagnosisCode": "00000000", "Diagnosis": "COUGH", "DiagnosisNameCase": "Cough", "Unit": "D"},
        {"DiagnosisCode": "00000000", "Diagnosis": "FEVER", "DiagnosisNameCase": "Fever", "Unit": "D"}
    ],
    "to_EXAMINATION": [
        {"ExaminationCode": "00000000", "Examination": "STOMACH PAIN", "ExaminationNameCase": "Stomach Pain", "Unit": "D"},
        {"ExaminationCode": "00000000", "Examination": "STOMACH ITCH", "ExaminationNameCase": "Stomach Itch", "Unit": "D"},
        {"ExaminationCode": "00000000", "Examination": "PAIN", "ExaminationNameCase": "Pain", "Unit": "D"}
    ],
    "to_ALLERGY": [
        {"AllergyCode": "00000000", "Allergy": "POLLEN", "AllergyNameCase": "Pollen", "Unit": "D"},
        {"AllergyCode": "00000000", "Allergy": "BERMUDA GRASS", "AllergyNameCase": "Bermuda grass", "Unit": "D"}
    ]
}"'''


    if text:
        print("Code entered JSON generation section")

    prompt = f"""
   From the following translated doctor–patient conversation:
{sum}

Extract the data in exactly this JSON schema:
{example}

Rules:

Output only valid JSON, no code blocks.

If Complaints is empty but Symptoms is present, copy the symptoms into Complaints.

If a symptom is also a diagnosis, fill both fields.

Normalize capitalization for medicine names, diagnoses, and symptoms.

Where a dosage, frequency, period, or unit can be confidently inferred from medical norms, include it.

Leave values empty only if truly not present or inferable from the conversation.

All text should be in English, with transliteration and translation as needed."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a medical data extraction assistant. Respond ONLY with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    try:
        # Parse string to JSON
        parsed_content = json.loads(content)
    except json.JSONDecodeError:
        # Fallback in case the model sends something slightly malformed
        return {"error": "Model did not return valid JSON", "raw_output": content}

    return parsed_content
