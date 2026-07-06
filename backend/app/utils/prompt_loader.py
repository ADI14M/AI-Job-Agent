import os
from pathlib import Path
from app.core.config import settings
from app.core.logger import system_logger

BASE_DIR = Path(__file__).resolve().parents[2]
PROMPTS_DIR = BASE_DIR / settings.PROMPTS_FOLDER

class PromptLoader:
    @staticmethod
    def load(filename: str, **kwargs) -> str:
        """
        Loads a prompt from a .txt file in the prompts directory and 
        formats it using the provided keyword arguments.
        """
        prompt_path = PROMPTS_DIR / filename
        
        if not prompt_path.exists():
            system_logger.error(f"Prompt file not found: {prompt_path}")
            raise FileNotFoundError(f"Prompt file {filename} not found in {PROMPTS_DIR}")
            
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                template = f.read()
                return template.format(**kwargs)
        except KeyError as e:
            system_logger.error(f"Missing formatting key {e} for prompt {filename}")
            raise ValueError(f"Missing formatting key {e} for prompt {filename}")
        except Exception as e:
            system_logger.error(f"Error loading prompt {filename}: {e}")
            raise
