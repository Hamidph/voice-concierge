# test.py
from dotenv import load_dotenv
import os
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent.absolute()

# Construct the path to the .env file
env_path = script_dir / ".env"

print(f"Looking for .env file at: {env_path}")

# Load the .env file
load_dotenv(dotenv_path=env_path)

print(
    "OPENAI_API_KEY:",
    os.getenv("OPENAI_API_KEY")[:5] + "..."
    if os.getenv("OPENAI_API_KEY")
    else "Not set",
)
print("WHISPER_MODEL:", os.getenv("WHISPER_MODEL", "Not set"))
print("LOG_FILE:", os.getenv("LOG_FILE", "Not set"))
