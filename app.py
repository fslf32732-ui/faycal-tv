import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

live_session = {
    "local_api_url": "",
    "is_ready": False
}

@app.route('/')
def index():
    global live_session
    local_api = live_session["local_api_url"] if live_session["is_ready"] else ""
    
    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>Faycal TV Hybrid Turbo</title>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>
            body {{ background-color: #0c0c0e; color: #ffffff; font-family: -apple-system, sans-serif; margin: 0; padding: 0; text-align: center; }}
            .app-bar {{ background: #16161a; padding: 15px; font-size: 20px; font-weight: bold; border-bottom: 1px solid #222227; }}
            .app-bar span {{ color: #ff3b30; }}
            .container {{ padding: 15px; max-width: 700px; margin: 0 auto; }}
            video {{ width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 12px; border: 1px solid #2c2c35; display: block; }}
            .status {{ background: #16161a; padding: 12px; margin-top: 15px; border-radius: 8px; font-size: 14px; color: #34c759; font-weight: bold; }}
            .btn-play {{ display: inline-block; background: #34c759; color: white; padding: 12px 24px; border-radius: 8px; font-weight: bold; margin-top: 10px; text-decoration: none; cursor: pointer; border: none; }}
        </style>
    </head>
    <body>
        <div class="app-bar">Faycal <span>TV Ultra</span></div>
        <div class="container">
            <video id="video" controls autoplay playsinline muted></video>
            <button class="btn-play" id="play_btn" onclick="forcePlay()">▶ اضغط هنا لتشغيل الصوت والبث فوراً</button>
            <div class="status" id="status_text">جاري استقبال البيانات...</div>
        </div>

        <script>
            var video = document.getElementById('video');
            var statusText = document.getElementById('status_text');
            var playBtn = document.getElementById('play_btn');
            var localApiUrl = "{local_api}";

            function forcePlay() {{
                video.muted = false;
                video.play();
                playBtn.style.display = "none";
            }}

            if (localApiUrl) {{
                fetch(localApiUrl, {{
                    method: 'GET',
                    headers: {{ 'ngrok-skip-browser-warning': 'true' }}
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.stream_url) {{
                        statusText.innerText = "● جاري إقلاع البث الصاروخي... 🚀";
                        
                        if (Hls.isSupported()) {{
                            var hls = new Hls({{
                                maxMaxBufferLength: 10, // تقليل البافر لمنع الدوران واللاق
                                enableWorker: true,
                                // تزوير الطلبات لجعل موقع البث يظن أننا نشاهده من موقعه الأصلي
                                xhrSetup: function (xhr, url) {{
                                    xhr.withCredentials = false;
                                }}
                            }});
                            hls.loadSource(data.stream_url);
                            hls.attachMedia(video);
                            hls.on(Hls.Events.MANIFEST_PARSED, function () {{
                                video.play().catch(function(e) {{
                                    statusText.innerText = "💡 اضغط على الزر الأخضر في الأسفل لتشغيل البث والصوت!";
                                }});
                            }});
                        }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                            video.src = data.stream_url;
                        }}
                    }}
                }})
                .catch(err => {{
                    statusText.innerText = "❌ خطأ في قراءة بيانات حاسوبك.";
                }});
            }}
        </script>
    </body>
    </html>
    """

@app.route('/update_stream', methods=['POST'])
def update_stream():
    global live_session
    data = request.json
    if not data or 'local_api_url' not in data:
        return jsonify({"status": "error"}), 400
    live_session["local_api_url"] = data['local_api_url']
    live_session["is_ready"] = True
    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, threaded=True)
