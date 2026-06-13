import subprocess
import time
import os
from flask import Flask, Response, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# الذاكرة السحابية المؤقتة لاستقبال البيانات من حاسوبك الشخصي
live_session = {
    "stream_url": None,
    "cookies_str": "",
    "referer_url": "https://zz.depoooo.com/albaplayer/bein-1/?serv=1",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "is_ready": False
}

def generate_cloud_stream():
    global live_session
    if not live_session["is_ready"] or not live_session["stream_url"]:
        return b""

    headers = (
        f"User-Agent: {live_session['user_agent']}\r\n"
        f"Referer: {live_session['referer_url']}\r\n"
        f"Cookie: {live_session['cookies_str']}\r\n"
    )
    
    command = [
        'ffmpeg',
        '-headers', headers,
        '-fflags', '+nobuffer+igndts',
        '-async', '1', '-vsync', '1',
        '-i', live_session["stream_url"],
        '-vf', 'scale=-2:720',             # جودة 720p HD نقية وثابتة
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-tune', 'zerolatency',
        '-crf', '24',
        '-maxrate:v', '1400k',
        '-bufsize:v', '2000k',
        '-c:a', 'aac', '-b:a', '128k',
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
        pass
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
        <title>Faycal TV Hybrid Cloud</title>
        <style>
            body { background-color: #0c0c0e; color: #ffffff; font-family: -apple-system, sans-serif; margin: 0; padding: 0; text-align: center; }
            .app-bar { background: #16161a; padding: 15px; font-size: 20px; font-weight: bold; border-bottom: 1px solid #222227; }
            .app-bar span { color: #ff3b30; }
            .container { padding: 15px; max-width: 600px; margin: 0 auto; }
            video { width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 12px; border: 1px solid #2c2c35; }
            .status { background: #16161a; padding: 12px; margin-top: 15px; border-radius: 8px; font-size: 14px; color: #8e8e93; }
        </style>
    </head>
    <body>
        <div class="app-bar">Faycal <span>TV Hybrid</span></div>
        <div class="container">
            <video id="player" controls autoplay playsinline>
                <source src="/video_feed" type="video/mp4">
            </video>
            <div class="status">النظام متصل بالسحاب ومؤمن بالكامل. البث يعمل تلقائياً عند استقبال الرابط من الحاسوب الرئيسي.</div>
        </div>
    </body>
    </html>
    """

# 🛡️ نقطة الاستقبال السرية: حاسوبك يرسل البيانات إلى هنا
@app.route('/update_stream', methods=['POST'])
def update_stream():
    global live_session
    data = request.json
    if not data or 'stream_url' not in data:
        return jsonify({"status": "error", "message": "Missing stream_url"}), 400
    
    live_session["stream_url"] = data['stream_url']
    live_session["cookies_str"] = data.get('cookies', '')
    live_session["referer_url"] = data.get('referer', live_session["referer_url"])
    live_session["is_ready"] = True
    
    print(f"[+] Cloud Received New URL: {live_session['stream_url'][:50]}...")
    return jsonify({"status": "success", "message": "Cloud Stream updated successfully!"})

@app.route('/video_feed')
def video_feed():
    if not live_session["is_ready"]:
        return Response("جاري انتظار بث الحاسوب الرئيسي...", mimetype='text/plain', status=202)
    return Response(generate_cloud_stream(), mimetype='video/mp4')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, threaded=True)
