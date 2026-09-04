import os
import requests
from flask import Flask, request, jsonify, redirect, render_template_string

app = Flask(__name__)

# وەرگرتنا زانیاریان ژ Variables یێن Railway
CLIENT_KEY = os.getenv('CLIENT_KEY')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

# لاپەڕێ سەرەکی (Dashboard)
@app.route('/')
def index():
    return """
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>TikTok Bot Control Center</h1>
        <p>Status: <span style="color:green">Active</span></p>
        <hr>
        <a href="/login"><button style="padding:15px 30px; font-size:18px; background:blue; color:white; border:none; border-radius:8px; cursor:pointer;">Connect TikTok Account</button></a>
    </body>
    """

# --- ١. بەشێ چوونە ژوورێ (Authentication) ---
@app.route('/login')
def login():
    # ئەڤە لینکێ فەرمی یێ تیک تۆکێ یە -Scopes دیار دکەن بوت دێ چ کەت
    scopes = "user.info.basic,video.list,video.upload,video.publish"
    auth_url = f"https://www.tiktok.com/v2/auth/authorize?client_key={CLIENT_KEY}&scope={scopes}&response_type=code&redirect_uri={REDIRECT_URI}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Error: No code returned", 400

    # گوهۆڕینا Code بۆ Access Token
    url = "https://open.tiktokapis.com/v2/oauth/token/"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'client_key': CLIENT_KEY,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }
    
    r = requests.post(url, headers=headers, data=data)
    token_info = r.json()
    
    # لێرە Token دێ نیشا دەت (د کارێ ڕاستەقینە دا دێ هێتە پاراستن)
    return jsonify({
        "status": "Authenticated Successfully",
        "access_token": token_info.get('access_token'),
        "message": "Copy this token to use in other functions"
    })

# --- ٢. بەشێ بینینا زانیاریێن ئەکاونتی ---
@app.route('/profile')
def get_profile():
    token = request.args.get('token') # دێ توکنێ د لینکێ دا فرێ کەی
    if not token: return "Missing Token", 400
    
    url = "https://open.tiktokapis.com/v2/user/info/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"fields": "display_name,avatar_url,follower_count"}
    
    r = requests.get(url, headers=headers, params=params)
    return jsonify(r.json())

# --- ٣. بەشێ لیستا ڤیدیۆیان (Analytics) ---
@app.route('/videos')
def get_videos():
    token = request.args.get('token')
    if not token: return "Missing Token", 400

    url = "https://open.tiktokapis.com/v2/video/list/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"max_count": 10}
    
    r = requests.post(url, headers=headers, json=data)
    return jsonify(r.json())

# --- ٤. بەشێ بڵاڤکرنا ڤیدیۆیان (Upload) ---
@app.route('/publish')
def publish_video():
    token = request.args.get('token')
    video_url = request.args.get('video_url') # لایەنێ ڤیدیۆیا تە دڤێت بڵاڤ کەی
    
    if not token or not video_url: return "Missing Info", 400

    url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {
        "source_info": {
            "source": "PULL_FROM_URL",
            "video_url": video_url
        }
    }
    
    r = requests.post(url, headers=headers, json=body)
    return jsonify(r.json())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
