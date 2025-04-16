import whisper
from gtts import gTTS
import subprocess
import os

# Função para extrair áudio do vídeo com ffmpeg
def extract_audio(video_path, audio_path):
    try:
        subprocess.run(["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"], check=True)
        print("🎧 Áudio extraído com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao extrair áudio: {e}")
        raise

# Função para transcrição de áudio usando Whisper
def transcribe_audio(audio_path):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        return result["text"]
    except Exception as e:
        print(f"❌ Erro na transcrição do áudio: {e}")
        raise

# Função para gerar áudio dublado com gTTS
def generate_dubbed_audio(text, dubbed_audio_path):
    try:
        tts = gTTS(text=text, lang='pt-br')
        tts.save(dubbed_audio_path)
        print("🎤 Áudio dublado gerado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao gerar áudio dublado: {e}")
        raise

# Função para substituir o áudio original pelo dublado no vídeo
def replace_audio_in_video(video_path, dubbed_audio_path, output_path):
    try:
        subprocess.run([
            "ffmpeg", "-i", video_path, "-i", dubbed_audio_path, "-c:v", "copy",
            "-map", "0:v:0", "-map", "1:a:0", "-shortest", output_path, "-y"
        ], check=True)
        print(f"🎬 Vídeo dublado salvo em: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao substituir áudio no vídeo: {e}")
        raise

# Função principal
def dub_video(video_path, audio_path, dubbed_audio_path, output_path):
    # 1. Extrair o áudio do vídeo
    extract_audio(video_path, audio_path)
    
    # 2. Transcrição com Whisper
    transcription = transcribe_audio(audio_path)
    print("📝 Transcrição:", transcription)
    
    # 3. Gerar áudio dublado com gTTS
    generate_dubbed_audio(transcription, dubbed_audio_path)
    
    # 4. Substituir áudio original pelo dublado
    replace_audio_in_video(video_path, dubbed_audio_path, output_path)
    
    # 5. Limpeza de arquivos temporários
    os.remove(audio_path)
    os.remove(dubbed_audio_path)
    print("🧹 Arquivos temporários removidos com sucesso!")

# Caminhos dos arquivos
video_path = "video.mp4"
audio_path = "audio_original.wav"
dubbed_audio_path = "audio_dublado.mp3"
output_path = "video_dublado.mp4"

# Iniciar o processo de dublagem
dub_video(video_path, audio_path, dubbed_audio_path, output_path)
