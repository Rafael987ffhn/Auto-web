
from flask import Flask, request, render_template, send_file
from gtts import gTTS
import ffmpeg
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video = request.files["video"]
        text = request.form["text"]

        if not video or not text:
            return "Faltam dados", 400

        video_filename = os.path.join(UPLOAD_FOLDER, str(uuid.uuid4()) + "_" + video.filename)
        video.save(video_filename)

        tts = gTTS(text=text, lang="pt-br")
        audio_filename = os.path.join(OUTPUT_FOLDER, str(uuid.uuid4()) + "_audio.mp3")
        tts.save(audio_filename)

        output_filename = os.path.join(OUTPUT_FOLDER, str(uuid.uuid4()) + "_output.mp4")

        (
            ffmpeg
            .input(video_filename)
            .input(audio_filename)
            .output(output_filename, vcodec='copy', acodec='aac', strict='experimental')
            .run()
        )

        return send_file(output_filename, as_attachment=True)

    return render_template("index.html")
