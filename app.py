from flask import Flask, render_template, request, jsonify
import whisper
import os
from gtts import gTTS
import ffmpeg
import traceback

app = Flask(__name__)

# Carregando o modelo do Whisper
model = whisper.load_model("base")  # Modelo 'base' do Whisper, ou outro modelo desejado

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar():
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado.'}), 400

        video_file = request.files['video']

        # Salva o arquivo temporariamente
        video_path = os.path.join('/tmp', video_file.filename)
        video_file.save(video_path)

        # Usar FFmpeg para extrair o áudio do vídeo
        audio_path = '/tmp/audio.wav'
        print(f"Processando o vídeo para extrair o áudio: {video_path}")
        ffmpeg.input(video_path).output(audio_path, loglevel='debug').run()

        # Usar o modelo Whisper para transcrever o áudio
        print("Transcrevendo o áudio...")
        result = model.transcribe(audio_path)
        texto_transcrito = result['text']
        print(f"Texto transcrito: {texto_transcrito}")

        # Converter o texto transcrito para áudio com gTTS
        print("Convertendo texto para áudio dublado...")
        tts = gTTS(texto_transcrito, lang='pt')
        tts_path = '/tmp/audio_dublado.mp3'
        tts.save(tts_path)

        # Deletar o arquivo de vídeo temporário
        os.remove(video_path)

        # Retornar o caminho do áudio gerado
        return jsonify({'audio_dublado': tts_path})

    except Exception as e:
        # Captura e exibe o erro com traceback para depuração
        error_message = str(e)
        error_traceback = traceback.format_exc()
        print(f"Erro: {error_message}")
        print(f"Traceback: {error_traceback}")
        return jsonify({'error': 'Erro interno do servidor, tente novamente mais tarde.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
