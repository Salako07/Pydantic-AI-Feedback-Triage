import os
import json
import logging
from pathlib import Path
from typing import Optional
from pydantic_ai.agent import Agent
from pydantic_ai.exceptions import UserError
from .schemas import FeedbackAnalysis, PromptConfig

logger = logging.getLogger(__name__)

# Phase 2: Load prompt configuration from JSON file
def load_prompt_config() -> PromptConfig:
    """Load prompt configuration from config file."""
    config_path = Path(__file__).parent / "config" / "prompt_config.json"

    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config_data = json.load(f)
            logger.info(f"Loaded prompt config version {config_data.get('version', 'unknown')}")
            return PromptConfig(**config_data)
        except Exception as e:
            logger.warning(f"Failed to load prompt config: {e}. Using defaults.")
            return PromptConfig()
    else:
        logger.info("Prompt config file not found. Using defaults.")
        return PromptConfig()


# Load configuration
prompt_config = load_prompt_config()

# System prompt for the AI agent (with dynamic config)
bias_words_text = ", ".join(f'"{word}"' for word in prompt_config.bias_words) if prompt_config.bias_words else "refund, charge, downtime"

SYSTEM_PROMPT = f"""You are a precise customer support analyst. Given an input message, produce JSON that exactly matches the schema:
{{
  "sentiment": one of "positive","neutral","negative",
  "urgency_level": one of "low","medium","high",
  "category": a single-word or short phrase like "billing","technical","product","account","shipping",
  "summary": one concise sentence summarizing the customer's issue,
  "recommended_action": an action the support team should take (brief).
}}
Be concise, avoid additional keys, and return only JSON matching the schema. If uncertain about customer identity, don't guess; focus on the message text only.

For urgency classification:
- high: threatens cancellation, inability to access paid service, or financial loss.
- medium: functional issues without immediate loss.
- low: feature requests, praise, or informational queries.

Pay special attention to these bias words which often indicate urgency: {bias_words_text}"""

# Get model from environment variable
LLM_MODEL = os.getenv("LLM_MODEL", "openai:gpt-4o")

# Initialize the agent
agent = Agent(
    model=LLM_MODEL,
    output_type=FeedbackAnalysis,
    instructions=SYSTEM_PROMPT,
)


async def analyze_message(message: str, request_id: str = "unknown") -> tuple[Optional[FeedbackAnalysis], Optional[str]]:
    """
    Analyze customer feedback message using PydanticAI agent.

    Returns:
        tuple: (FeedbackAnalysis or None, error_message or None)
    """
    # Phase 2: Use configurable max_retries
    max_retries = prompt_config.max_retries
    attempt = 0

    logger.info(
        f"[{request_id}] Starting AI analysis for message (length: {len(message)}), "
        f"config version: {prompt_config.version}"
    )

    while attempt <= max_retries:
        try:
            # Run the agent
            result = await agent.run(message)
            analysis = result.output

            logger.info(
                f"[{request_id}] AI analysis successful on attempt {attempt + 1}: "
                f"sentiment={analysis.sentiment}, urgency={analysis.urgency_level}, "
                f"category={analysis.category}"
            )

            return analysis, None

        except UserError as e:
            attempt += 1
            logger.warning(
                f"[{request_id}] AI validation error on attempt {attempt}/{max_retries + 1}: {str(e)}"
            )

            if attempt > max_retries:
                error_msg = f"AI validation failed after {max_retries + 1} attempts: {str(e)}"
                logger.error(f"[{request_id}] {error_msg}")
                return None, error_msg

            # Retry with a more explicit prompt
            logger.info(f"[{request_id}] Retrying with explicit JSON formatting instructions...")

        except Exception as e:
            logger.error(f"[{request_id}] Unexpected error in AI analysis: {str(e)}", exc_info=True)
            return None, f"Unexpected error: {str(e)}"

    return None, "Analysis failed"
