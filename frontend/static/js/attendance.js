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

setInterval(() => {
    if (!video.videoWidth) return;

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
        ctx.drawImage(video, 0, 0);

        if (!data.faces) return;

        ctx.font = "18px Arial";
        ctx.lineWidth = 3;

        data.faces.forEach(face => {
            ctx.strokeStyle = face.name === "Unknown" ? "red" : "lime";
            ctx.fillStyle = "yellow";

            ctx.strokeRect(face.x, face.y, face.w, face.h);
            ctx.fillText(face.name, face.x, face.y - 8);
        });
    });
}, 1200);
