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
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Logs
logging.basicConfig(level=logging.DEBUG)

# Verifica extensão permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rota principal
@app.route('/processar', methods=['POST'])
def processar():
    try:
        if 'video' not in request.files:
            return jsonify({"error": "Nenhum arquivo de vídeo enviado"}), 400

        video = request.files['video']
        if video.filename == '':
            return jsonify({"error": "Arquivo sem nome"}), 400

        if video and allowed_file(video.filename):
            filename = secure_filename(video.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video.save(video_path)

            # Caminho do áudio
            audio_filename = "audio_original.wav"
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)

            logging.info(f"Extraindo áudio do vídeo: {video_path}")

            try:
                command = ['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', audio_path, '-y']
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()

                if process.returncode != 0:
                    logging.error(f"Erro ao extrair áudio: {stderr.decode()}")
                    return jsonify({"error": "Erro ao extrair áudio"}), 500

                logging.info(f"Áudio extraído com sucesso: {audio_path}")
                return jsonify({"audio_file": audio_path, "success": "Áudio extraído com sucesso"})

            except Exception as e:
                logging.error(f"Erro ao rodar ffmpeg: {str(e)}")
                return jsonify({"error": "Erro ao processar áudio"}), 500

        else:
            return jsonify({"error": "Formato de vídeo inválido"}), 400

    except Exception as e:
        logging.error(f"Erro geral: {str(e)}")
        return jsonify({"error": "Erro interno no servidor"}), 500

# Inicialização da aplicação
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
