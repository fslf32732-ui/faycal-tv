import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# الذاكرة السحابية المؤقتة لحفظ بيانات البث القادمة من حاسوبك
live_session = {
    "stream_url": "",
    "cookies_str": "",
    "referer_url": "",
    "is_ready": False
}

@app.route('/')
def index():
    global live_session
    stream_url = live_session["stream_url"] if live_session["is_ready"] else ""
    
    # كود الواجهة والمشغل الذكي hls.js مدمج هنا بدقة
    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>Faycal TV Pro Live</title>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>
            body {{ background-color: #0c0c0e; color: #ffffff; font-family: -apple-system, sans-serif; margin: 0; padding: 0; text-align: center; }}
            .app-bar {{ background: #16161a; padding: 15px; font-size: 20px; font-weight: bold; border-bottom: 1px solid #222227; }}
            .app-bar span {{ color: #ff3b30; }}
            .container {{ padding: 15px; max-width: 700px; margin: 0 auto; }}
            video {{ width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 12px; border: 1px solid #2c2c35; display: block; }}
            .status {{ background: #16161a; padding: 12px; margin-top: 15px; border-radius: 8px; font-size: 14px; color: #34c759; }}
        </style>
    </head>
    <body>
        <div class="app-bar">Faycal <span>TV HLS Pro</span></div>
        <div class="container">
            <video id="video" controls autoplay playsinline></video>
            <div class="status" id="status_text">جاري فحص اتصال السحاب الرئيسي...</div>
        </div>

        <script>
            var video = document.getElementById('video');
            var statusText = document.getElementById('status_text');
            var streamUrl = "{stream_url}";

            if (streamUrl) {{
                statusText.innerText = "● تم جلب الرابط الحي! جاري تشغيل البث الصاروخي... 🚀";
                
                if (Hls.isSupported()) {{
                    var hls = new Hls();
                    hls.loadSource(streamUrl);
                    hls.attachMedia(video);
                    hls.on(Hls.Events.MANIFEST_PARSED, function () {{
                        video.play();
                    }});
                }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                    // دعم هواتف الآيفون ومتصفح سفاري تلقائياً
                    video.src = streamUrl;
                    video.addEventListener('loadedmetadata', function() {{
                        video.play();
                    }});
                }}
            }} else {{
                statusText.innerText = "❌ في انتظار تشغيل السكربت على الحاسوب الرئيسي...";
                statusText.style.color = "#ff9500";
            }}
        </script>
    </body>
    </html>
    """

@app.route('/update_stream', methods=['POST'])
def update_stream():
    global live_session
    data = request.json
    if not data or 'stream_url' not in data:
        return jsonify({"status": "error"}), 400
    
    # استقبال البيانات وتحديث الذاكرة بسلام بدون تداخل الأقواس المزدوجة
    live_session["stream_url"] = data['stream_url']
    live_session["cookies_str"] = data.get('cookies', '')
    live_session["referer_url"] = data.get('referer', '')
    live_session["is_ready"] = True
    print("[+] Cloud: Received stream URL successfully!")
    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, threaded=True)
