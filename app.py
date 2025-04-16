import os
import subprocess
from flask import Flask, render_template, request, redirect, url_for
import whisper
from gtts import gTTS
from werkzeug.utils import secure_filename

app = Flask(__name__)
if __name__ == '__main__':
    app.run(debug=True)

# Caminho para salvar vídeos e áudios
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Função para extrair o áudio do vídeo
def extract_audio(video_path):
    audio_path = os.path.join(UPLOAD_FOLDER, "audio_original.wav")
    cmd = ['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', audio_path, '-y']
    subprocess.run(cmd, check=True)
    return audio_path
chmod -R 777 uploads/

# Função para transcrição de áudio
def transcribe_audio(audio_path):
    model = whisper.load_model("base")  # ou "tiny" para mais rápido
    result = model.transcribe(audio_path)
    return result["text"]

# Função para gerar áudio dublado
def generate_dubbed_audio(text, lang='pt-br'):
    tts = gTTS(text=text, lang=lang)
    dubbed_audio_path = os.path.join(UPLOAD_FOLDER, "audio_dublado.mp3")
    tts.save(dubbed_audio_path)
    return dubbed_audio_path

# Função para substituir o áudio do vídeo
def replace_audio_in_video(video_path, dubbed_audio_path):
    output_video_path = os.path.join(UPLOAD_FOLDER, "video_dublado.mp4")
    cmd = ['ffmpeg', '-i', video_path, '-i', dubbed_audio_path, '-c:v', 'copy', '-c:a', 'aac', '-strict', 'experimental', output_video_path]
    subprocess.run(cmd, check=True)
    return output_video_path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    try:
        if 'video' not in request.files:
            print("Erro: Nenhum vídeo enviado.")
            return "Erro: Nenhum vídeo enviado.", 400

        video_file = request.files['video']
        idioma = request.form['idioma']
        if video_file.filename == '':
            print("Erro: Nenhum arquivo selecionado.")
            return "Erro: Nenhum arquivo selecionado.", 400
        
        print(f"Arquivo recebido: {video_file.filename}")
        
        if video_file:
            video_filename = secure_filename(video_file.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
            video_file.save(video_path)

            # Etapas de processamento
            print("Extraindo áudio...")
            audio_path = extract_audio(video_path)
            print(f"Áudio extraído: {audio_path}")

            print("Realizando transcrição...")
            transcription = transcribe_audio(audio_path)
            print(f"Transcrição: {transcription}")

            print("Gerando áudio dublado...")
            dubbed_audio_path = generate_dubbed_audio(transcription, lang=idioma)
            print(f"Áudio dublado gerado: {dubbed_audio_path}")

            print("Substituindo áudio no vídeo...")
            output_video_path = replace_audio_in_video(video_path, dubbed_audio_path)
            print(f"Vídeo final gerado: {output_video_path}")

            return redirect(url_for('download', filename=output_video_path))

    except Exception as e:
        print(f"Erro durante o processamento: {str(e)}")
        return f"Ocorreu um erro: {str(e)}", 500


@app.route('/download/<filename>')
def download(filename):
    return redirect(url_for('static', filename=filename))

if __name__ == '__main__':
    app.run(debug=True)
@app.route('/processar', methods=['POST'])
def processar():
    try:
        if 'video' not in request.files:
            print("Erro: Nenhum vídeo enviado.")
            return redirect(request.url)

        video_file = request.files['video']
        idioma = request.form['idioma']
        if video_file.filename == '':
            print("Erro: Nenhum arquivo selecionado.")
            return redirect(request.url)
        
        print("Arquivo recebido:", video_file.filename)
        
        if video_file:
            video_filename = secure_filename(video_file.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
            video_file.save(video_path)

            # Etapas do processamento
            audio_path = extract_audio(video_path)
            transcription = transcribe_audio(audio_path)
            dubbed_audio_path = generate_dubbed_audio(transcription, lang=idioma)
            output_video_path = replace_audio_in_video(video_path, dubbed_audio_path)

            print("Vídeo dublado gerado com sucesso.")
            return redirect(url_for('download', filename=output_video_path))

    except Exception as e:
        print("Erro durante o processamento:", str(e))
        return "Ocorreu um erro durante o processamento. Tente novamente mais tarde.", 500
