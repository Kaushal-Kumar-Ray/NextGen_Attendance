let video = document.createElement("video");
video.setAttribute("autoplay", true);
video.setAttribute("playsinline", true);

let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");

let intervalId = null;

function startCapture() {
    const studentId = document.getElementById("student_id").value.trim();
    const studentName = document.getElementById("student_name").value.trim();

    if (!studentId || !studentName) {
        alert("Enter Student ID and Name");
        return;
    }

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
            video.play();

            document.getElementById("status").innerText =
                "Camera started. Capturing faces...";

            intervalId = setInterval(() => {
                captureFrame(studentId, studentName);
            }, 400);
        })
        .catch(err => {
            alert("Camera access denied");
            console.error(err);
        });
}

function captureFrame(id, name) {
    if (!video.videoWidth || !video.videoHeight) return;

    // Match canvas to camera
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw live video
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    fetch("/capture_face", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            id: id,
            name: name,
            image: canvas.toDataURL("image/jpeg")
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("status").innerText =
            `Captured ${data.count} / 30 faces`;

        // Draw guide box (visual feedback)
        ctx.strokeStyle = "lime";
        ctx.lineWidth = 3;
        ctx.strokeRect(
            canvas.width * 0.2,
            canvas.height * 0.2,
            canvas.width * 0.6,
            canvas.height * 0.6
        );

        if (data.done) {
            clearInterval(intervalId);
            video.srcObject.getTracks().forEach(t => t.stop());
            document.getElementById("status").innerText =
                "✅ Capture complete. You can now train the model.";
            document.getElementById("trainBtn").style.display = "inline-block";

        }
    })
    .catch(err => console.error(err));
}


function trainModel() {
    document.getElementById("status").innerText = "Training model, please wait...";

    fetch("/train_model", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.getElementById("status").innerText =
                    "✅ Model trained successfully. You can now mark attendance.";
            } else {
                document.getElementById("status").innerText =
                    "❌ Training failed. Check server logs.";
            }
        })
        .catch(err => {
            console.error(err);
            document.getElementById("status").innerText =
                "❌ Training error.";
        });
}
