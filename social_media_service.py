from ai_service import generate_text_with_gemini, generate_unique_variation
from typing import List, Dict, Tuple
import re
import logging
import json

logger = logging.getLogger(__name__)


def generate_instagram_content(prompt: str, content_type: str = 'tags', style: str = 'trending',
                               count: int = 30, length: str = 'medium', hashtags: str = 'yes', emojis: str = 'moderate') -> Dict:
    """
    Generate Instagram content (hashtags, captions, etc.)

    Args:
        prompt (str): Description of the content
        content_type (str): 'tags', 'caption', 'bio', 'stories'
        style (str): 'trending', 'niche', 'mixed'
        count (int): Number of items to generate
        length (str): 'short', 'medium', 'long' (for captions)
        hashtags (str): 'yes', 'no', 'many' (for captions)
        emojis (str): 'moderate', 'minimal', 'lots', 'none' (for captions)

    Returns:
        Dict: Generated content
    """
    try:
        if content_type == 'tags':
            return generate_instagram_tags(prompt, style, count)
        elif content_type == 'caption':
            return generate_instagram_caption(prompt, style, length, hashtags, emojis)
        elif content_type == 'bio':
            return generate_instagram_bio(prompt)
        elif content_type == 'stories':
            return generate_instagram_story_ideas(prompt, count)
        else:
            raise ValueError("Invalid content type")
    except Exception as e:
        logger.error(f"Instagram content generation failed: {str(e)}")
        raise


def generate_youtube_content(prompt: str, content_type: str = 'tags', count: int = 20) -> Dict:
    """
    Generate YouTube content (tags, titles, descriptions)

    Args:
        prompt (str): Video description/topic
        content_type (str): 'tags', 'title', 'description', 'thumbnail'
        count (int): Number of items to generate

    Returns:
        Dict: Generated content
    """
    try:
        if content_type == 'tags':
            return generate_youtube_tags(prompt, count)
        elif content_type == 'title':
            return generate_youtube_titles(prompt, count)
        elif content_type == 'description':
            return generate_youtube_description(prompt)
        elif content_type == 'thumbnail':
            return generate_youtube_thumbnail_ideas(prompt, count)
        else:
            raise ValueError("Invalid content type")
    except Exception as e:
        logger.error(f"YouTube content generation failed: {str(e)}")
        raise


def generate_twitter_content(prompt: str, content_type: str = 'tags', count: int = 15) -> Dict:
    """
    Generate Twitter/X content

    Args:
        prompt (str): Tweet topic/description
        content_type (str): 'tags', 'tweet', 'thread', 'bio'
        count (int): Number of items to generate

    Returns:
        Dict: Generated content
    """
    try:
        if content_type == 'tags':
            return generate_twitter_hashtags(prompt, count)
        elif content_type == 'tweet':
            return generate_twitter_tweets(prompt, count)
        elif content_type == 'thread':
            return generate_twitter_thread(prompt)
        elif content_type == 'bio':
            return generate_twitter_bio(prompt)
        else:
            raise ValueError("Invalid content type")
    except Exception as e:
        logger.error(f"Twitter content generation failed: {str(e)}")
        raise


def generate_tiktok_content(prompt: str, content_type: str = 'tags', count: int = 25) -> Dict:
    """
    Generate TikTok content

    Args:
        prompt (str): Video description/topic
        content_type (str): 'tags', 'caption', 'hooks', 'trends'
        count (int): Number of items to generate

    Returns:
        Dict: Generated content
    """
    try:
        if content_type == 'tags':
            return generate_tiktok_hashtags(prompt, count)
        elif content_type == 'caption':
            return generate_tiktok_captions(prompt, count)
        elif content_type == 'hooks':
            return generate_tiktok_hooks(prompt, count)
        elif content_type == 'trends':
            return generate_tiktok_trend_ideas(prompt, count)
        else:
            raise ValueError("Invalid content type")
    except Exception as e:
        logger.error(f"TikTok content generation failed: {str(e)}")
        raise


