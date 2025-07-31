let mediaRecorder;
let recordedChunks = [];
let selectedFile = null;

const recordBtn = document.getElementById("recordBtn");
const stopBtn = document.getElementById("stopBtn");
const submitBtn = document.getElementById("submitBtn");
const audioInput = document.getElementById("audioUpload");
const responseBox = document.getElementById("response");
const previewAudio = document.createElement("audio");
previewAudio.controls = true;
previewAudio.style.display = "none";
document.querySelector(".container").appendChild(previewAudio);

audioInput.addEventListener("change", (e) => {
  selectedFile = e.target.files[0];

  // Show uploaded audio for playback
  if (selectedFile) {
    const fileURL = URL.createObjectURL(selectedFile);
    previewAudio.src = fileURL;
    previewAudio.style.display = "block";
  }
});

recordBtn.addEventListener("click", async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);

  recordedChunks = [];

  mediaRecorder.ondataavailable = function (e) {
    if (e.data.size > 0) recordedChunks.push(e.data);
  };

  mediaRecorder.onstop = () => {
    const blob = new Blob(recordedChunks, { type: "audio/wav" });
    selectedFile = new File([blob], "recorded_audio.wav");

    // Show playback
    const blobURL = URL.createObjectURL(blob);
    previewAudio.src = blobURL;
    previewAudio.style.display = "block";
  };

  mediaRecorder.start();
  recordBtn.disabled = true;
  stopBtn.disabled = false;
});

stopBtn.addEventListener("click", () => {
  mediaRecorder.stop();
  recordBtn.disabled = false;
  stopBtn.disabled = true;
});

submitBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    alert("Please record or upload an audio file.");
    return;
  }

  const formData = new FormData();
  formData.append("file", selectedFile);

  responseBox.textContent = "Sending to API...";

  try {
    const res = await fetch("https://keywordextractor-95fn.onrender.com/analyze-audio/", {
      method: "POST",
      body: formData,
    });

    const json = await res.json();
    responseBox.textContent = JSON.stringify(json, null, 2);
  } catch (err) {
    responseBox.textContent = "Error: " + err;
  }
});
