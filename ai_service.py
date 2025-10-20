import google.generativeai as genai
import os
from typing import List
import logging
from dotenv import load_dotenv

load_dotenv()


def load_api_key():
    """Load API key from environment variable"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    return api_key


# Configure the API key
genai.configure(api_key=load_api_key())

# Create the model with improved configuration
generation_config = {
    "temperature": 0.8,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,  # Sufficient for Instagram captions
    "response_mime_type": "text/plain",
}

# Set up logger
logger = logging.getLogger(__name__)

# Initialize model
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",  # Using more stable model
    generation_config=generation_config,
)


def generate_text_with_gemini(prompt: str, max_tokens: int = 1024, include_web_search: bool = True) -> str:
    """
    Generate text using Gemini AI

    Args:
        prompt (str): The prompt to send to Gemini
        max_tokens (int): Maximum number of tokens in response
        include_web_search (bool): Whether to include web search for recent trends

    Returns:
        str: Generated text from Gemini

    Raises:
        Exception: If API call fails
    """
    try:
        # CRITICAL: Keep prompts SHORT and DIRECT
        # Don't repeat requirements multiple times
        enhanced_prompt = prompt

        # Set max tokens
        current_config = generation_config.copy()
        current_config["max_output_tokens"] = max_tokens

        print(f"📤 Sending prompt ({len(enhanced_prompt)} chars, ~{len(enhanced_prompt.split())} words)")

        # Generate content
        response = model.generate_content(
            enhanced_prompt,
            generation_config=current_config
        )

        print(f"📥 Response received")

        # Try to extract text using response.text (most reliable)
        try:
            text = response.text.strip()
            if text:
                print(f"✅ Success: Generated {len(text)} characters")
                return text
        except ValueError as e:
            # response.text raises ValueError when there's no text
            print(f"⚠️  response.text error: {e}")

            # Check if blocked or other issues
            if response.candidates:
                candidate = response.candidates[0]
                finish_reason = candidate.finish_reason

                print(f"Finish reason: {finish_reason}")

                # finish_reason values:
                # 0 = FINISH_REASON_UNSPECIFIED
                # 1 = STOP (normal completion)
                # 2 = MAX_TOKENS (truncated)
                # 3 = SAFETY (blocked by safety)
                # 4 = RECITATION (blocked by recitation)
                # 5 = OTHER

                if finish_reason == 3:
                    raise Exception("Content blocked by safety filters. Try a different topic.")
                elif finish_reason == 4:
                    raise Exception("Content blocked due to recitation. Try being more creative.")
                elif finish_reason == 2:
                    # MAX_TOKENS but no content generated
                    raise Exception("Prompt is too complex. Please simplify your request.")

                # Try to extract from parts even if response.text failed
                if candidate.content and candidate.content.parts:
                    text_parts = []
                    for part in candidate.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)

                    if text_parts:
                        combined = ''.join(text_parts).strip()
                        if combined:
                            print(f"✅ Extracted from parts: {len(combined)} characters")
                            return combined

            raise Exception("AI generated empty response. This usually means the prompt is too complex.")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Gemini error: {error_msg}")

        if "blocked" in error_msg.lower() or "safety" in error_msg.lower():
            raise Exception("Content blocked by safety filters. Try a different topic.")
        elif "quota" in error_msg.lower():
            raise Exception("API quota exceeded. Please try again later.")
        elif "complex" in error_msg.lower() or "empty" in error_msg.lower():
            raise  # Re-raise as is
        else:
            raise Exception(f"AI service error: {error_msg}")


def generate_instagram_caption(topic: str, style: str = "engaging",
                               num_sentences: str = "3-5",
                               word_range: str = "50-100",
                               hashtag_range: str = "3-5",
                               emoji_range: str = "2-4") -> str:
    """
    Generate Instagram caption with simplified, effective prompting

    Args:
        topic: The topic/subject for the caption
        style: Writing style (engaging, professional, casual, trendy)
        num_sentences: Number of sentences (e.g., "3-5")
        word_range: Word count range (e.g., "50-100")
        hashtag_range: Number of hashtags (e.g., "3-5")
        emoji_range: Number of emojis (e.g., "2-4")

    Returns:
        str: Generated Instagram caption
    """

    # SIMPLIFIED PROMPT - this is the key fix!
    # Don't repeat requirements, don't use ALL CAPS, keep it concise
    prompt = f"""Write an Instagram caption about: {topic}

Style: {style}
Length: {num_sentences} sentences, {word_range} words
Include: {emoji_range} emojis, {hashtag_range} hashtags, call-to-action

Make it current and engaging for 2024."""

    try:
        return generate_text_with_gemini(prompt, max_tokens=800, include_web_search=True)
    except Exception as e:
        logger.error(f"Caption generation failed: {e}")
        raise


def test_gemini_connection() -> bool:
    """Test if Gemini AI connection is working"""
    try:
        logger.info("Testing Gemini connection...")
        response = model.generate_content("Say 'Hello'")

        try:
            if response.text:
                logger.info("✅ Connection successful")
                return True
        except:
            pass

        logger.error("❌ Connection failed")
        return False
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False


def get_gemini_model_info():
    """Get information about available Gemini models"""
    try:
        models = genai.list_models()
        return [model.name for model in models if 'generateContent' in model.supported_generation_methods]
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return []


def generate_unique_variation(original_prompt: str, variation_type: str = "creative", max_tokens: int = 1024) -> str:
    """
    Generate a unique variation of content

    Args:
        original_prompt: The original prompt
        variation_type: Type of variation (creative, professional, casual, trendy)
        max_tokens: Maximum tokens for response

    Returns:
        str: Unique variation of the content
    """

    # Simplified variation prompts
    variation_styles = {
        "creative": "Create a unique, creative version",
        "professional": "Rewrite in professional tone",
        "casual": "Make it casual and friendly",
        "trendy": "Update with latest 2024 trends"
    }

    prompt = f"""{original_prompt}

{variation_styles.get(variation_type, variation_styles["creative"])}."""

    try:
        return generate_text_with_gemini(prompt, max_tokens, include_web_search=True)
    except Exception as e:
        logger.error(f"Variation failed: {e}")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("🧪 Testing Gemini connection...")
    if test_gemini_connection():
        print("✅ Connection successful!\n")

        # Test caption generation
        print("🧪 Testing caption generation...")
        try:
            caption = generate_instagram_caption(
                topic="dance",
                style="engaging",
                num_sentences="3-5",
                word_range="50-100",
                hashtag_range="3-5",
                emoji_range="2-4"
            )
            print(f"\n✅ Generated caption:\n{caption}\n")
        except Exception as e:
            print(f"\n❌ Failed: {e}\n")
    else:
        print("❌ Connection failed!")

    print("\n📋 Available models:")
    models = get_gemini_model_info()
    for model_name in models[:5]:
        print(f"   • {model_name}")