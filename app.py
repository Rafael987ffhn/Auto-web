from flask import Flask, render_template, request, send_file
from gtts import gTTS
import tempfile
import os
import subprocess
import whisper

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return 'No file part', 400

    video = request.files['video']
    language = request.form.get('language')

    if not video or video.filename == '':
        return 'No selected file', 400

    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = os.path.join(tmpdir, 'input.mp4')
        audio_path = os.path.join(tmpdir, 'audio.wav')
        tts_path = os.path.join(tmpdir, 'tts.mp3')
        output_path = os.path.join(tmpdir, 'output.mp4')

        video.save(video_path)

        # Extrai áudio
        subprocess.run(['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', audio_path], check=True)

        # Transcreve com Whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        text = result['text']

        # TTS com gTTS
        tts = gTTS(text=text, lang=language)
        tts.save(tts_path)

        # Combina vídeo + novo áudio
        subprocess.run([
            'ffmpeg', '-i', video_path, '-i', tts_path,
            '-c:v', 'copy', '-map', '0:v:0', '-map', '1:a:0',
            '-shortest', output_path
        ], check=True)

        return send_file(output_path, as_attachment=True, download_name="dublado.mp4")

if __name__ == '__main__':
    app.run(debug=True)
