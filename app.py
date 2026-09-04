import os
import requests
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

# وەرگرتنا زانیاریان ژ Variables یێن Railway
CLIENT_KEY = os.getenv('CLIENT_KEY')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

@app.route('/')
def index():
    return """
    <h1>TikTok Bot Control Center</h1>
    <p>Status: <span style='color:green'>Active</span></p>
    <hr>
    <a href='/login'><button style='padding:10px 20px; background:blue; color:white; border:none; border-radius:5px; cursor:pointer;'>Connect TikTok Account</button></a>
    """

# --- ١. بەشێ چوونە ژوورێ (Authentication) ---
@app.route('/login')
def login():
    # ئەڤە لینکێ فەرمی یێ تیک تۆکێ یە بۆ دەستهەڵاتێ
    # تێبینی: Scopes دیار دکەن کا بوت دێ چ کاران کەت
    scopes = "user.info.basic,video.list,video.upload,video.publish"
    auth_url = f"https://www.tiktok.com/v2/auth/authorize?client_key={CLIENT_KEY}&scope={scopes}&response_type=code&redirect_uri={REDIRECT_URI}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return "Error: No code returned from TikTok", 400

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
    
    response = requests.post(url, headers=headers, data=data)
    token_data = response.json()
    
    # لێرە Token دێ هێتە پاراستن (د داتابەیسەکێ دا یان پیشاندان)
    return jsonify({
        "message": "Login Successful!",
        "access_token": token_data.get('access_token'),
        "expires_in": token_data.get('expires_in')
    })

# --- ٢. بەشێ ئانالیزا ئەکاونتی (Analytics) ---
@app.route('/profile')
def get_profile():
    token = request.args.get('token')
    url = "https://open.
