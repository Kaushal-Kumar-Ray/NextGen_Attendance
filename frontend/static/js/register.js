let video = document.createElement("video");
video.setAttribute("autoplay", true);
video.setAttribute("playsinline", true);

let canvas = document.getElementById("canvas");
let ctx = canvas.getContext("2d");

let intervalId = null;
let isCapturing = false;

// 🚀 START CAPTURE
function startCapture() {
    const studentId = document.getElementById("student_id").value.trim();
    const studentName = document.getElementById("student_name").value.trim();

    if (!studentId || !studentName) {
        alert("Enter Student ID and Name");
        return;
    }

    if (isCapturing) return;

    isCapturing = true;

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
            video.play();

            document.getElementById("status").innerText =
                "📸 Capturing faces... Please stay steady.";

            intervalId = setInterval(() => {
                captureFrame(studentId, studentName);
            }, 500);
        })
        .catch(err => {
            alert("Camera access denied");
            console.error(err);
            isCapturing = false;
        });
}

// 📸 CAPTURE FRAME
function captureFrame(id, name) {
    if (!video.videoWidth || !video.videoHeight) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    ctx.drawImage(video, 0, 0);

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

        // 🔥 STATUS
        document.getElementById("status").innerText =
            `📊 Captured ${data.count} / 30`;

        // 🎯 GUIDE BOX
        ctx.strokeStyle = "rgba(0,255,255,0.7)";
        ctx.lineWidth = 2;
        ctx.strokeRect(
            canvas.width * 0.25,
            canvas.height * 0.2,
            canvas.width * 0.5,
            canvas.height * 0.6
        );

        // ✅ DONE
        if (data.done) {
            clearInterval(intervalId);
            video.srcObject.getTracks().forEach(t => t.stop());
            isCapturing = false;

            document.getElementById("status").innerText =
                "✅ Capture complete. Ready to train.";

            document.getElementById("trainBtn").style.display = "inline-block";
        }
    })
    .catch(err => {
        console.error(err);
        isCapturing = false;
    });
}

// 🧠 TRAIN MODEL
function trainModel() {
    document.getElementById("status").innerText =
        "🧠 Training model... Please wait.";

    fetch("/train_model", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                document.getElementById("status").innerText =
                    "🎉 Model trained successfully!";
            } else {
                document.getElementById("status").innerText =
                    "❌ Training failed.";
            }
        })
        .catch(err => {
            console.error(err);
            document.getElementById("status").innerText =
                "❌ Training error.";
        });
}