# Instagram specific functions
def generate_instagram_tags(prompt: str, style: str = 'trending', count: int = 30) -> Dict:
    """Generate Instagram hashtags"""
    ai_prompt = f"""CRITICAL: You MUST follow these EXACT specifications. Do NOT deviate from user choices.

Generate EXACTLY {count} Instagram hashtags for: "{prompt}"

STYLE REQUIREMENT (MUST FOLLOW):
- {style.upper()}: {{
  - trending: ONLY popular, widely-used hashtags for maximum reach (like #photooftheday, #instagood, #love)
  - niche: ONLY specific, targeted hashtags for engaged audiences (like #sunsetphotography, #beachvibes, #naturelover)
  - mixed: EXACTLY 50% popular hashtags and 50% niche hashtags
}}

STRICT REQUIREMENTS:
- Return EXACTLY {count} hashtags
- One hashtag per line
- NO # symbol in output
- Only letters, numbers, underscores
- 3-25 characters each
- MUST be relevant to the prompt
- MUST follow the selected style exactly

OUTPUT FORMAT (MUST BE EXACT):
hashtag1
hashtag2
hashtag3
... (continue until {count} hashtags)

REMINDER: Follow the style selection EXACTLY. If user chose 'trending', ONLY use popular hashtags. If 'niche', ONLY use specific hashtags. If 'mixed', use exactly half of each."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=800)
        tags = _extract_hashtags_from_response(response)
        cleaned_tags = _clean_and_validate_tags(tags)

        if len(cleaned_tags) < 5:
            cleaned_tags.extend(_generate_fallback_tags(prompt, count))
            cleaned_tags = list(dict.fromkeys(cleaned_tags))

        return {
            "success": True,
            "tags": cleaned_tags[:count],
            "count": len(cleaned_tags[:count]),
            "with_hash": ["#" + tag for tag in cleaned_tags[:count]],
            "text_only": " ".join(cleaned_tags[:count]),
            "text_with_hash": " ".join(["#" + tag for tag in cleaned_tags[:count]])
        }
    except Exception as e:
        fallback_tags = _generate_fallback_tags(prompt, count)
        return {
            "success": True,
            "tags": fallback_tags,
            "count": len(fallback_tags),
            "with_hash": ["#" + tag for tag in fallback_tags],
            "text_only": " ".join(fallback_tags),
            "text_with_hash": " ".join(["#" + tag for tag in fallback_tags])
        }


def generate_instagram_caption(prompt: str, style: str = 'engaging', length: str = 'medium', hashtags: str = 'yes', emojis: str = 'moderate', is_variation: bool = False) -> Dict:
    """Generate Instagram captions with web search and unique variations"""
    
    # Parse the enhanced prompt to extract the original content
    original_prompt = prompt
    if " (Style:" in prompt:
        original_prompt = prompt.split(" (Style:")[0].strip()
    
    # Length guidelines
    length_guide = {
        'short': '1-2 sentences, under 50 words',
        'medium': '3-5 sentences, 50-100 words', 
        'long': '6+ sentences, 100-150 words'
    }
    
    # Hashtag guidelines
    hashtag_guide = {
        'yes': 'Include 3-5 relevant hashtags at the end',
        'no': 'No hashtags in the caption',
        'many': 'Include 8-12 relevant hashtags at the end'
    }
    
    # Emoji guidelines
    emoji_guide = {
        'moderate': 'Use 2-4 emojis strategically placed',
        'minimal': 'Use 1-2 emojis sparingly',
        'lots': 'Use 5-8 emojis throughout the caption',
        'none': 'No emojis, clean text only'
    }
    
    # Enhanced prompt with STRICT parameter enforcement
    ai_prompt = f"""CRITICAL: You MUST follow these EXACT specifications. Do NOT deviate from user choices.

Create an Instagram caption for: "{original_prompt}"

STRICT REQUIREMENTS (MUST FOLLOW):
1. STYLE: {style.upper()} - Make it {style} and authentic
2. LENGTH: {length_guide[length]} - MUST be exactly {length_guide[length]}
3. HASHTAGS: {hashtag_guide[hashtags]} - MUST follow this rule exactly
4. EMOJIS: {emoji_guide[emojis]} - MUST use exactly as specified

ADDITIONAL REQUIREMENTS:
- Include a call-to-action
- Make it engaging and shareable
- Use current 2024 trends and viral phrases
- Be creative and unique

FORMAT:
[Caption text here following ALL requirements above]

{hashtag_guide[hashtags].replace('Include ', '').replace(' at the end', '') if hashtags != 'no' else ''}

IMPORTANT: This caption MUST feel fresh, current, and trending. Include recent viral phrases or trends if relevant.

REMINDER: Follow ALL user specifications EXACTLY. Do not change the style, length, hashtag count, or emoji usage from what was requested."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=400)
        return {
            "success": True,
            "caption": response.strip(),
            "character_count": len(response.strip())
        }
    except Exception as e:
        fallback_caption = f"Amazing {prompt}! ✨ What do you think about this? Let me know in the comments! 👇\n\n#amazing #photooftheday #instagood"
        return {
            "success": True,
            "caption": fallback_caption,
            "character_count": len(fallback_caption)
        }


