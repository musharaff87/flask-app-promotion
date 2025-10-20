import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from youtube_service import upload_to_youtube, authenticate_youtube, start_youtube_auth_flow, complete_youtube_auth_flow
from auth_service import start_google_auth_flow, complete_google_auth_flow, store_user_data
from social_media_service import (
    generate_instagram_content,
    generate_youtube_content,
    generate_twitter_content,
    generate_tiktok_content
)
from google_auth_oauthlib.flow import Flow
import sys
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500mb

# Configure logging
app.logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('app.log')
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

@app.route('/')
def home():
    is_logged_in = 'user_id' in session
    return render_template('index.html', is_logged_in=is_logged_in)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/services')
def services():
    return render_template('services.html')

# Auth routes (keeping existing)
@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == 'POST':
        auth_url, state = start_google_auth_flow()
        session['oauth_state'] = state
        return redirect(auth_url)
    return render_template('login.html')

@app.route('/oauth2callback')
def oauth2callback():
    if 'oauth_state' not in session:
        return "Invalid state", 400
    state = request.args.get('state')
    if state != session['oauth_state']:
        return "State mismatch", 400
    code = request.args.get('code')
    if not code:
        return "No authorization code", 400
    google = complete_google_auth_flow(code)
    user_id = store_user_data(google)
    session.pop('oauth_state', None)
    session['user_id'] = user_id
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

# Social Media Main Pages
@app.route('/social-media')
def social_media_services():
    """Social media services landing page"""
    return render_template('social_media_services.html')

# AI Video Generator Page
@app.route('/ai-video-generator')
def ai_video_generator():
    return render_template('ai-video-generator.html')

# Instagram Routes
@app.route('/instagram-tools')
def instagram_tools():
    """Instagram tools page"""
    return render_template('instagram_tools.html')

@app.route('/instagram-hashtag-generator')
def instagram_hashtag_generator():
    """Instagram hashtag generator page"""
    return render_template('instagram_hashtag_generator.html')

@app.route('/instagram-caption-generator')
def instagram_caption_generator():
    """Instagram caption generator page"""
    return render_template('instagram_caption_generator.html')

@app.route('/instagram-bio-generator')
def instagram_bio_generator():
    """Instagram bio generator page"""
    return render_template('instagram_bio_generator.html')

# YouTube Routes
@app.route('/youtube-tools')
def youtube_tools():
    """YouTube tools page"""
    return render_template('youtube_tools.html')

@app.route('/youtube-tag-generator')
def youtube_tag_generator():
    """YouTube tag generator page"""
    return render_template('youtube_tag_generator.html')

@app.route('/youtube-title-generator')
def youtube_title_generator():
    """YouTube title generator page"""
    return render_template('youtube_title_generator.html')

@app.route('/youtube-description-generator')
def youtube_description_generator():
    """YouTube description generator page"""
    return render_template('youtube_description_generator.html')

# Twitter/X Routes
@app.route('/twitter-tools')
def twitter_tools():
    """Twitter tools page"""
    return render_template('twitter_tools.html')

@app.route('/twitter-hashtag-generator')
def twitter_hashtag_generator():
    """Twitter hashtag generator page"""
    return render_template('twitter_hashtag_generator.html')

@app.route('/twitter-tweet-generator')
def twitter_tweet_generator():
    """Twitter tweet generator page"""
    return render_template('twitter_tweet_generator.html')

@app.route('/twitter-thread-generator')
def twitter_thread_generator():
    """Twitter thread generator page"""
    return render_template('twitter_thread_generator.html')

# TikTok Routes
@app.route('/tiktok-tools')
def tiktok_tools():
    """TikTok tools page"""
    return render_template('tiktok_tools.html')

@app.route('/tiktok-hashtag-generator')
def tiktok_hashtag_generator():
    """TikTok hashtag generator page"""
    return render_template('tiktok_hashtag_generator.html')

@app.route('/tiktok-caption-generator')
def tiktok_caption_generator():
    """TikTok caption generator page"""
    return render_template('tiktok_caption_generator.html')

@app.route('/tiktok-hook-generator')
def tiktok_hook_generator():
    """TikTok hook generator page"""
    return render_template('tiktok_hook_generator.html')

