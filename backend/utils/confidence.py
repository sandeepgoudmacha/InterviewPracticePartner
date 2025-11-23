"""Confidence scoring utilities."""
import librosa
import numpy as np


def get_confidence_score(audio_path: str) -> float:
    """
    Calculate confidence score based on audio characteristics.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    try:
        # Load audio
        y, sr = librosa.load(audio_path)

        # 1. Duration Check
        # If audio is too short (< 1s), it's likely a one-word answer or noise.
        duration = librosa.get_duration(y=y, sr=sr)
        if duration < 1.0:
            return 0.2

        # --- METRIC 1: FLUENCY (Silence Detection) ---
        # Split audio into non-silent intervals (top_db=25 is standard for voice)
        non_silent_intervals = librosa.effects.split(y, top_db=25)
        
        if len(non_silent_intervals) == 0:
            return 0.1 # Pure silence = Low confidence

        # Calculate total duration of actual speech
        active_time = sum([end - start for start, end in non_silent_intervals]) / sr
        
        # Fluency Ratio: active_time / total_duration
        # If you pause a lot (say "um..."), this ratio drops.
        # Perfect continuous speech = 1.0. Frequent pausing < 0.5.
        fluency_ratio = active_time / duration
        
        # Normalize Fluency: < 0.4 is bad (0 score), > 0.8 is good (1.0 score)
        fluency_score = np.clip((fluency_ratio - 0.4) / (0.8 - 0.4), 0.0, 1.0)


        # --- METRIC 2: VOLUME (RMS Energy) ---
        # Analyze only the non-silent parts to avoid silence dragging down the score
        y_active = np.concatenate([y[start:end] for start, end in non_silent_intervals])
        rms_feature = librosa.feature.rms(y=y_active)
        rms = np.mean(rms_feature) if len(rms_feature) > 0 else 0.0
        
        # Normal conversational RMS is usually around 0.02 to 0.05
        # If rms < 0.01, it's whispering/mumbling (Score -> 0).
        # If rms > 0.05, it's loud and clear (Score -> 1).
        volume_score = np.clip((rms - 0.01) / (0.05 - 0.01), 0.0, 1.0)


        # --- METRIC 3: PACE (Tempo) ---
        try:
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        except Exception:
            tempo = 120.0 # Fallback average

        # Ideal conversational pace is ~110-130 BPM. 
        # Penalize if too slow (< 90) or too fast (> 160)
        if tempo < 90:
            pace_score = 0.6  # Hesitant/Slow
        elif tempo > 160:
            pace_score = 0.7  # Rushed/Nervous
        else:
            pace_score = 1.0  # Confident Pace


        # --- FINAL WEIGHTED SCORE ---
        # Fluency (hesitation) is the biggest indicator of confidence (40%)
        # Volume (clarity) is next (40%)
        # Pace is minor (20%)
        confidence = (0.4 * fluency_score) + (0.4 * volume_score) + (0.2 * pace_score)

        # Ensure safe float return
        confidence = float(np.clip(confidence, 0.0, 1.0))
        return round(confidence, 2)

    except Exception as e:
        print(f"[Confidence Error] {e}")
        return 0.5  # fallback