def generate_instagram_caption_variation(prompt: str, style: str = 'engaging', length: str = 'medium', hashtags: str = 'yes', emojis: str = 'moderate') -> Dict:
    """Generate a unique variation of Instagram caption with web search"""
    
    # Parse the enhanced prompt to extract the original content
    original_prompt = prompt
    if " (Style:" in prompt:
        original_prompt = prompt.split(" (Style:")[0].strip()
    
    try:
        # Use the unique variation function for creative, trending content
        variation_prompt = f"""Create a completely different, unique Instagram caption for: "{original_prompt}"

Style: {style}
Length: {length}
Hashtags: {hashtags}
Emojis: {emojis}

IMPORTANT: 
- Make this completely different from typical responses
- Search web for latest trends and viral content
- Use current 2024 social media language
- Be creative, innovative, and unique
- Include trending phrases if relevant
- Make it feel fresh and current"""

        response = generate_unique_variation(variation_prompt, "trendy", 400)
        
        return {
            "success": True,
            "caption": response.strip(),
            "character_count": len(response.strip()),
            "is_variation": True
        }
        
    except Exception as e:
        # Generate a more creative fallback
        creative_fallbacks = [
            f"✨ {original_prompt} just hit different today! The vibes are immaculate and I'm here for it! 🔥 What's your take on this? Drop a comment below! 👇 #vibes #trending #2024",
            f"POV: You discover {original_prompt} and your entire perspective shifts! This is the content we've been waiting for! 💫 Who else can relate? #perspective #discovery #relatable",
            f"🚀 {original_prompt} is literally everything right now! The energy is unmatched and I'm obsessed! Tell me you love this without telling me! 💯 #obsessed #energy #viral",
            f"Plot twist: {original_prompt} becomes your new personality trait! The character development we didn't know we needed! 😱 Who else is experiencing this? #plot #character #development",
            f"✨ {original_prompt} supremacy! This is the moment we've all been waiting for! The serotonin boost is real! 🎉 What are your thoughts? #supremacy #moment #serotonin"
        ]
        
        import random
        fallback_caption = random.choice(creative_fallbacks)
        
        return {
            "success": True,
            "caption": fallback_caption,
            "character_count": len(fallback_caption),
            "is_variation": True
        }


def generate_instagram_bio(prompt: str) -> Dict:
    """Generate Instagram bio"""
    ai_prompt = f"""Create an engaging Instagram bio for: "{prompt}"

Requirements:
- Under 150 characters
- Include relevant keywords
- Make it authentic and engaging
- Include a call-to-action if appropriate
- Use line breaks for readability

Format:
Bio text here..."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=300)
        return {
            "success": True,
            "bio": response.strip(),
            "character_count": len(response.strip())
        }
    except Exception as e:
        fallback_bio = f"✨ {prompt} enthusiast | Sharing amazing moments | Follow for daily inspiration"
        return {
            "success": True,
            "bio": fallback_bio,
            "character_count": len(fallback_bio)
        }


def generate_instagram_story_ideas(prompt: str, count: int = 5) -> Dict:
    """Generate Instagram story ideas"""
    ai_prompt = f"""CRITICAL: You MUST follow these EXACT specifications. Do NOT deviate from user choices.

Generate EXACTLY {count} Instagram story ideas for: "{prompt}"

STRICT REQUIREMENTS:
- Return EXACTLY {count} story ideas - no more, no less
- Each idea MUST be creative and engaging
- MUST include visual elements and text overlays
- MUST make them interactive and shareable
- One idea per line

OUTPUT FORMAT (MUST BE EXACT):
Story idea 1
Story idea 2
Story idea 3
... (continue until {count} ideas)

COUNT VERIFICATION:
- Count each story idea carefully
- Ensure you have exactly {count} ideas
- Each idea should be complete and actionable

REMINDER: You MUST return EXACTLY {count} story ideas. Count them carefully before submitting."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=400)
        ideas = [line.strip() for line in response.split('\n') if line.strip()]
        
        if len(ideas) < 3:
            ideas = _generate_instagram_story_fallback(prompt, count)
        
        return {
            "success": True,
            "ideas": ideas[:count],
            "count": len(ideas[:count])
        }
    except Exception as e:
        fallback_ideas = _generate_instagram_story_fallback(prompt, count)
        return {
            "success": True,
            "ideas": fallback_ideas,
            "count": len(fallback_ideas)
        }


# YouTube specific functions
def generate_youtube_tags(prompt: str, count: int = 20) -> Dict:
    """Generate YouTube tags (keywords without hashtags)"""
    ai_prompt = f"""CRITICAL: You MUST follow these EXACT specifications. Do NOT deviate from user choices.

Generate EXACTLY {count} YouTube tags/keywords for: "{prompt}"

STRICT REQUIREMENTS:
- Return EXACTLY {count} tags - no more, no less
- NO hashtags (#) - just keywords
- Each tag should be 2-4 words
- MUST be SEO optimized for YouTube
- MUST be relevant to the prompt
- Tags should be separated by new lines (one per line)

OUTPUT FORMAT (MUST BE EXACT):
tag1
tag2
tag3
... (continue until {count} tags)

EXAMPLE FORMAT:
how to cook pasta
easy pasta recipes
cooking tips
italian food
quick meals

REMINDER: You MUST return EXACTLY {count} tags. Count them carefully before submitting."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=600)

        # Extract tags (keywords) from response
        lines = response.split('\n')
        tags = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Remove bullets and numbers
                line = re.sub(r'^\d+\.\s*', '', line)
                line = re.sub(r'^-\s*', '', line)
                line = re.sub(r'^\*\s*', '', line)

                # Clean and validate
                if len(line) <= 50 and len(line.split()) <= 5:
                    tags.append(line)

        # Also try comma-separated extraction
        if ',' in response:
            comma_tags = [tag.strip() for tag in response.replace('\n', ',').split(',')]
            for tag in comma_tags:
                tag = re.sub(r'^\d+\.\s*', '', tag)
                tag = re.sub(r'^-\s*', '', tag)
                if tag and len(tag) <= 50 and len(tag.split()) <= 5 and tag not in tags:
                    tags.append(tag)

        # Fallback if not enough tags
        if len(tags) < 5:
            fallback = _generate_youtube_fallback_tags(prompt, count)
            tags.extend(fallback)
            tags = list(dict.fromkeys(tags))  # Remove duplicates

        final_tags = tags[:count]
        return {
            "success": True,
            "tags": final_tags,
            "count": len(final_tags),
            "comma_separated": ", ".join(final_tags),
            "quoted": ", ".join([f'"{tag}"' for tag in final_tags])
        }

    except Exception as e:
        fallback_tags = _generate_youtube_fallback_tags(prompt, count)
        return {
            "success": True,
            "tags": fallback_tags,
            "count": len(fallback_tags),
            "comma_separated": ", ".join(fallback_tags),
            "quoted": ", ".join([f'"{tag}"' for tag in fallback_tags])
        }


def generate_youtube_titles(prompt: str, count: int = 10) -> Dict:
    """Generate YouTube video titles"""
    ai_prompt = f"""CRITICAL: You MUST follow these EXACT specifications. Do NOT deviate from user choices.

