import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from youtube_service import upload_to_youtube, authenticate_youtube, start_youtube_auth_flow, complete_youtube_auth_flow
from auth_service import start_google_auth_flow, complete_google_auth_flow, store_user_data
from google_auth_oauthlib.flow import Flow
import sys

app = Flask(__name__)
app.secret_key = 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500mb

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Capture print statements into logs
class StreamToLogger:
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

# Redirect stdout and stderr to logger
sys.stdout = StreamToLogger(logger, logging.INFO)
sys.stderr = StreamToLogger(logger, logging.ERROR)

# Ensure Flask logs exceptions
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    logger.debug("Session cleared before starting auth flow")
    if request.method == 'POST':
        logger.debug("Starting Google auth flow")
        auth_url, state = start_google_auth_flow()
        logger.debug(f"Generated auth_url: {auth_url}")
        logger.debug(f"State: {state}")
        session['oauth_state'] = state
        return redirect(auth_url)
    return render_template('login.html')

@app.route('/oauth2callback')
def oauth2callback():
    if 'oauth_state' not in session:
        logger.error("Invalid state in oauth2callback: No state in session")
        return "Invalid state", 400
    state = request.args.get('state')
    if state != session['oauth_state']:
        logger.error(f"State mismatch in oauth2callback: Expected {session['oauth_state']}, got {state}")
        return "State mismatch", 400
    code = request.args.get('code')
    if not code:
        logger.error("No authorization code in oauth2callback")
        return "No authorization code", 400
    logger.debug(f"Received code: {code}")
    google = complete_google_auth_flow(code)
    user_id = store_user_data(google)
    logger.debug(f"Logged in user_id: {user_id}")
    session.pop('oauth_state', None)
    session['user_id'] = user_id
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    logger.debug("User logged out")
    return redirect(url_for('home'))

@app.route('/clear_session')
def clear_session():
    session.clear()
    logger.debug("Session cleared")
    return "Session cleared", 200

@app.route('/api/upload_video', methods=['POST'])
def upload_video():
    if 'video_file' not in request.files:
        logger.error("No video file provided in request")
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video_file']
    video_id = request.form.get('video_id')
    title = request.form.get('title')
    description = request.form.get('description')
    tags = request.form.get('tags', '').split(',')
    category_id = request.form.get('category_id', "24")
    publish_time_str = request.form.get('publish_time')

    logger.debug(f"Received: video_id={video_id}, title={title}")
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
        logger.info(f"Upload successful: {result}")
        return jsonify(result), 200
    except ValueError as e:
        logger.error(f"ValueError in upload: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception(f"Upload failed with exception: {str(e)}")
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


@app.route('/api/authenticate_youtube', methods=['POST'])
def authenticate_youtube_endpoint():
    session.clear()
    try:
        auth_url, state = start_youtube_auth_flow()
        session['youtube_auth_state'] = state
        logger.info("Generated YouTube auth URL")
        return jsonify({"auth_url": auth_url}), 200
    except Exception as e:
        logger.error(f"YouTube authentication initiation failed: {str(e)}")
        return jsonify({"error": f"Authentication failed: {str(e)}"}), 500

@app.route('/youtube_auth_callback')
def youtube_auth_callback():
    if 'youtube_auth_state' not in session:
        logger.error("Invalid state in youtube_auth_callback")
        return "Invalid state", 400

    state = request.args.get('state')
    if state != session['youtube_auth_state']:
        logger.error(f"State mismatch in youtube_auth_callback: Expected {session['youtube_auth_state']}, got {state}")
        return "State mismatch", 400

    try:
        code = request.args.get('code')
        youtube = complete_youtube_auth_flow(code)
        session.pop('youtube_auth_state', None)
        logger.info("YouTube authentication successful")
        return redirect(url_for('services', auth_status='success'))
    except Exception as e:
        logger.error(f"YouTube auth callback failed: {str(e)}")
        return redirect(url_for('services', auth_status=f'error: {str(e)}'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)