import os
import requests
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)

# ئەڤ زانیاریان دێ ژ Railway وەرگریت
CLIENT_KEY = os.getenv('CLIENT_KEY')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

@app.route('/')
def index():
    return "<h1>TikTok Bot Control Center</h1><p>Bot is Active and Running.</p>"

@app.route('/login')
def login():
    # ئەڤ لینکە ڕێ دەتە بوتێ تە بچیتە د ناڤ هەر ئەکاونتەکی دا
    # Scopes: دەستهەڵاتێن بوتێ تە (زانیاری، لیستا ڤیدیۆیان، بڵاڤکرن)
    scopes = "user.info.basic,video.list,video.upload,video.publish"
    auth_url = f"https://www.tiktok.com/v2/auth/authorize/?client_key={CLIENT_KEY}&scope={scopes}&response_type=code&redirect_uri={REDIRECT_URI}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # وەرگرتنا کۆدێ تیک تۆکێ دهنێریت پاش چوونە ژوورێ
    code = request.args.get('code')
    if not code:
        return "Error: No code returned from TikTok", 400

    # گوهۆڕینا کۆدی بۆ Access Token یێ هەمیشەیی
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
    
    # نوکە بوت یێ ئامادەیە بۆ کارێ ب هێز
    return jsonify({
        "status": "Success",
        "message": "Bot is now authorized!",
        "data": token_data
    })

# ئەڤ بەشە بۆ وەرگرتنا لیستا ڤیدیۆیانە (نموونەیا کارەکێ ب هێز)
@app.route('/my-videos')
def get_videos():
    access_token = request.args.get('token')
    url = "https://open.tiktokapis.com/v2/video/list/"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(url, headers=headers, json={"max_count": 10})
    return jsonify(response.json())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