Generate EXACTLY {count} catchy YouTube video titles for: "{prompt}"

STRICT REQUIREMENTS:
- Return EXACTLY {count} titles - no more, no less
- Each title MUST be 40-60 characters
- MUST be click-worthy but not clickbait
- MUST include relevant keywords from the prompt
- MUST use various styles (How-to, Question, List, etc.)
- One title per line

OUTPUT FORMAT (MUST BE EXACT):
title1
title2
title3
... (continue until {count} titles)

CHARACTER COUNT CHECK:
- Count each title carefully
- Ensure each is between 40-60 characters
- Verify you have exactly {count} titles

REMINDER: You MUST return EXACTLY {count} titles. Count them carefully before submitting."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=500)
        titles = [line.strip() for line in response.split('\n') if line.strip()]

        # Clean titles
        cleaned_titles = []
        for title in titles:
            title = re.sub(r'^\d+\.\s*', '', title)
            title = re.sub(r'^-\s*', '', title)
            if title and 20 <= len(title) <= 100:
                cleaned_titles.append(title)

        if len(cleaned_titles) < 3:
            cleaned_titles = _generate_youtube_title_fallback(prompt, count)

        return {
            "success": True,
            "titles": cleaned_titles[:count],
            "count": len(cleaned_titles[:count])
        }
    except Exception as e:
        fallback_titles = _generate_youtube_title_fallback(prompt, count)
        return {
            "success": True,
            "titles": fallback_titles,
            "count": len(fallback_titles)
        }


def generate_youtube_description(prompt: str) -> Dict:
    """Generate YouTube video description"""
    ai_prompt = f"""Create a YouTube video description for: "{prompt}"

Structure:
1. Engaging opening (2-3 sentences)
2. What viewers will learn/see
3. Timestamps (if applicable)
4. Call-to-action (subscribe, like, comment)
5. Social media links placeholders
6. Relevant tags/keywords naturally included

Keep it under 500 words but informative."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=800)
        return {
            "success": True,
            "description": response.strip(),
            "character_count": len(response.strip()),
            "word_count": len(response.strip().split())
        }
    except Exception as e:
        fallback_desc = f"""Welcome to our channel! In this video, we explore {prompt}.

🔥 What you'll learn:
• Key insights about {prompt}
• Practical tips and techniques
• Expert advice and recommendations

💡 Don't forget to:
• LIKE this video if it helped you
• SUBSCRIBE for more content
• COMMENT your thoughts below
• SHARE with friends who might find this useful

🔗 Connect with us:
• Instagram: @yourchannel
• Twitter: @yourchannel
• Website: www.yourwebsite.com

#youtube #content #tutorial"""

        return {
            "success": True,
            "description": fallback_desc,
            "character_count": len(fallback_desc),
            "word_count": len(fallback_desc.split())
        }


def generate_youtube_thumbnail_ideas(prompt: str, count: int = 5) -> Dict:
    """Generate YouTube thumbnail ideas"""
    ai_prompt = f"""CRITICAL: You MUST follow these EXACT specifications. Do NOT deviate from user choices.

Generate EXACTLY {count} YouTube thumbnail ideas for: "{prompt}"

STRICT REQUIREMENTS:
- Return EXACTLY {count} thumbnail ideas - no more, no less
- Each idea MUST be eye-catching and click-worthy
- MUST include text overlay suggestions
- MUST use bright colors and contrast
- MUST include emoji suggestions
- MUST make them stand out in search results
- One idea per line

OUTPUT FORMAT (MUST BE EXACT):
Thumbnail idea 1
Thumbnail idea 2
Thumbnail idea 3
... (continue until {count} ideas)

COUNT VERIFICATION:
- Count each thumbnail idea carefully
- Ensure you have exactly {count} ideas
- Each idea should be complete and actionable

REMINDER: You MUST return EXACTLY {count} thumbnail ideas. Count them carefully before submitting."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=500)
        ideas = [line.strip() for line in response.split('\n') if line.strip()]

        if len(ideas) < 3:
            ideas = _generate_youtube_thumbnail_fallback(prompt, count)

        return {
            "success": True,
            "ideas": ideas[:count],
            "count": len(ideas[:count])
        }
    except Exception as e:
        fallback_ideas = _generate_youtube_thumbnail_fallback(prompt, count)
        return {
            "success": True,
            "ideas": fallback_ideas,
            "count": len(fallback_ideas)
        }


# Twitter/X specific functions
def generate_twitter_hashtags(prompt: str, count: int = 15) -> Dict:
    """Generate Twitter hashtags"""
    ai_prompt = f"""CRITICAL: You MUST follow these EXACT specifications. Do NOT deviate from user choices.

