# src/voice_concierge/utils/cost_tracking.py
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import threading

from voice_concierge.utils.logging_utils import get_logger
from voice_concierge.config import settings

logger = get_logger(__name__)


class CostTracker:
    """Utility for tracking API usage and costs."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Implement as a singleton."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(CostTracker, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the cost tracker."""
        if self._initialized:
            return

        self.cost_log_path = os.path.join(
            os.path.dirname(settings.log_file),
            "costs",
            f"cost_log_{datetime.now().strftime('%Y%m%d')}.json",
        )

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.cost_log_path), exist_ok=True)

        # Initialize the cost log if it doesn't exist
        if not os.path.exists(self.cost_log_path):
            with open(self.cost_log_path, "w") as f:
                json.dump([], f)

        self._initialized = True
        logger.info(f"Cost tracker initialized with log path: {self.cost_log_path}")

    def log_api_call(
        self,
        service: str,
        operation: str,
        model: str,
        tokens_in: int = 0,
        tokens_out: int = 0,
        duration_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an API call with usage information.

        Args:
            service: Service name (e.g., 'openai', 'whisper')
            operation: Operation name (e.g., 'completion', 'transcription')
            model: Model name (e.g., 'o3', 'whisper-1')
            tokens_in: Number of input tokens
            tokens_out: Number of output tokens
            duration_ms: Call duration in milliseconds
            metadata: Additional metadata
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "service": service,
            "operation": operation,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "total_tokens": tokens_in + tokens_out,
        }

        if duration_ms is not None:
            entry["duration_ms"] = duration_ms

        if metadata:
            entry["metadata"] = metadata

        # Add cost estimate based on model
        # Note: These are placeholder rates and should be updated based on actual pricing
        rates = {
            "o3": {"input": 0.00001, "output": 0.00005},
            "whisper-1": {"minute": 0.006},
        }

        if model in rates:
            if "minute" in rates[model] and duration_ms is not None:
                # Calculate cost based on duration for models like Whisper
                minutes = duration_ms / 60000  # Convert ms to minutes
                entry["estimated_cost"] = minutes * rates[model]["minute"]
            else:
                # Calculate cost based on tokens for LLM models
                entry["estimated_cost"] = tokens_in * rates[model].get(
                    "input", 0
                ) + tokens_out * rates[model].get("output", 0)

        # Load existing log
        with open(self.cost_log_path, "r") as f:
            log = json.load(f)

        # Append new entry
        log.append(entry)

        # Save updated log
        with open(self.cost_log_path, "w") as f:
            json.dump(log, f, indent=2)

        logger.debug(f"Logged {service}/{operation} call with model {model}")

    def get_usage_summary(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get a summary of API usage and costs.

        Args:
            start_date: Optional start date (ISO format)
            end_date: Optional end date (ISO format)

        Returns:
            Dictionary with usage summary
        """
        # Load logs
        log_dir = os.path.dirname(self.cost_log_path)
        log_files = [
            f
            for f in os.listdir(log_dir)
            if f.startswith("cost_log_") and f.endswith(".json")
        ]

        all_entries = []
        for log_file in log_files:
            with open(os.path.join(log_dir, log_file), "r") as f:
                entries = json.load(f)
                all_entries.extend(entries)

        # Filter by date if provided
        if start_date:
            all_entries = [e for e in all_entries if e["timestamp"] >= start_date]

        if end_date:
            all_entries = [e for e in all_entries if e["timestamp"] <= end_date]

        # Calculate summaries
        total_cost = sum(e.get("estimated_cost", 0) for e in all_entries)
        total_tokens = sum(e.get("total_tokens", 0) for e in all_entries)

        # Group by service and model
        services = {}
        models = {}

        for entry in all_entries:
            service = entry["service"]
            model = entry["model"]
            cost = entry.get("estimated_cost", 0)

            if service not in services:
                services[service] = {"count": 0, "cost": 0}

            if model not in models:
                models[model] = {"count": 0, "cost": 0}

            services[service]["count"] += 1
            services[service]["cost"] += cost

            models[model]["count"] += 1
            models[model]["cost"] += cost

        return {
            "total_calls": len(all_entries),
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "services": services,
            "models": models,
            "start_date": start_date,
            "end_date": end_date,
            "generated_at": datetime.now().isoformat(),
        }
