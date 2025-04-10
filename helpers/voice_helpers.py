from gtts import gTTS
import base64
from io import BytesIO

def generate_tts_audio(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return base64.b64encode(fp.read()).decode('utf-8')