Generate EXACTLY {count} Twitter hashtags for: "{prompt}"

STRICT REQUIREMENTS:
- Return EXACTLY {count} hashtags - no more, no less
- MUST be trending and relevant to the prompt
- MUST include a mix of popular and niche tags
- NO # symbol in output
- One hashtag per line
- Each hashtag MUST be 3-20 characters
- MUST focus on Twitter trends and current topics

OUTPUT FORMAT (MUST BE EXACT):
hashtag1
hashtag2
hashtag3
... (continue until {count} hashtags)

COUNT VERIFICATION:
- Count each hashtag carefully
- Ensure you have exactly {count} hashtags
- Verify each meets the character limit (3-20 characters)

REMINDER: You MUST return EXACTLY {count} hashtags. Count them carefully before submitting."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=400)
        tags = _extract_hashtags_from_response(response)
        cleaned_tags = _clean_and_validate_tags(tags, max_length=20)

        if len(cleaned_tags) < 5:
            cleaned_tags.extend(_generate_twitter_fallback_tags(prompt, count))
            cleaned_tags = list(dict.fromkeys(cleaned_tags))

        return {
            "success": True,
            "tags": cleaned_tags[:count],
            "count": len(cleaned_tags[:count]),
            "with_hash": ["#" + tag for tag in cleaned_tags[:count]],
            "text_only": " ".join(cleaned_tags[:count]),
            "text_with_hash": " ".join(["#" + tag for tag in cleaned_tags[:count]])
        }
    except Exception as e:
        fallback_tags = _generate_twitter_fallback_tags(prompt, count)
        return {
            "success": True,
            "tags": fallback_tags,
            "count": len(fallback_tags),
            "with_hash": ["#" + tag for tag in fallback_tags],
            "text_only": " ".join(fallback_tags),
            "text_with_hash": " ".join(["#" + tag for tag in fallback_tags])
        }


def generate_twitter_tweets(prompt: str, count: int = 5) -> Dict:
    """Generate Twitter tweets"""
    ai_prompt = f"""CRITICAL: You MUST follow these EXACT specifications. Do NOT deviate from user choices.

Generate EXACTLY {count} engaging tweets about: "{prompt}"

STRICT REQUIREMENTS:
- Return EXACTLY {count} tweets - no more, no less
- Each tweet MUST be under 280 characters
- MUST include 1-2 relevant hashtags
- MUST be engaging and shareable
- MUST use various styles (question, fact, opinion, etc.)
- One tweet per line

OUTPUT FORMAT (MUST BE EXACT):
tweet1
tweet2
tweet3
... (continue until {count} tweets)

CHARACTER COUNT CHECK:
- Count each tweet carefully
- Ensure each is under 280 characters
- Verify you have exactly {count} tweets

REMINDER: You MUST return EXACTLY {count} tweets. Count them carefully before submitting."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=600)
        tweets = [line.strip() for line in response.split('\n') if line.strip() and len(line.strip()) <= 280]

        if len(tweets) < 3:
            tweets = _generate_twitter_tweet_fallback(prompt, count)

        return {
            "success": True,
            "tweets": tweets[:count],
            "count": len(tweets[:count])
        }
    except Exception as e:
        fallback_tweets = _generate_twitter_tweet_fallback(prompt, count)
        return {
            "success": True,
            "tweets": fallback_tweets,
            "count": len(fallback_tweets)
        }


def generate_twitter_thread(prompt: str) -> Dict:
    """Generate Twitter thread"""
    ai_prompt = f"""Create an engaging Twitter thread about: "{prompt}"

Requirements:
- 3-5 tweets that tell a story
- Each tweet under 280 characters
- Include relevant hashtags
- Make it engaging and shareable
- One tweet per line with numbering

Format:
1. First tweet here...
2. Second tweet here...
3. Third tweet here..."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=800)
        tweets = []
        
        for line in response.split('\n'):
            line = line.strip()
            if line and re.match(r'^\d+\.', line):
                # Remove numbering and clean
                tweet = re.sub(r'^\d+\.\s*', '', line)
                if tweet and len(tweet) <= 280:
                    tweets.append(tweet)
        
        if len(tweets) < 3:
            tweets = _generate_twitter_thread_fallback(prompt)
        
        return {
            "success": True,
            "thread": tweets,
            "count": len(tweets)
        }
    except Exception as e:
        fallback_thread = _generate_twitter_thread_fallback(prompt)
        return {
            "success": True,
            "thread": fallback_thread,
            "count": len(fallback_thread)
        }


