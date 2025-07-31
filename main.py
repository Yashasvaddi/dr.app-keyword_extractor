from fastapi import FastAPI, File, UploadFile, HTTPException
import speech_recognition as sr
import google.generativeai as genai
from pydub import AudioSegment
import tempfile
import os
import json
from dotenv import load_dotenv
import re
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
genai.configure(api_key=os.getenv('gemini_api_key'))
model = genai.GenerativeModel('gemini-2.5-flash')

def convert_audio(file_path):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_output:
        output_path = temp_output.name
        sound = AudioSegment.from_file(file_path)
        sound = sound.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        sound.export(output_path, format="wav")
    return output_path

def transcribe_audio(wav_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)
    return recognizer.recognize_google(audio)

def analyze_with_gemini(text):
    text1=model.generate_content(f'Translate the given doctor-patient conversation to english:{text} and fill in some missing words/grammar if needed.')
    prompt = f'''
From the following translated doctor-patient conversation {text1}:

Extract and return ONLY a valid JSON object with the following keys:
- "to_SYMPTOMS": list of symptom objects with fields: Symptoms, SymptomsNameCase, Severity, FromDate, Duration, Unit
- "to_COMPLAINTS": list of complaint objects with fields: Complaint, Severity, FromDate, Duration, Unit

Example format:
{{
  "to_SYMPTOMS": [
    {{
      "Symptoms": "cough",
      "SymptomsNameCase": "COUGH",
      "Severity": "HIGH",
      "FromDate": "2025-01-15",
      "Duration": "3",
      "Unit": "M"
    }},
    {{
      "Symptoms": "fever",
      "SymptomsNameCase": "FEVER",
      "Severity": "MEDIUM",
      "FromDate": "2025-01-15"
    }}
  ],
  "to_COMPLAINTS": [
    {{
      "Complaint": "cougH",
      "Severity": "MEDIUM",
      "Duration": "2",
      "FromDate": "2025-01-08",
      "Unit": "H"
    }},
    {{
      "Complaint": "Fever And Cough",
      "Severity": "VHIGH"
    }}
  ]
}}

Ensure it is strictly valid JSON without explanation or markdown formatting.
'''

    response = model.generate_content(prompt)
    response_text = response.text.strip()

    if response_text.startswith("```json"):
        response_text = re.sub(r"```json|```", "", response_text).strip()

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        print("❌ JSON parsing failed. Raw Gemini output:\n", response_text)
        return {"error": "Gemini response not valid JSON", "raw": response_text}

@app.post('/')
def test():
    print("The feature is working")
    return "The feature is working"

@app.post("/analyze-audio/")
async def analyze_audio(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".input") as temp_in:
            temp_in.write(await file.read())
            input_path = temp_in.name

        converted_path = convert_audio(input_path)
        transcript = transcribe_audio(converted_path)
        analysis = analyze_with_gemini(transcript)

        result = {
            "transcript": transcript,
            "to_SYMPTOMS": analysis.get("to_SYMPTOMS", []),
            "to_COMPLAINTS": analysis.get("to_COMPLAINTS", [])
        }

        return result

    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Could not understand the audio.")
    except sr.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Speech recognition error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(converted_path):
            os.remove(converted_path)
