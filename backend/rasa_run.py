#!/usr/bin/env python3
"""
Script to run the Rasa chatbot server.
"""

import os
import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_rasa_installation():
    """Check if Rasa is installed."""
    try:
        result = subprocess.run(['rasa', '--version'], capture_output=True, text=True)
        logger.info(f"Rasa version: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
        logger.error("Rasa is not installed. Please install it with: pip install rasa")
        return False

def train_model():
    """Train the Rasa model if not already trained."""
    models_dir = Path('models')
    if not models_dir.exists() or not any(models_dir.glob('*.tar.gz')):
        logger.info("Training Rasa model...")
        try:
            result = subprocess.run(['rasa', 'train'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Model training completed successfully")
            else:
                logger.error(f"Model training failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error during training: {e}")
            return False
    else:
        logger.info("Model already exists, skipping training")
    return True

def run_rasa_server():
    """Run the Rasa server."""
    logger.info("Starting Rasa server...")
    try:
        # Run Rasa server with action server
        subprocess.run(['rasa', 'run', '--enable-api', '--cors', '*'], check=True)
    except KeyboardInterrupt:
        logger.info("Rasa server stopped by user")
    except Exception as e:
        logger.error(f"Error running Rasa server: {e}")
        return False
    return True

def main():
    """Main function to set up and run Rasa server."""
    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    logger.info("Setting up Rasa chatbot server...")

    # Check if Rasa is installed
    if not check_rasa_installation():
        sys.exit(1)

    # Train model if needed
    if not train_model():
        sys.exit(1)

    # Run the server
    if not run_rasa_server():
        sys.exit(1)

if __name__ == "__main__":
    main()