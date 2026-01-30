"""
TTS Engine for IL CUSTODE DEL CAVEAU
Text-to-Speech with viseme generation for lip-sync
"""
import pyttsx3
import base64
import io
import os
import tempfile
import wave
import struct
import math
from typing import Dict, List, Tuple
import numpy as np

# Viseme mapping for Italian phonemes (simplified)
# Maps approximate phoneme sounds to viseme indices
VISEME_MAP = {
    'a': 'viseme_aa',      # Open mouth
    'e': 'viseme_E',       # Mid open
    'i': 'viseme_I',       # Smile
    'o': 'viseme_O',       # Round lips
    'u': 'viseme_U',       # Pursed lips
    'p': 'viseme_PP',      # Lips together
    'b': 'viseme_PP',
    'm': 'viseme_PP',
    'f': 'viseme_FF',      # Lower lip under teeth
    'v': 'viseme_FF',
    't': 'viseme_DD',      # Tongue behind teeth
    'd': 'viseme_DD',
    'n': 'viseme_nn',
    'l': 'viseme_DD',
    's': 'viseme_SS',      # Teeth together
    'z': 'viseme_SS',
    'r': 'viseme_RR',      # Tongue curl
    'k': 'viseme_kk',      # Back of mouth
    'g': 'viseme_kk',
    'c': 'viseme_kk',
    'ch': 'viseme_CH',     # Pucker
    'sh': 'viseme_CH',
}

# Ready Player Me morphTarget names
RPM_VISEMES = [
    'viseme_sil',   # 0 - Silence
    'viseme_PP',    # 1 - p, b, m
    'viseme_FF',    # 2 - f, v
    'viseme_TH',    # 3 - th
    'viseme_DD',    # 4 - t, d, n, l
    'viseme_kk',    # 5 - k, g
    'viseme_CH',    # 6 - ch, sh
    'viseme_SS',    # 7 - s, z
    'viseme_nn',    # 8 - n
    'viseme_RR',    # 9 - r
    'viseme_aa',    # 10 - a
    'viseme_E',     # 11 - e
    'viseme_I',     # 12 - i
    'viseme_O',     # 13 - o
    'viseme_U',     # 14 - u
]


class TTSEngine:
    def __init__(self):
        """Initialize the TTS engine."""
        self.engine = pyttsx3.init()
        # Set Italian voice if available
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'italian' in voice.name.lower() or 'it' in voice.id.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Set properties for dramatic effect
        self.engine.setProperty('rate', 140)  # Slower, more menacing
        self.engine.setProperty('volume', 1.0)
    
    def generate_audio(self, text: str) -> Tuple[str, List[Dict]]:
        """
        Generate audio from text and create corresponding viseme data.
        
        Args:
            text: The text to convert to speech
            
        Returns:
            Tuple of (base64_audio, viseme_data)
        """
        # Create temp file for audio
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_path = f.name
        
        try:
            # Generate audio file
            self.engine.save_to_file(text, temp_path)
            self.engine.runAndWait()
            
            # Read the generated audio
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Convert to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Generate viseme data based on text analysis
            visemes = self._generate_visemes(text, temp_path)
            
            return audio_base64, visemes
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def _generate_visemes(self, text: str, audio_path: str) -> List[Dict]:
        """
        Generate viseme timing data for lip-sync.
        Uses text analysis to estimate phoneme timing.
        
        Args:
            text: The spoken text
            audio_path: Path to the audio file for duration
            
        Returns:
            List of viseme events with timing
        """
        visemes = []
        
        # Get audio duration
        try:
            with wave.open(audio_path, 'rb') as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                duration = frames / float(rate)
        except Exception:
            # Estimate duration based on text length
            duration = len(text) * 0.08  # ~80ms per character
        
        # Clean text for phoneme analysis
        text_lower = text.lower()
        
        # Calculate time per character
        chars = [c for c in text_lower if c.isalpha() or c == ' ']
        if not chars:
            return [{"time": 0, "viseme": "viseme_sil", "weight": 0.0}]
        
        time_per_char = duration / len(chars)
        
        current_time = 0.0
        prev_viseme = 'viseme_sil'
        
        for char in chars:
            if char == ' ':
                # Brief pause on spaces
                visemes.append({
                    "time": round(current_time, 3),
                    "viseme": "viseme_sil",
                    "weight": 0.3
                })
            elif char in VISEME_MAP:
                viseme = VISEME_MAP[char]
                # Add transition smoothing
                weight = 0.8 if viseme != prev_viseme else 0.6
                visemes.append({
                    "time": round(current_time, 3),
                    "viseme": viseme,
                    "weight": weight
                })
                prev_viseme = viseme
            else:
                # Default to open mouth for unknown chars
                visemes.append({
                    "time": round(current_time, 3),
                    "viseme": "viseme_aa",
                    "weight": 0.5
                })
            
            current_time += time_per_char
        
        # End with silence
        visemes.append({
            "time": round(duration, 3),
            "viseme": "viseme_sil",
            "weight": 0.0
        })
        
        return visemes
    
    def get_audio_duration(self, audio_base64: str) -> float:
        """Get duration of base64 encoded audio."""
        try:
            audio_data = base64.b64decode(audio_base64)
            with io.BytesIO(audio_data) as f:
                with wave.open(f, 'rb') as wav:
                    frames = wav.getnframes()
                    rate = wav.getframerate()
                    return frames / float(rate)
        except Exception:
            return 0.0


# Singleton instance
_tts_engine = None

def get_tts_engine() -> TTSEngine:
    """Get or create the TTS engine singleton."""
    global _tts_engine
    if _tts_engine is None:
        _tts_engine = TTSEngine()
    return _tts_engine


def generate_speech(text: str) -> Tuple[str, List[Dict]]:
    """
    Convenience function to generate speech and visemes.
    
    Args:
        text: Text to speak
        
    Returns:
        Tuple of (base64_audio, viseme_data)
    """
    engine = get_tts_engine()
    return engine.generate_audio(text)