# API Endpoints for Instagram
@app.route('/api/instagram/hashtags', methods=['POST'])
def api_instagram_hashtags():
    """Generate Instagram hashtags"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Prompt is required"}), 400

        prompt = data['prompt']
        style = data.get('style', 'trending')
        count = int(data.get('count', 30))

        if count < 5 or count > 50:
            return jsonify({"error": "Count must be between 5 and 50"}), 400

        result = generate_instagram_content(prompt, 'tags', style, count)
        return jsonify(result), 200

    except Exception as e:
        app.logger.exception(f"Instagram hashtag generation failed: {str(e)}")
        return jsonify({"error": "Failed to generate hashtags. Please try again."}), 500

@app.route('/api/instagram/caption', methods=['POST'])
def api_instagram_caption():
    """Generate Instagram caption"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Prompt is required"}), 400

        prompt = data['prompt']
        style = data.get('style', 'engaging')
        length = data.get('length', 'medium')
        hashtags = data.get('hashtags', 'yes')
        emojis = data.get('emojis', 'moderate')
        is_variation = data.get('is_variation', False)

        if is_variation:
            # Import the variation function
            from social_media_service import generate_instagram_caption_variation
            result = generate_instagram_caption_variation(prompt, style, length, hashtags, emojis)
        else:
            result = generate_instagram_content(prompt, 'caption', style, length=length, hashtags=hashtags, emojis=emojis)

        return jsonify(result), 200

    except Exception as e:
        app.logger.exception(f"Instagram caption generation failed: {str(e)}")
        return jsonify({"error": "Failed to generate caption. Please try again."}), 500

@app.route('/api/instagram/bio', methods=['POST'])
def api_instagram_bio():
    """Generate Instagram bio"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Prompt is required"}), 400

        prompt = data['prompt']
        result = generate_instagram_content(prompt, 'bio')
        return jsonify(result), 200

    except Exception as e:
        app.logger.exception(f"Instagram bio generation failed: {str(e)}")
        return jsonify({"error": "Failed to generate bio. Please try again."}), 500

# API Endpoints for YouTube
@app.route('/api/youtube/tags', methods=['POST'])
def api_youtube_tags():
    """Generate YouTube tags"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Prompt is required"}), 400

        prompt = data['prompt']
        count = int(data.get('count', 20))

        if count < 5 or count > 50:
            return jsonify({"error": "Count must be between 5 and 50"}), 400

        result = generate_youtube_content(prompt, 'tags', count)
        return jsonify(result), 200

    except Exception as e:
        app.logger.exception(f"YouTube tag generation failed: {str(e)}")
        return jsonify({"error": "Failed to generate tags. Please try again."}), 500

@app.route('/api/youtube/titles', methods=['POST'])
def api_youtube_titles():
    """Generate YouTube titles"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Prompt is required"}), 400

        prompt = data['prompt']
        count = int(data.get('count', 10))

        result = generate_youtube_content(prompt, 'title', count)
        return jsonify(result), 200

    except Exception as e:
        app.logger.exception(f"YouTube title generation failed: {str(e)}")
        return jsonify({"error": "Failed to generate titles. Please try again."}), 500

@app.route('/api/youtube/description', methods=['POST'])
def api_youtube_description():
    """Generate YouTube description"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Prompt is required"}), 400

        prompt = data['prompt']
        result = generate_youtube_content(prompt, 'description')
        return jsonify(result), 200

    except Exception as e:
        app.logger.exception(f"YouTube description generation failed: {str(e)}")
        return jsonify({"error": "Failed to generate description. Please try again."}), 500

# API Endpoints for Twitter
@app.route('/api/twitter/hashtags', methods=['POST'])
def api_twitter_hashtags():
    """Generate Twitter hashtags"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Prompt is required"}), 400

        prompt = data['prompt']
        count = int(data.get('count', 15))

        if count < 5 or count > 30:
            return jsonify({"error": "Count must be between 5 and 30"}), 400

        result = generate_twitter_content(prompt, 'tags', count)
        return jsonify(result), 200

    except Exception as e:
        app.logger.exception(f"Twitter hashtag generation failed: {str(e)}")
        return jsonify({"error": "Failed to generate hashtags. Please try again."}), 500

@app.route('/api/twitter/tweets', methods=['POST'])
def api_twitter_tweets():
    """Generate Twitter tweets"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Prompt is required"}), 400

        prompt = data['prompt']
        count = int(data.get('count', 5))

        result = generate_twitter_content(prompt, 'tweet', count)
        return jsonify(result), 200

    except Exception as e:
        app.logger.exception(f"Twitter tweet generation failed: {str(e)}")
        return jsonify({"error": "Failed to generate tweets. Please try again."}), 500

