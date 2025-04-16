import os
import subprocess
from flask import Flask, request, jsonify
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurar o diretório para uploads e log de erros
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Configuração de logs
logging.basicConfig(level=logging.DEBUG)

# Função para verificar se o arquivo tem uma extensão permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/processar', methods=['POST'])
def processar():
    try:
        if 'video' not in request.files:
            return jsonify({"error": "No video file part"}), 400
        video = request.files['video']
        if video.filename == '':
            return jsonify({"error": "No selected file"}), 400
        if video and allowed_file(video.filename):
            filename = secure_filename(video.filename)
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            video.save(video_path)

            # Extração do áudio
            audio_filename = "audio_original.wav"
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
            
            logging.info(f"Extrair áudio do vídeo: {video_path}")
            
            try:
                # Comando para extrair o áudio usando ffmpeg
                command = ['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', audio_path, '-y']
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()

                if process.returncode != 0:
                    logging.error(f"Erro ao extrair áudio: {stderr.decode()}")
                    return jsonify({"error": "Erro ao extrair áudio"}), 500
                
                logging.info(f"Áudio extraído com sucesso para: {audio_path}")
                
                # Retorno de sucesso
                return jsonify({"audio_file": audio_path, "success": "Audio extracted successfully"})

            except Exception as e:
                logging.error(f"Erro no subprocesso ffmpeg: {str(e)}")
                return jsonify({"error": "Erro no processamento do áudio"}), 500

        else:
            return jsonify({"error": "Invalid file format"}), 400
    
    except Exception as e:
        logging.error(f"Erro no processamento geral: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
