from gtts import gTTS
import os
from config import LANGUAGE, SLOW_MODE

def generate_audio(script_text, output_filename="output_audio.mp3"):
    tts = gTTS(text=script_text, lang=LANGUAGE, slow=SLOW_MODE)
    output_path = os.path.join(os.path.dirname(__file__), "output", output_filename)
    tts.save(output_path)
    print(f"Audio file saved at: {output_path}")