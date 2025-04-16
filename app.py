from flask import Flask, render_template, request, send_file
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'static/videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    video = request.files['video']
    idioma = request.form['idioma']

    if not video:
        return "Nenhum vídeo enviado", 400

    # Salvar vídeo temporariamente
    caminho_video = os.path.join(UPLOAD_FOLDER, video.filename)
    video.save(caminho_video)

    # Aqui você chamaria a função principal para dublar (vou simular)
    nome_saida = f"dublado_{video.filename}"
    caminho_saida = os.path.join(PROCESSED_FOLDER, nome_saida)

    # Simulação da dublagem: copiar o vídeo original
    # No seu projeto, substitua essa parte com a função de dublagem real
    import shutil
    shutil.copy(caminho_video, caminho_saida)

    video_url = f"/static/videos/{nome_saida}"
    return render_template('index.html', video_url=video_url)
