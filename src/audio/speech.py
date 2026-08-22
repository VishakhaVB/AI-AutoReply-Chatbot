import os
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Optional

class SpeechProcessor:
    """
    Processes audio speech using a local OpenAI Whisper model.
    
    Handles audio preprocessing via ffmpeg to match Whisper's sample rate and channel 
    requirements, performs text transcription, and detects the spoken language.
    """

    def __init__(self, model_size: str = "base") -> None:
        """
        Initializes the SpeechProcessor.
        
        Args:
            model_size (str): Size name of the local Whisper model (e.g., 'tiny', 'base', 'small').
                              Defaults to 'base'.
        """
        self.model_size = model_size
        self._model = None  # Lazily loaded on demand to speed up class initialization

    def _load_model(self) -> any:
        """
        Imports and loads the local Whisper model if it hasn't been loaded already.
        
        Returns:
            whisper.Whisper: The loaded Whisper model instance.
            
        Raises:
            RuntimeError: If whisper import or model loading fails.
        """
        if self._model is None:
            logging.info(f"Loading local OpenAI Whisper model '{self.model_size}'...")
            try:
                import whisper
                self._model = whisper.load_model(self.model_size)
                logging.info("Whisper model loaded successfully.")
            except ImportError as e:
                logging.error("Failed to import whisper. Ensure 'openai-whisper' is installed in the env.")
                raise RuntimeError(
                    "Required package 'openai-whisper' is missing. "
                    "Install it via: pip install openai-whisper"
                ) from e
            except Exception as e:
                logging.error(f"Whisper model loading failed: {e}", exc_info=True)
                raise RuntimeError(f"Whisper model loading failed: {e}") from e
        return self._model

    def preprocess_audio(self, audio_path: str) -> str:
        """
        Converts input audio (MP3, WAV, OGG) to standard 16kHz mono WAV format using ffmpeg.
        
        Whisper performs best with 16kHz mono audio.
        
        Args:
            audio_path (str): Filepath of the input audio file.
            
        Returns:
            str: Absolute filepath of the preprocessed WAV file.
            
        Raises:
            FileNotFoundError: If the input file is missing.
            ValueError: If the file format is unsupported.
            RuntimeError: If ffmpeg is missing from PATH or conversion fails.
        """
        path = Path(audio_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Audio file not found at path: '{audio_path}'")

        ext = path.suffix.lower()
        if ext not in [".mp3", ".wav", ".ogg"]:
            raise ValueError(
                f"Unsupported audio format: '{ext}'. "
                "Supported formats are MP3, WAV, and OGG."
            )

        # Output filepath in the system temp directory
        temp_dir = tempfile.gettempdir()
        output_filename = f"{path.stem}_preprocessed_16khz.wav"
        output_path = Path(temp_dir) / output_filename

        # Command: convert to WAV, force 16kHz sample rate, force mono channel, overwrite existing
        command = [
            "ffmpeg",
            "-y",
            "-i", str(path),
            "-ar", "16000",
            "-ac", "1",
            str(output_path)
        ]

        try:
            logging.info(f"Preprocessing audio using ffmpeg: {audio_path}")
            # Run ffmpeg subprocess silently
            subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            logging.info(f"Audio preprocessed successfully: {output_path}")
            return str(output_path)
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode().strip()
            logging.error(f"ffmpeg conversion failed: {error_message}")
            raise RuntimeError(f"ffmpeg conversion failed: {error_message}") from e
        except FileNotFoundError as e:
            logging.error("ffmpeg executable not found in system environment PATH.")
            raise RuntimeError(
                "ffmpeg executable not found. Please install ffmpeg and add it to your PATH."
            ) from e

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes the speech in an audio file to text using Whisper.
        
        Args:
            audio_path (str): Filepath of the input audio file (MP3, WAV, OGG).
            
        Returns:
            str: Clean transcribed text content.
            
        Raises:
            RuntimeError: If preprocessing or transcription fails.
        """
        preprocessed_path = self.preprocess_audio(audio_path)
        model = self._load_model()

        try:
            logging.info(f"Running Whisper transcription for: {preprocessed_path}")
            result = model.transcribe(preprocessed_path)
            transcription = result.get("text", "").strip()
            
            # Clean up the generated temp WAV file
            self._cleanup_temp_file(preprocessed_path)
            return transcription
        except Exception as e:
            logging.error(f"Transcription failed: {e}", exc_info=True)
            self._cleanup_temp_file(preprocessed_path)
            raise RuntimeError(f"Transcription execution failed: {e}") from e

    def detect_language(self, audio_path: str) -> str:
        """
        Detects the spoken language code in the audio file.
        
        Args:
            audio_path (str): Filepath of the input audio file (MP3, WAV, OGG).
            
        Returns:
            str: Detected two-character ISO language code (e.g. 'en', 'hi', 'es').
            
        Raises:
            RuntimeError: If language detection fails.
        """
        preprocessed_path = self.preprocess_audio(audio_path)
        model = self._load_model()

        try:
            import whisper
            logging.info(f"Detecting spoken language for: {preprocessed_path}")
            
            # Load and pad/trim to exactly 30 seconds for language header scan
            audio = whisper.load_audio(preprocessed_path)
            audio = whisper.pad_or_trim(audio)
            
            # Generate spectrogram representation
            mel = whisper.log_mel_spectrogram(audio).to(model.device)
            
            # Extract language probabilities
            _, probabilities = model.detect_language(mel)
            detected_lang = max(probabilities, key=probabilities.get)
            
            logging.info(f"Language detection completed. Detected code: '{detected_lang}'")
            self._cleanup_temp_file(preprocessed_path)
            return detected_lang
        except Exception as e:
            logging.error(f"Language detection failed: {e}", exc_info=True)
            self._cleanup_temp_file(preprocessed_path)
            raise RuntimeError(f"Language detection execution failed: {e}") from e

    def _cleanup_temp_file(self, file_path: str) -> None:
        """
        Safely deletes a temporary file if it exists.
        
        Args:
            file_path (str): Path of the file to remove.
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logging.debug(f"Removed temporary file: {file_path}")
        except Exception as e:
            logging.warning(f"Could not clean up temporary file '{file_path}': {e}")
