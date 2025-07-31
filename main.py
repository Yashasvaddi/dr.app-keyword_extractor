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
    allow_origins=["*"],  # Or specify your frontend domain here for better security
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
    prompt = f'''
Translate the given doctor-patient conversation in english if it is not in english:{text}\n
From the following translated doctor-patient conversation:\n

Extract and return ONLY a valid JSON object with the following keys:
- "symptoms" (list of strings)
- "symptom_duration" (string)
- "medication" (list of strings)
- "healing_time" (string)

Ensure it is strictly valid JSON without explanation or markdown formatting.
'''

    response = model.generate_content(prompt)
    response_text = response.text.strip()

    # 🔍 Clean response if wrapped in markdown
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

        # Unpack keys into top-level response
        result = {
            "transcript": transcript,
            "symptoms": analysis.get("symptoms", []),
            "symptom_duration": analysis.get("symptom_duration", ""),
            "medication": analysis.get("medication", []),
            "healing_time": analysis.get("healing_time", "")
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
