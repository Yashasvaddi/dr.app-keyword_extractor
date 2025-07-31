import requests

url = "https://keywordextractor-95fn.onrender.com/analyze-audio/"
files = {"file": open("C:\\New folder\\codes\\college stuff\\dr.app-keyword_extractor\\doctor_patient_conversation_hindi.wav", "rb")}

response = requests.post(url, files=files)
print(response.json())
