import streamlit as st
import requests
from streamlit_webrtc import webrtc_streamer, WebRtcMode, ClientSettings
import av
import tempfile
import os

st.title("🩺 Audio Keyword Extractor (Hindi/English)")

# Option to record or upload
option = st.radio("Choose input method:", ("Upload Audio", "Record Audio"))

audio_file = None

if option == "Upload Audio":
    uploaded_file = st.file_uploader("Upload an audio file", type=["wav", "mp3", "m4a"])
    if uploaded_file is not None:
        audio_file = uploaded_file

elif option == "Record Audio":
    st.warning("This requires microphone access and may not work in all browsers.")
    
    # Setup stream
    class AudioProcessor:
        def __init__(self):
            self.recording = b""

        def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
            self.recording += frame.planes[0].to_bytes()
            return frame

    ctx = webrtc_streamer(
        key="example",
        mode=WebRtcMode.SENDRECV,
        in_audio=True,
        media_stream_constraints={"audio": True, "video": False}
    )


    if ctx.audio_processor and st.button("Save Recording"):
        wav_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        with open(wav_file.name, "wb") as f:
            f.write(ctx.audio_processor.recording)
        audio_file = open(wav_file.name, "rb")
        st.success("Audio recorded and saved.")

# API call
if audio_file and st.button("Extract Keywords"):
    with st.spinner("Sending to API..."):
        try:
            url = "https://keywordextractor-95fn.onrender.com/analyze-audio/"
            files = {"file": audio_file}
            response = requests.post(url, files=files)
            result = response.json()
            st.subheader("📋 Extracted Info")
            st.json(result)
        except Exception as e:
            st.error(f"Error: {e}")
