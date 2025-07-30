import requests

url = "https://keywordextractor-95fn.onrender.com/analyze-audio/"
files = {"audio_file": open("C:\\New folder\\codes\\college stuff\\dr.app-keyword_extractor\\doctor_patient_conversation.wav", "rb")}

response = requests.post(url, files=files)
print(response.json())
