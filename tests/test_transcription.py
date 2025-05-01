# tests/test_transcription.py
import pytest
from unittest.mock import patch, MagicMock

from voice_concierge.transcription.whisper_client import TranscribeAudio


def test_transcribe_audio_init():
    """Test TranscribeAudio initialization."""
    tool = TranscribeAudio(model="test-model")
    assert tool.model == "test-model"

    # Test with default model
    with patch(
        "voice_concierge.transcription.whisper_client.settings",
        MagicMock(whisper_model="default-model"),
    ):
        tool = TranscribeAudio()
        assert tool.model == "default-model"


def test_transcribe_audio_file_not_found():
    """Test TranscribeAudio with non-existent file."""
    tool = TranscribeAudio()
    with pytest.raises(FileNotFoundError):
        tool.run("non_existent_file.mp3")


def test_transcribe_audio_success(mock_openai_whisper, test_audio_path):
    """Test successful transcription."""
    tool = TranscribeAudio()
    result = tool.run(test_audio_path)

    assert "text" in result
    assert result["text"] == "This is a test transcription."
    assert "segments" in result
    assert "language" in result
    assert result["language"] == "en"

    # Verify the API was called correctly
    mock_openai_whisper.assert_called_once()