@app.route('/api/twitter/thread', methods=['POST'])
def api_twitter_thread():
    """Generate Twitter thread"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Prompt is required"}), 400

        prompt = data['prompt']
        result = generate_twitter_content(prompt, 'thread')
        return jsonify(result), 200

    except Exception as e:
        app.logger.exception(f"Twitter thread generation failed: {str(e)}")
        return jsonify({"error": "Failed to generate thread. Please try again."}), 500

# API Endpoints for TikTok
@app.route('/api/tiktok/hashtags', methods=['POST'])
def api_tiktok_hashtags():
    """Generate TikTok hashtags"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Prompt is required"}), 400

        prompt = data['prompt']
        count = int(data.get('count', 25))

        if count < 5 or count > 50:
            return jsonify({"error": "Count must be between 5 and 50"}), 400

        result = generate_tiktok_content(prompt, 'tags', count)
        return jsonify(result), 200

    except Exception as e:
        app.logger.exception(f"TikTok hashtag generation failed: {str(e)}")
        return jsonify({"error": "Failed to generate hashtags. Please try again."}), 500

@app.route('/api/tiktok/captions', methods=['POST'])
def api_tiktok_captions():
    """Generate TikTok captions"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Prompt is required"}), 400

        prompt = data['prompt']
        count = int(data.get('count', 5))

        result = generate_tiktok_content(prompt, 'caption', count)
        return jsonify(result), 200

    except Exception as e:
        app.logger.exception(f"TikTok caption generation failed: {str(e)}")
        return jsonify({"error": "Failed to generate captions. Please try again."}), 500

@app.route('/api/tiktok/hooks', methods=['POST'])
def api_tiktok_hooks():
    """Generate TikTok hooks"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Prompt is required"}), 400

        prompt = data['prompt']
        count = int(data.get('count', 10))

        result = generate_tiktok_content(prompt, 'hooks', count)
        return jsonify(result), 200

    except Exception as e:
        app.logger.exception(f"TikTok hook generation failed: {str(e)}")
        return jsonify({"error": "Failed to generate hooks. Please try again."}), 500

# YouTube upload routes (keeping existing)
@app.route('/api/upload_video', methods=['POST'])
def upload_video():
    if 'video_file' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video_file']
    video_id = request.form.get('video_id')
    title = request.form.get('title')
    description = request.form.get('description')
    tags = request.form.get('tags', '').split(',')
    category_id = request.form.get('category_id', "24")
    publish_time_str = request.form.get('publish_time')

    try:
        result = upload_to_youtube(
            video_file=video_file,
            video_id=video_id,
            title=title,
            description=description,
            tags=tags,
            category_id=category_id,
            publish_time_str=publish_time_str
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        app.logger.exception(f"Upload failed: {str(e)}")
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/api/authenticate_youtube', methods=['POST'])
def authenticate_youtube_endpoint():
    session.clear()
    try:
        auth_url, state = start_youtube_auth_flow()
        session['youtube_auth_state'] = state
        return jsonify({"auth_url": auth_url}), 200
    except Exception as e:
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 500

@app.route('/youtube_auth_callback')
def youtube_auth_callback():
    if 'youtube_auth_state' not in session:
        return "Invalid state", 400

    state = request.args.get('state')
    if state != session['youtube_auth_state']:
        return "State mismatch", 400

    try:
        code = request.args.get('code')
        youtube = complete_youtube_auth_flow(code)
        session.pop('youtube_auth_state', None)
        return redirect(url_for('services', auth_status='success'))
    except Exception as e:
        return redirect(url_for('services', auth_status=f'error: {str(e)}'))

# Test routes
@app.route('/test-instagram')
def test_instagram():
    try:
        result = generate_instagram_content("sunset beach photo", "tags", "trending", 10)
        return f"Success! Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/test-youtube')
def test_youtube():
    try:
        result = generate_youtube_content("how to cook pasta", "tags", 10)
        return f"Success! Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/test-twitter')
def test_twitter():
    try:
        result = generate_twitter_content("artificial intelligence", "tags", 10)
        return f"Success! Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/test-tiktok')
def test_tiktok():
    try:
        result = generate_tiktok_content("dance tutorial", "tags", 15)
        return f"Success! Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)