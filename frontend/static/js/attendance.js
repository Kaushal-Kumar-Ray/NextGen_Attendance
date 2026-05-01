const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const video = document.createElement("video");

video.setAttribute("autoplay", true);
video.setAttribute("playsinline", true);

let isProcessing = false;

navigator.mediaDevices.getUserMedia({ video: true })
.then(stream => {
    video.srcObject = stream;
    video.play();
})
.catch(() => alert("Camera access denied"));

setInterval(() => {
    if (!video.videoWidth || isProcessing) return;

    isProcessing = true;
    const width = video.videoWidth;
    const height = video.videoHeight;
    canvas.width = width;
    canvas.height = height;

    ctx.drawImage(video, 0, 0, width, height);

    fetch("/process_attendance", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: canvas.toDataURL("image/jpeg") })
    })
    .then(res => res.json())
    .then(data => {
        isProcessing = false;
        ctx.drawImage(video, 0, 0, width, height);

        if (!data.faces) return;

        data.faces.forEach((face, i) => {
            const y = 40 + i * 40;
            const isUnknown = face.name === "Unknown";
            
            // Clean Silver theme canvas overlays
            ctx.fillStyle = isUnknown ? "rgba(220, 38, 38, 0.85)" : "rgba(5, 150, 105, 0.85)";
            ctx.fillRect(15, y - 25, 240, 35);

            ctx.fillStyle = "#ffffff";
            ctx.font = "600 16px 'DM Sans', sans-serif";
            ctx.fillText(face.name, 25, y);
        });

        // Clean guide box
        ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
        ctx.lineWidth = 2;
        ctx.setLineDash([10, 10]);
        ctx.strokeRect(width * 0.25, height * 0.2, width * 0.5, height * 0.6);
        ctx.setLineDash([]);
    })
    .catch(err => {
        console.error(err);
        isProcessing = false;
    });

}, 1200);