def generate_twitter_bio(prompt: str) -> Dict:
    """Generate Twitter bio"""
    ai_prompt = f"""Create an engaging Twitter bio for: "{prompt}"

Requirements:
- Under 160 characters
- Include relevant keywords
- Make it authentic and engaging
- Include a call-to-action if appropriate

Format:
Bio text here..."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=300)
        return {
            "success": True,
            "bio": response.strip(),
            "character_count": len(response.strip())
        }
    except Exception as e:
        fallback_bio = f"✨ {prompt} enthusiast | Sharing insights | Follow for updates"
        return {
            "success": True,
            "bio": fallback_bio,
            "character_count": len(fallback_bio)
        }


# TikTok specific functions
def generate_tiktok_hashtags(prompt: str, count: int = 25) -> Dict:
    """Generate TikTok hashtags"""
    ai_prompt = f"""CRITICAL: You MUST follow these EXACT specifications. Do NOT deviate from user choices.

Generate EXACTLY {count} TikTok hashtags for: "{prompt}"

STRICT REQUIREMENTS:
- Return EXACTLY {count} hashtags - no more, no less
- MUST focus on viral and trending TikTok hashtags
- MUST include a mix of popular and niche tags
- MUST use TikTok-specific terms
- NO # symbol in output
- One hashtag per line
- MUST include essential TikTok tags: fyp, foryou, viral, trending, tiktok

OUTPUT FORMAT (MUST BE EXACT):
hashtag1
hashtag2
hashtag3
... (continue until {count} hashtags)

ESSENTIAL TIKTOK TAGS (MUST INCLUDE):
- fyp (for you page)
- foryou
- viral
- trending
- tiktok

COUNT VERIFICATION:
- Count each hashtag carefully
- Ensure you have exactly {count} hashtags
- Include the essential TikTok tags first

REMINDER: You MUST return EXACTLY {count} hashtags. Count them carefully before submitting."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=600)
        tags = _extract_hashtags_from_response(response)
        cleaned_tags = _clean_and_validate_tags(tags)

        # Add essential TikTok tags
        essential_tiktok_tags = ['fyp', 'foryou', 'viral', 'trending', 'tiktok']
        for tag in essential_tiktok_tags:
            if tag not in [t.lower() for t in cleaned_tags]:
                cleaned_tags.insert(0, tag)

        if len(cleaned_tags) < 10:
            cleaned_tags.extend(_generate_tiktok_fallback_tags(prompt, count))
            cleaned_tags = list(dict.fromkeys(cleaned_tags))

        return {
            "success": True,
            "tags": cleaned_tags[:count],
            "count": len(cleaned_tags[:count]),
            "with_hash": ["#" + tag for tag in cleaned_tags[:count]],
            "text_only": " ".join(cleaned_tags[:count]),
            "text_with_hash": " ".join(["#" + tag for tag in cleaned_tags[:count]])
        }
    except Exception as e:
        fallback_tags = _generate_tiktok_fallback_tags(prompt, count)
        return {
            "success": True,
            "tags": fallback_tags,
            "count": len(fallback_tags),
            "with_hash": ["#" + tag for tag in fallback_tags],
            "text_only": " ".join(fallback_tags),
            "text_with_hash": " ".join(["#" + tag for tag in fallback_tags])
        }


def generate_tiktok_captions(prompt: str, count: int = 5) -> Dict:
    """Generate TikTok captions"""
    ai_prompt = f"""CRITICAL: You MUST follow these EXACT specifications. Do NOT deviate from user choices.

Generate EXACTLY {count} engaging TikTok captions for: "{prompt}"

STRICT REQUIREMENTS:
- Return EXACTLY {count} captions - no more, no less
- Each caption MUST be short and catchy
- MUST include trending phrases
- MUST add 2-3 relevant hashtags
- MUST use emojis
- MUST have engaging hooks
- Each caption MUST be under 150 characters
- One caption per line

OUTPUT FORMAT (MUST BE EXACT):
caption1
caption2
caption3
... (continue until {count} captions)

CHARACTER COUNT CHECK:
- Count each caption carefully
- Ensure each is under 150 characters
- Verify you have exactly {count} captions

REMINDER: You MUST return EXACTLY {count} captions. Count them carefully before submitting."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=500)
        captions = [line.strip() for line in response.split('\n') if line.strip()]

        if len(captions) < 3:
            captions = _generate_tiktok_caption_fallback(prompt, count)

        return {
            "success": True,
            "captions": captions[:count],
            "count": len(captions[:count])
        }
    except Exception as e:
        fallback_captions = _generate_tiktok_caption_fallback(prompt, count)
        return {
            "success": True,
            "captions": fallback_captions,
            "count": len(fallback_captions)
        }


def generate_tiktok_hooks(prompt: str, count: int = 10) -> Dict:
    """Generate TikTok hooks"""
    ai_prompt = f"""CRITICAL: You MUST follow these EXACT specifications. Do NOT deviate from user choices.

