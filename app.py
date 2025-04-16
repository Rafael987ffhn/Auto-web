from flask import Flask, render_template, request
import os
import whisper
from gtts import gTTS
import moviepy.editor as mp

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    video = request.files['video']
    idioma = request.form.get('idioma', 'pt-br')  # Padrão pt-br

    if not video:
        return "Nenhum vídeo enviado", 400

    # Salvar vídeo
    video_path = os.path.join(UPLOAD_FOLDER, video.filename)
    video.save(video_path)

    # Etapa 1: Extrair áudio do vídeo
    clip = mp.VideoFileClip(video_path)
    audio_path = os.path.join(UPLOAD_FOLDER, 'audio_original.wav')
    clip.audio.write_audiofile(audio_path)

    # Etapa 2: Transcrever com Whisper
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    transcription = result['text']

    # Etapa 3: Gerar áudio dublado com gTTS
    tts = gTTS(text=transcription, lang=idioma)
    dubbed_audio_path = os.path.join(UPLOAD_FOLDER, 'audio_dublado.mp3')
    tts.save(dubbed_audio_path)

    # Etapa 4: Substituir áudio original pelo dublado
    new_audio = mp.AudioFileClip(dubbed_audio_path)
    final_clip = clip.set_audio(new_audio)

    # Etapa 5: Exportar vídeo final
    output_filename = f"dublado_{video.filename}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    final_clip.write_videofile(output_path)

    video_url = f"/static/videos/{output_filename}"
    return render_template("index.html", video_url=video_url)
