import os
import ffmpeg
import gradio as gr
import whisper
from deep_translator import GoogleTranslator
from gTTS import gTTS

model = whisper.load_model("tiny")

IDIOMAS_SUPORTADOS = {
    "Africâner": "af", "Albanês": "sq", "Alemão": "de", "Amárico": "am",
    "Árabe": "ar", "Armênio": "hy", "Azerbaijano": "az", "Bengali": "bn",
    "Bielorrusso": "be", "Bósnio": "bs", "Búlgaro": "bg", "Cantonês": "zh-TW",
    "Catalão": "ca", "Chinês": "zh-CN", "Chinês (simplificado)": "zh-CN",
    "Chinês (tradicional)": "zh-TW", "Coreano": "ko", "Croata": "hr",
    "Dinamarquês": "da", "Eslovaco": "sk", "Esloveno": "sl", "Espanhol": "es",
    "Filipino": "tl", "Finlandês": "fi", "Francês": "fr", "Georgiano": "ka",
    "Grego": "el", "Groenlandês": "kl", "Hindi": "hi", "Holandês": "nl",
    "Húngaro": "hu", "Indonésio": "id", "Inglês": "en", "Irlandês": "ga",
    "Islandês": "is", "Italiano": "it", "Japonês": "ja", "Latim": "la",
    "Luxemburguês": "lb", "Macedônio": "mk", "Malaio": "ms", "Mongol": "mn",
    "Nepalês": "ne", "Norueguês": "no", "Persa": "fa", "Polonês": "pl",
    "Português": "pt", "Romeno": "ro", "Russo": "ru", "Sérvio": "sr",
    "Somali": "so", "Tadjique": "tg", "Tagalo": "tl", "Tailandês": "th",
    "Tâmil": "ta", "Tcheco": "cs", "Télugo": "te", "Tibetano": "bo",
    "Tonganês": "to", "Turco": "tr", "Turcomeno": "tk", "Ucraniano": "uk",
    "Uzbeque": "uz", "Vietnamita": "vi"
}

def dublar_para_multiplos_idiomas(video_path, lista_idiomas):
    if not video_path or not lista_idiomas:
        return []
    
    audio_original = "temp_audio.wav"
    try:
        ffmpeg.input(video_path).output(audio_original, ac=1, ar='16000').overwrite_output().run(quiet=True)
    except Exception as e:
        print(f"Erro ao extrair áudio: {e}")
        return []
    
    result = model.transcribe(audio_original)
    texto_original = result.get('text', '')
    videos_gerados = []
    
    for nome_idioma in lista_idiomas:
        codigo_iso = IDIOMAS_SUPORTADOS[nome_idioma]
        try:
            texto_traduzido = GoogleTranslator(source='auto', target=codigo_iso).translate(texto_original)
            audio_dublado = f"temp_{codigo_iso}.mp3"
            tts = gTTS(text=texto_traduzido, lang=codigo_iso.lower(), slow=False)
            tts.save(audio_dublado)
            
            video_saida = f"dublado_{codigo_iso}.mp4"
            input_video = ffmpeg.input(video_path)
            input_audio = ffmpeg.input(audio_dublado)
            
            ffmpeg.output(input_video.video, input_audio, video_saida, vcodec='copy', acodec='aac').overwrite_output().run(quiet=True)
            videos_gerados.append(video_saida)
            
            if os.path.exists(audio_dublado):
                os.remove(audio_dublado)
        except Exception as err:
            print(f"Aviso no idioma {nome_idioma}: {err}")
            continue
            
    if os.path.exists(audio_original):
        os.remove(audio_original)
    
    return videos_gerados

interface = gr.Interface(
    fn=dublar_para_multiplos_idiomas,
    inputs=[
        gr.Video(label="Upload seu vídeo (Sem limite de tempo)"),
        gr.CheckboxGroup(
            choices=sorted(list(IDIOMAS_SUPORTADOS.keys())),
            value=[
                "Africâner", "Albanês", "Alemão", "Amárico", "Árabe", "Armênio",
                "Azerbaijano", "Bengali", "Bielorrusso", "Bósnio", "Búlgaro",
                "Cantonês", "Catalão", "Chinês", "Chinês (simplificado)",
                "Chinês (tradicional)", "Coreano", "Croata", "Dinamarquês",
                "Eslovaco", "Esloveno", "Espanhol", "Filipino", "Finlandês",
                "Francês", "Georgiano", "Grego", "Groenlandês", "Hindi",
                "Holandês", "Húngaro", "Indonésio", "Inglês", "Irlandês",
                "Islandês", "Italiano", "Japonês", "Latim", "Luxemburguês",
                "Macedônio", "Malaio", "Mongol", "Nepalês", "Norueguês",
                "Persa", "Polonês", "Português", "Romeno", "Russo", "Sérvio",
                "Somali", "Tadjique", "Tagalo", "Tailandês", "Tâmil", "Tcheco",
                "Télugo", "Tibetano", "Tonganês", "Turco", "Turcomeno",
                "Ucraniano", "Uzbeque", "Vietnamita"
            ],
            label="Selecione os idiomas para dublagem"
        )
    ],
    outputs=gr.Gallery(label="Galeria de Vídeos Dublados", columns=2),
    title="Dublador Automático IA - Multi-idiomas",
    description="Faça upload do seu vídeo e gere dublagens em múltiplos idiomas gratuitamente."
)

if __name__ == "__main__":
    interface.launch(server_name="0.0.0.0", server_port=7860)
