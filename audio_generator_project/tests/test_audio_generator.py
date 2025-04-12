import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'audio_generator')))
from audio_generator import generate_audio

if __name__ == "__main__":
    sample_script = """
    Welcome to Code & Calm.
    I'm Mukesh Kumar, your guide in tech, yoga, and mindful productivity.
    Stay tuned for weekly videos to help you grow stronger and calmer.
    """
    generate_audio(sample_script, "sample_output.mp3")