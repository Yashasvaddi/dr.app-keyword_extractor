<button onclick="startRecording()">Start</button>
<button onclick="stopRecording()">Stop</button>

<script>
let mediaRecorder;
let audioChunks = [];

async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    mediaRecorder.onstop = uploadAudio;
    mediaRecorder.start();
}

function stopRecording() {
    mediaRecorder.stop();
}

function uploadAudio() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append("file", audioBlob, "recorded_audio.wav");

    fetch("https://keywordextractor-95fn.onrender.com/analyze-audio/", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        console.log("API response:", data);
        // Optional: Display on your PHP page using DOM
    })
    .catch(err => console.error("Upload error:", err));
}
</script>
