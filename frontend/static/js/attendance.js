
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const video = document.createElement("video");

video.setAttribute("autoplay", true);
video.setAttribute("playsinline", true);

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        video.play();
        document.getElementById("status").innerText = "Camera started";
    })
    .catch(() => alert("Camera access denied"));

let isProcessing = false;

window.loop = setInterval(() => {
    if (!video.videoWidth || isProcessing) return;

    isProcessing = true;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    ctx.drawImage(video, 0, 0);

    fetch("/process_attendance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            image: canvas.toDataURL("image/jpeg")
        })
    })
    .then(res => res.json())
    .then(data => {
        isProcessing = false;

        ctx.drawImage(video, 0, 0);

        if (!data.faces) return;

        ctx.font = "20px Arial";

        // 🔥 SHOW NAME EVEN WITHOUT BOX
        data.faces.forEach((face, i) => {
            ctx.fillStyle = face.name === "Unknown" ? "red" : "lime";
            ctx.fillText(face.name, 20, 40 + i * 30);
        });
    })
    .catch(err => {
        console.error(err);
        isProcessing = false;
    });

}, 2000);