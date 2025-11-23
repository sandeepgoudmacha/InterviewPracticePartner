"""Audio processing utilities."""
import whisper

# Load Whisper model
model = whisper.load_model('base')


def transcribe(audio_path: str) -> str:
    """
    Transcribe audio file to text.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Transcribed text
    """
    result = model.transcribe(audio_path)
    return result['text']
