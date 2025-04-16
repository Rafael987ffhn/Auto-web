import os
import subprocess
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Definir diretório para upload
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Limitar o tipo de arquivos aceitos
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}

# Função para verificar extensões de arquivos permitidos
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rota para a página inicial (upload do vídeo)
@app.route('/')
def index():
    return render_template('index.html')

# Rota para processar o vídeo
@app.route('/processar', methods=['POST'])
def processar():
    if 'video' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    video_file = request.files['video']
    
    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if video_file and allowed_file(video_file.filename):
        filename = secure_filename(video_file.filename)
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video_file.save(video_path)

        # Extrair áudio do vídeo usando FFmpeg
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'audio_original.wav')
        try:
            # Executar o comando FFmpeg para extrair o áudio
            subprocess.run(
                ['ffmpeg', '-i', video_path, '-q:a', '0', '-map', 'a', audio_path, '-y'],
                check=True
            )
            return jsonify({'success': 'Audio extracted successfully', 'audio_file': audio_path}), 200
        except subprocess.CalledProcessError as e:
            return jsonify({'error': f'Error extracting audio: {e}'}), 500
    else:
        return jsonify({'error': 'Invalid file type. Only mp4, avi, mov, and mkv are allowed.'}), 400

# Rota para selecionar o idioma da dublagem
@app.route('/selecionar_idioma', methods=['POST'])
def selecionar_idioma():
    idioma = request.form.get('idioma')
    if not idioma:
        return jsonify({'error': 'Idioma não selecionado'}), 400
    
    # Aqui você pode adicionar a lógica para processar a dublagem, usando o idioma selecionado.
    # Exemplo de processamento fictício:
    return jsonify({'success': f'Idioma {idioma} selecionado para a dublagem.'}), 200

if __name__ == '__main__':
    app.run(debug=True)
