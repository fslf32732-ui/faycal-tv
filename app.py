import subprocess
import time
import threading
import os
import requests
from flask import Flask, Response, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ضع هنا الروابط المباشرة التي تريد تشغيلها (تتغير بسهولة في أي وقت)
SERVER_LINKS = {
    "1": "https://zz.depoooo.com/albaplayer/bein-1/?serv=1",
    "2": "https://zz.depoooo.com/albaplayer/bein-1/?serv=2",
    "3": "https://zz.depoooo.com/albaplayer/bein-1/?serv=3"
}

live_session = {
    "current_server": "1",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def generate_stable_stream():
    """
    سحب البث مباشرة من الرابط بأقل استهلاك ممكن لموارد السيرفر المجاني
    """
    active_url = SERVER_LINKS[live_session["current_server"]]
    
    headers = {
        "User-Agent": live_session["user_agent"],
        "Referer": active_url
    }
    
    # تحويل وإعادة بث ذكي متوافق 100% مع الهواتف وبدقة HD ثابتة ونقية
    command = [
        'ffmpeg',
        '-headers', f"User-Agent: {headers['User-Agent']}\r\nReferer: {headers['Referer']}\r\n",
        '-fflags', '+nobuffer+igndts',
        '-async', '1', '-vsync', '1',
        '-i', active_url,
        '-vf', 'scale=-2:720',             # جودة 720p HD مريحة ونظيفة للعين
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-crf', '25',                      # CRF متوازن جداً لمنع الضغط والتقطيع في السيرفر المجاني
        '-maxrate:v', '1200k',             # سقف بيانات ذكي ومناسب لإنترنت الهاتف في الجزائر
        '-bufsize:v', '1800k',
        '-c:a', 'aac', '-b:a', '96k',      # صوت ستيريو نقي وخفيف
        '-f', 'mp4', 
        '-movflags', 'frag_keyframe+empty_moov+default_base_moof',
        'pipe:1'
    ]
    
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        while True:
            data = process.stdout.read(4096)
            if not data:
                break
            yield data
    except Exception as e:
        print(f"[-] Client disconnected from stream")
    finally:
        try: process.kill()
        except: pass

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>Faycal TV Cloud</title>
        <style>
            * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
            body { background-color: #0c0c0e; color: #ffffff; font-family: -apple-system, sans-serif; margin: 0; padding: 0; overflow-x: hidden; }
            .app-bar { background: linear-gradient(to bottom, #16161a, #0c0c0e); padding: 15px 20px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #222227; position: sticky; top: 0; z-index: 100; }
            .brand { display: flex; align-items: center; gap: 10px; }
            .logo-icon { background: linear-gradient(135deg, #ff3b30, #ff9500); width: 35px; height: 35px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; box-shadow: 0 0 10px rgba(255, 59, 48, 0.4); }
            .app-title { font-size: 20px; font-weight: 800; }
            .app-title span { color: #ff3b30; }
            .live-badge { background-color: #ff3b30; color: white; font-size: 11px; font-weight: bold; padding: 4px 10px; border-radius: 20px; animation: pulse 1.5s infinite; }
            .main-container { padding: 15px; width: 100%; max-width: 800px; margin: 0 auto; }
            .player-wrapper { position: relative; width: 100%; background: #000; border-radius: 16px; overflow: hidden; box-shadow: 0px 10px 30px rgba(0,0,0,0.8); border: 1px solid #2c2c35; margin-bottom: 20px; }
            video { width: 100%; aspect-ratio: 16/9; display: block; }
            .channel-info { background: #16161a; border-radius: 14px; padding: 15px; border: 1px solid #222227; text-align: right; margin-bottom: 20px; }
            .channel-title { font-size: 16px; font-weight: bold; margin: 0 0 5px 0; }
            .channel-desc { font-size: 13px; color: #8e8e93; margin: 0; }
            .servers-section { text-align: right; }
            .section-label { font-size: 14px; color: #aeaeae; margin-bottom: 12px; padding-right: 5px; }
            .servers-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
            .server-btn { background: #1c1c24; border: 1px solid #2c2c35; color: #fff; padding: 14px; border-radius: 12px; font-size: 14px; font-weight: bold; cursor: pointer; transition: all 0.2s ease; }
            .server-btn.active { background: linear-gradient(135deg, #ff3b30, #ff453a); border-color: #ff3b30; box-shadow: 0 4px 12px rgba(255, 59, 48, 0.3); }
            @keyframes pulse { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }
        </style>
    </head>
    <body>
        <div class="app-bar">
            <div class="brand">
                <div class="logo-icon">F</div>
                <div class="app-title">Faycal <span>TV</span></div>
            </div>
            <div class="live-badge">بث سحابي مستقر ●</div>
        </div>
        <div class="main-container">
            <div class="player-wrapper">
                <video id="videoPlayer" controls autoplay playsinline>
                    <source src="/video_feed" type="video/mp4">
                    المشغل لا يدعم البث.
                </video>
            </div>
            <div class="channel-info">
                <h3 class="channel-title">beIN SPORTS 1 HD</h3>
                <p class="channel-desc">مستضاف بالكامل في السحاب - تم التحديث بنمط الاستهلاك المنخفض فائق السرعة الثابت.</p>
            </div>
            <div class="servers-section">
                <div class="section-label">اختر الجودة والسيرفر:</div>
                <div class="servers-grid">
                    <button id="btn1" class="server-btn active" onclick="changeServer('1')">سيرفر 1</button>
                    <button id="btn2" class="server-btn" onclick="changeServer('2')">سيرفر 2</button>
                    <button id="btn3" class="server-btn" onclick="changeServer('3')">سيرفر 3</button>
                </div>
            </div>
        </div>
        <script>
            function changeServer(serverId) {
                document.querySelectorAll('.server-btn').forEach(btn => btn.classList.remove('active'));
                document.getElementById('btn' + serverId).classList.add('active');
                
                fetch('/set_server?id=' + serverId)
                .then(response => response.json())
                .then(data => {
                    if(data.status === "success") {
                        var video = document.getElementById('videoPlayer');
                        video.load();
                        video.play();
                    }
                });
            }
        </script>
    </body>
    </html>
    """

@app.route('/set_server')
def set_server():
    global live_session
    server_id = request.args.get('id', '1')
    if server_id in SERVER_LINKS:
        live_session["current_server"] = server_id
        return jsonify({"status": "success", "server": server_id})
    return jsonify({"status": "error"})

@app.route('/video_feed')
def video_feed():
    return Response(generate_stable_stream(), mimetype='video/mp4')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, threaded=True)
