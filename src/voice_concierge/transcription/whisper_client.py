# src/voice_concierge/transcription/whisper_client.py
from typing import BinaryIO, Optional, Dict, Any
import os
from tenacity import retry, stop_after_attempt, wait_exponential
import openai
from agents import Tool

from voice_concierge.config import settings
from voice_concierge.utils.logging_utils import get_logger

logger = get_logger(__name__)


class TranscribeAudio(Tool):
    """Tool for transcribing audio using OpenAI's Whisper model."""

    name = "transcribe_audio"
    description = "Transcribe audio files to text with optional diarization."

    def __init__(self, model: Optional[str] = None):
        """Initialize the transcription tool.

        Args:
            model: The Whisper model to use. Defaults to config setting.
        """
        self.model = model or settings.whisper_model
        logger.info(f"Initialized TranscribeAudio with model: {self.model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def _call_whisper_api(self, file_obj: BinaryIO) -> Dict[str, Any]:
        """Call Whisper API with retry logic.

        Args:
            file_obj: File object containing audio data.

        Returns:
            Dict containing transcription response.
        """
        logger.debug(f"Calling Whisper API with model: {self.model}")
        try:
            response = openai.audio.transcriptions.create(
                model=self.model, file=file_obj, response_format="verbose_json"
            )
            return response
        except Exception as e:
            logger.error(f"Error calling Whisper API: {str(e)}")
            raise

    def run(self, file_path: str, diarize: bool = False) -> Dict[str, Any]:
        """Transcribe audio file to text.

        Args:
            file_path: Path to audio file.
            diarize: Whether to enable speaker diarization.

        Returns:
            Dict containing transcription text and metadata.
        """
        logger.info(f"Transcribing audio file: {file_path}")

        if not os.path.exists(file_path):
            error_msg = f"Audio file not found: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        with open(file_path, "rb") as audio_file:
            response = self._call_whisper_api(audio_file)

        # Process response to extract text and segments
        result = {
            "text": response.text,
            "segments": response.segments if hasattr(response, "segments") else [],
            "language": response.language if hasattr(response, "language") else None,
        }

        logger.info(f"Transcription complete: {len(result['text'])} characters")
        return result
