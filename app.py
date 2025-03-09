# app.py
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from youtube_service import upload_to_youtube  # Unchanged import
from auth_service import authenticate_google, store_user_data  # New import

app = Flask(__name__)
app.secret_key = 'abd2332c672f142303ff666182f64bc5'


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
    if 'user_id' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        google = authenticate_google()
        user_id = store_user_data(google)
        print(google)
        print("****************")
        print(user_id)
        session['user_id'] = user_id
        return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/api/upload_video', methods=['POST'])
def upload_video():
    """Handle video upload request and call the service."""
    if 'video_file' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video_file = request.files['video_file']
    video_id = request.form.get('video_id')
    title = request.form.get('title')
    description = request.form.get('description')
    tags = request.form.get('tags', '').split(',')  # Ensure tags exist
    category_id = request.form.get('category_id', "24")
    publish_time_str = request.form.get('publish_time')

    print(f"Received: video_id={video_id}, title={title}")

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
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)