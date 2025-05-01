# tests/conftest.py
import os
import tempfile
import pytest
from unittest.mock import MagicMock, patch

from voice_concierge.config import Settings


@pytest.fixture
def test_audio_path():
    """Fixture providing path to a test audio file."""
    # This is a placeholder - in a real implementation, you'd include a small test audio file
    return os.path.join(os.path.dirname(__file__), "fixtures", "test_audio.mp3")


@pytest.fixture
def mock_openai_whisper():
    """Fixture providing a mock for the OpenAI Whisper API."""
    with patch("openai.audio.transcriptions.create") as mock:
        mock.return_value = MagicMock(
            text="This is a test transcription.",
            segments=[{"start": 0, "end": 2, "text": "This is a test transcription."}],
            language="en",
        )
        yield mock


@pytest.fixture
def mock_vector_store():
    """Fixture providing a mock vector store."""
    mock = MagicMock()
    mock.search.return_value = [
        {
            "content": "This is a test document content.",
            "metadata": {"source": "test_document.pdf"},
        }
    ]
    return mock


@pytest.fixture
def mock_settings():
    """Fixture providing test settings."""
    return Settings(
        openai_api_key="test_key",
        whisper_model="whisper-1",
        vector_store_path=tempfile.mkdtemp(),
        log_level="DEBUG",
        log_file=os.path.join(tempfile.mkdtemp(), "test.log"),
    )


@pytest.fixture
def sample_transcript():
    """Fixture providing a sample transcript."""
    return {
        "text": "This is a sample meeting transcript discussing project Alpha.",
        "segments": [
            {
                "start": 0,
                "end": 5,
                "text": "This is a sample meeting transcript discussing project Alpha.",
            }
        ],
        "language": "en",
    }


@pytest.fixture
def sample_summary():
    """Fixture providing a sample summary."""
    return {
        "title": "Project Alpha Discussion",
        "slides": [
            {
                "title": "Project Overview",
                "bullets": [
                    {"text": "Alpha is a new initiative launching in Q3", "level": 0},
                    {"text": "Budget approved for $500k", "level": 0},
                    {"text": "Timeline: 6 months to MVP", "level": 0},
                ],
            }
        ],
    }
