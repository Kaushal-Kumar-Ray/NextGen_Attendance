const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const video = document.createElement("video");

video.setAttribute("autoplay", true);
video.setAttribute("playsinline", true);

let isProcessing = false;

// 🎥 Start camera
navigator.mediaDevices.getUserMedia({ video: true })
.then(stream => {
    video.srcObject = stream;
    video.play();
})
.catch(() => alert("Camera access denied"));

// 🔁 Main loop (optimized)
setInterval(() => {
    if (!video.videoWidth || isProcessing) return;

    isProcessing = true;

    // Maintain aspect ratio
    const width = video.videoWidth;
    const height = video.videoHeight;

    canvas.width = width;
    canvas.height = height;

    // Draw video
    ctx.drawImage(video, 0, 0, width, height);

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

        // Redraw frame
        ctx.drawImage(video, 0, 0, width, height);

        if (!data.faces) return;

        // 🔥 DRAW UI OVERLAY
        data.faces.forEach((face, i) => {
            const y = 40 + i * 40;

            const isUnknown = face.name === "Unknown";

            // Background label
            ctx.fillStyle = isUnknown
                ? "rgba(255, 0, 0, 0.7)"
                : "rgba(0, 255, 120, 0.7)";

            ctx.fillRect(15, y - 25, 220, 35);

            // Text
            ctx.fillStyle = "#000";
            ctx.font = "bold 16px sans-serif";
            ctx.fillText(face.name, 25, y);
        });

        // 🎯 Center guide box (optional but pro feel)
        ctx.strokeStyle = "rgba(0,255,255,0.5)";
        ctx.lineWidth = 2;
        ctx.strokeRect(
            width * 0.25,
            height * 0.2,
            width * 0.5,
            height * 0.6
        );

    })
    .catch(err => {
        console.error(err);
        isProcessing = false;
    });

}, 1200); // 🔥 faster + smoother (was 2000ms)