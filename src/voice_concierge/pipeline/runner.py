# src/voice_concierge/pipeline/runner.py
from typing import Dict, Any, Optional
import os
import json
from datetime import datetime

from agents import Runner, Agent
from voice_concierge.utils.logging_utils import get_logger
from voice_concierge.transcription.whisper_client import TranscribeAudio
from voice_concierge.summarization.agent import create_summarizer_agent
from voice_concierge.retrieval.retrieval_agent import create_retrieval_agent
from voice_concierge.presentation.slide_maker import SlideMaker

logger = get_logger(__name__)


class VoiceConciergeRunner:
    """Main pipeline runner for the Voice Concierge system."""

    def __init__(
        self,
        transcribe_tool: Optional[TranscribeAudio] = None,
        summarizer_agent: Optional[Agent] = None,
        slide_maker: Optional[SlideMaker] = None,
        trace_dir: Optional[str] = None,
    ):
        """Initialize the Voice Concierge pipeline runner.

        Args:
            transcribe_tool: Optional TranscribeAudio tool to use.
            summarizer_agent: Optional summarizer agent to use.
            slide_maker: Optional SlideMaker tool to use.
            trace_dir: Directory to save traces to. If None, traces are not saved.
        """
        # Create components if not provided
        self.transcribe_tool = transcribe_tool or TranscribeAudio()

        retrieval_agent = create_retrieval_agent()
        self.summarizer_agent = summarizer_agent or create_summarizer_agent(
            retrieval_agent
        )

        self.slide_maker = slide_maker or SlideMaker()

        # Setup trace directory
        self.trace_dir = trace_dir
        if trace_dir and not os.path.exists(trace_dir):
            os.makedirs(trace_dir)

        # Create the runner
        self.runner = Runner(
            agents=[self.transcribe_tool, self.summarizer_agent, self.slide_maker],
            strategy="chain",
            trace=bool(trace_dir),
        )

        logger.info("Voice Concierge pipeline initialized")

    def process_audio(
        self,
        audio_path: str,
        output_path: Optional[str] = None,
        save_transcript: bool = True,
        save_summary: bool = True,
    ) -> Dict[str, Any]:
        """Process audio file through the pipeline.

        Args:
            audio_path: Path to the audio file to process.
            output_path: Path for the output PowerPoint file.
            save_transcript: Whether to save the transcript to a file.
            save_summary: Whether to save the summary to a file.

        Returns:
            Dict containing paths to created files and status information.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Set default output path if not provided
        if not output_path:
            output_path = f"summary_{timestamp}.pptx"

        logger.info(f"Starting pipeline for audio: {audio_path}")
        logger.info(f"Output will be saved to: {output_path}")

        # Prepare trace file path if tracing is enabled
        trace_path = None
        if self.trace_dir:
            trace_path = os.path.join(self.trace_dir, f"trace_{timestamp}.html")
            logger.info(f"Trace will be saved to: {trace_path}")

        # Run the pipeline
        try:
            result = self.runner.run({"TranscribeAudio": {"file_path": audio_path}})

            # Save the trace if enabled
            if trace_path:
                self.runner.save_trace(trace_path)

            # Extract results
            transcript = result.get("TranscribeAudio", {}).get("result", {})
            summary = result.get("Summarizer", {}).get("result", {})
            pptx_path = result.get("SlideMaker", {}).get("result", "")

            # Save transcript if requested
            transcript_path = None
            if save_transcript and transcript:
                transcript_path = f"transcript_{timestamp}.json"
                with open(transcript_path, "w") as f:
                    json.dump(transcript, f, indent=2)
                logger.info(f"Transcript saved to: {transcript_path}")

            # Save summary if requested
            summary_path = None
            if save_summary and summary:
                summary_path = f"summary_{timestamp}.json"
                with open(summary_path, "w") as f:
                    json.dump(summary, f, indent=2)
                logger.info(f"Summary saved to: {summary_path}")

            # Prepare the result
            output = {
                "status": "success",
                "timestamp": timestamp,
                "audio_path": audio_path,
                "transcript_path": transcript_path,
                "summary_path": summary_path,
                "presentation_path": pptx_path,
                "trace_path": trace_path,
            }

            logger.info("Pipeline completed successfully")
            return output

        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise
