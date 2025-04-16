import os
import subprocess
import logging
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurações
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Cria a pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configuração de logs
logging.basicConfig(level=logging.DEBUG)

# Verifica se a extensão do arquivo é permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/processar', methods=['POST'])
def processar():
    try:
        if 'video' not in request.files:
            return jsonify({"error": "Nenhum arquivo de vídeo enviado"}), 400
        
        video = request.files['video']
        if video.filename == '':
            return jsonify({"error": "Nome do arquivo vazio"}), 400
        
        if video and allowed_file(video.filename):
            filename = secure_filename(video.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video.save(video_path)

            # Caminho do áudio extraído
            audio_filename = "audio_original.wav"
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
            
            logging.info(f"Extraindo áudio do vídeo: {video_path}")
            
            # Comando FFmpeg para extrair o áudio
            command = ['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', audio_path, '-y']
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                logging.error(f"Erro ao extrair áudio: {stderr.decode()}")
                return jsonify({"error": "Erro ao extrair áudio"}), 500
            
            logging.info(f"Áudio extraído com sucesso para: {audio_path}")
            return jsonify({
                "video_file": filename,
                "audio_file": audio_filename,
                "success": "Áudio extraído com sucesso"
            })

        else:
            return jsonify({"error": "Formato de arquivo inválido"}), 400

    except Exception as e:
        logging.error(f"Erro no processamento: {str(e)}")
        return jsonify({"error": "Erro interno no servidor"}), 500

if __name__ == '__main__':
    # Para a Render, use host='0.0.0.0' e