Generate EXACTLY {count} attention-grabbing TikTok hooks for: "{prompt}"

STRICT REQUIREMENTS:
- Return EXACTLY {count} hooks - no more, no less
- Each hook MUST be for first 3 seconds
- MUST stop the scroll
- MUST use trending phrases
- MUST include emojis
- Each hook MUST be under 100 characters
- One hook per line

OUTPUT FORMAT (MUST BE EXACT):
hook1
hook2
hook3
... (continue until {count} hooks)

CHARACTER COUNT CHECK:
- Count each hook carefully
- Ensure each is under 100 characters
- Verify you have exactly {count} hooks

REMINDER: You MUST return EXACTLY {count} hooks. Count them carefully before submitting."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=500)
        hooks = [line.strip() for line in response.split('\n') if line.strip()]

        if len(hooks) < 3:
            hooks = _generate_tiktok_hook_fallback(prompt, count)

        return {
            "success": True,
            "hooks": hooks[:count],
            "count": len(hooks[:count])
        }
    except Exception as e:
        fallback_hooks = _generate_tiktok_hook_fallback(prompt, count)
        return {
            "success": True,
            "hooks": fallback_hooks,
            "count": len(fallback_hooks)
        }


def generate_tiktok_trend_ideas(prompt: str, count: int = 5) -> Dict:
    """Generate TikTok trend ideas"""
    ai_prompt = f"""CRITICAL: You MUST follow these EXACT specifications. Do NOT deviate from user choices.

Generate EXACTLY {count} TikTok trend ideas for: "{prompt}"

STRICT REQUIREMENTS:
- Return EXACTLY {count} trend ideas - no more, no less
- Each idea MUST be viral and trending
- MUST include dance, challenge, or creative ideas
- MUST use trending sounds and effects
- MUST make them shareable and engaging
- One idea per line

OUTPUT FORMAT (MUST BE EXACT):
Trend idea 1
Trend idea 2
Trend idea 3
... (continue until {count} ideas)

COUNT VERIFICATION:
- Count each trend idea carefully
- Ensure you have exactly {count} ideas
- Each idea should be complete and actionable

REMINDER: You MUST return EXACTLY {count} trend ideas. Count them carefully before submitting."""

    try:
        response = generate_text_with_gemini(ai_prompt, max_tokens=500)
        ideas = [line.strip() for line in response.split('\n') if line.strip()]

        if len(ideas) < 3:
            ideas = _generate_tiktok_trend_fallback(prompt, count)

        return {
            "success": True,
            "ideas": ideas[:count],
            "count": len(ideas[:count])
        }
    except Exception as e:
        fallback_ideas = _generate_tiktok_trend_fallback(prompt, count)
        return {
            "success": True,
            "ideas": fallback_ideas,
            "count": len(fallback_ideas)
        }


# Helper functions
def _extract_hashtags_from_response(response: str) -> List[str]:
    """Extract hashtags from AI response"""
    lines = response.split('\n')
    hashtags = []

    for line in lines:
        line = line.strip()
        if line:
            # Remove # symbol if present
            if line.startswith('#'):
                line = line[1:]

            # Remove markdown formatting and bullets
            line = re.sub(r'^\d+\.\s*', '', line)
            line = re.sub(r'^-\s*', '', line)
            line = re.sub(r'^\*\s*', '', line)
            line = re.sub(r'^\*\*', '', line)
            line = re.sub(r'\*\*$', '', line)

            # Extract just the hashtag part
            match = re.match(r'^([a-zA-Z0-9_]+)', line)
            if match:
                clean_tag = match.group(1)
                if 3 <= len(clean_tag) <= 25:
                    hashtags.append(clean_tag)

    return hashtags


def _clean_and_validate_tags(tags: List[str], max_length: int = 25) -> List[str]:
    """Clean and validate hashtags"""
    cleaned_tags = []
    seen_tags = set()

    for tag in tags:
        tag_lower = tag.lower()

        if (tag_lower not in seen_tags and
                3 <= len(tag) <= max_length and
                re.match(r'^[a-zA-Z0-9_]+$', tag) and
                not tag.isdigit() and
                not tag.startswith('_')):
            cleaned_tags.append(tag)
            seen_tags.add(tag_lower)

    return cleaned_tags


# Fallback functions
def _generate_fallback_tags(prompt: str, count: int) -> List[str]:
    """Generate fallback Instagram tags"""
    base_tags = ['instagram', 'insta', 'instadaily', 'photooftheday', 'beautiful', 'amazing', 'love', 'happy', 'style',
                 'follow']
    prompt_words = re.findall(r'\b[a-zA-Z]{3,15}\b', prompt.lower())
    relevant_tags = [word for word in prompt_words if word not in {'the', 'and', 'for', 'with', 'this'}]

    return list(dict.fromkeys(relevant_tags + base_tags))[:count]


def _generate_youtube_fallback_tags(prompt: str, count: int) -> List[str]:
    """Generate fallback YouTube tags"""
    words = prompt.lower().split()
    tags = []

    # Single words
    for word in words:
        if len(word) > 3:
            tags.append(word)

    # Two word combinations
    for i in range(len(words) - 1):
        if len(f"{words[i]} {words[i + 1]}") <= 30:
            tags.append(f"{words[i]} {words[i + 1]}")

    # Add generic tags
    generic_tags = ['tutorial', 'how to', 'tips', 'guide', 'learn', 'easy', 'best', 'top']
    tags.extend(generic_tags)

    return list(dict.fromkeys(tags))[:count]


def _generate_twitter_fallback_tags(prompt: str, count: int) -> List[str]:
    """Generate fallback Twitter tags"""
    base_tags = ['twitter', 'trending', 'viral', 'news', 'update', 'discussion', 'opinion', 'thoughts']
    prompt_words = re.findall(r'\b[a-zA-Z]{3,15}\b', prompt.lower())
    return list(dict.fromkeys(prompt_words + base_tags))[:count]


def _generate_tiktok_fallback_tags(prompt: str, count: int) -> List[str]:
    """Generate fallback TikTok tags"""
    base_tags = ['fyp', 'foryou', 'viral', 'trending', 'tiktok', 'dance', 'funny', 'comedy', 'lifestyle', 'tutorial']
    prompt_words = re.findall(r'\b[a-zA-Z]{3,15}\b', prompt.lower())
    return list(dict.fromkeys(base_tags + prompt_words))[:count]


def _generate_youtube_title_fallback(prompt: str, count: int) -> List[str]:
    """Generate fallback YouTube titles"""
    return [
               f"The Ultimate Guide to {prompt}",
               f"How to Master {prompt} in 2024",
               f"Everything You Need to Know About {prompt}",
               f"Top 10 Tips for {prompt}",
               f"Why {prompt} is Trending Right Now"
           ][:count]

    
def _generate_twitter_tweet_fallback(prompt: str, count: int) -> List[str]:
    """Generate fallback Twitter tweets"""
    return [
               f"Just discovered something amazing about {prompt}! What are your thoughts? 🤔 #trending",
               f"Hot take: {prompt} is going to be huge in 2024. Who else agrees? 🔥",
               f"Can we talk about {prompt} for a second? This is incredible! ✨ #viral",
               f"Your daily reminder that {prompt} exists and it's awesome 💪",
               f"POV: You're scrolling and see this post about {prompt} 👀 #fyp"
           ][:count]


def _generate_tiktok_caption_fallback(prompt: str, count: int) -> List[str]:
    """Generate fallback TikTok captions"""
    return [
               f"POV: You discover {prompt} 😱 #fyp #viral",
               f"This {prompt} hit different 🔥 #trending #foryou",
               f"Tell me you love {prompt} without telling me 💯 #tiktok",
               f"When someone mentions {prompt}: 🤩✨ #viral #fyp",
               f"Rate this {prompt} content 1-10 🤔 #rating #foryou"
           ][:count]


def _generate_instagram_story_fallback(prompt: str, count: int) -> List[str]:
    """Generate fallback Instagram story ideas"""
    return [
               f"Behind the scenes: {prompt} 📸",
               f"Q&A about {prompt} - Ask me anything! ❓",
               f"Day in the life: {prompt} edition ✨",
               f"Tips and tricks for {prompt} 💡",
               f"Celebrating {prompt} with you! 🎉"
           ][:count]


def _generate_twitter_thread_fallback(prompt: str) -> List[str]:
    """Generate fallback Twitter thread"""
    return [
        f"Just discovered something incredible about {prompt}! Let me break it down for you 🧵",
        f"Here's what you need to know: {prompt} is changing everything we thought we knew 🔥",
        f"The future of {prompt} looks brighter than ever. Who else is excited? ✨",
        f"Key takeaway: {prompt} isn't just a trend, it's a revolution 💪",
        f"What are your thoughts on {prompt}? Drop a comment below! 👇"
    ]


def _generate_tiktok_hook_fallback(prompt: str, count: int) -> List[str]:
    """Generate fallback TikTok hooks"""
    return [
        f"POV: You discover {prompt} 😱",
        f"This {prompt} hit different 🔥",
        f"Tell me you love {prompt} without telling me 💯",
        f"When someone mentions {prompt}: 🤩✨",
        f"Rate this {prompt} content 1-10 🤔"
    ][:count]


def _generate_tiktok_trend_fallback(prompt: str, count: int) -> List[str]:
    """Generate fallback TikTok trend ideas"""
    return [
        f"POV: You're scrolling and see {prompt} 🎭",
        f"Day in the life: {prompt} edition ✨",
        f"Before and after: {prompt} transformation 🔄",
        f"3 ways to master {prompt} 💡",
        f"Hidden secrets of {prompt} 🤫"
    ][:count]


def _generate_youtube_thumbnail_fallback(prompt: str, count: int) -> List[str]:
    """Generate fallback YouTube thumbnail ideas"""
    return [
        f"🔥 {prompt} - You Won't Believe This!",
        f"💡 {prompt} - The Ultimate Guide",
        f"⚡ {prompt} - Game Changer!",
        f"🎯 {prompt} - Expert Tips Revealed",
        f"🚀 {prompt} - Next Level Content"
    ][:count]