import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# حفظ رابط الـ API المحلي الخاص بحاسوبك
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
        <title>Faycal TV Hybrid Pro</title>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>
            body {{ background-color: #0c0c0e; color: #ffffff; font-family: -apple-system, sans-serif; margin: 0; padding: 0; text-align: center; }}
            .app-bar {{ background: #16161a; padding: 15px; font-size: 20px; font-weight: bold; border-bottom: 1px solid #222227; }}
            .app-bar span {{ color: #ff3b30; }}
            .container {{ padding: 15px; max-width: 700px; margin: 0 auto; }}
            video {{ width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 12px; border: 1px solid #2c2c35; display: block; }}
            .status {{ background: #16161a; padding: 12px; margin-top: 15px; border-radius: 8px; font-size: 14px; color: #34c759; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="app-bar">Faycal <span>TV Hybrid API</span></div>
        <div class="container">
            <video id="video" controls autoplay playsinline></video>
            <div class="status" id="status_text">جاري الاتصال بالسحاب وفحص الـ API المحلي...</div>
        </div>

        <script>
            var video = document.getElementById('video');
            var statusText = document.getElementById('status_text');
            var localApiUrl = "{local_api}";

            if (localApiUrl) {{
                statusText.innerText = "🔄 جاري جلب الرابط الحي من الـ API الخاص بحاسوبك...";
                
                // الاتصال بالـ API المحلي الخاص بحاسوبك لجلب رابط البث والكوكيز الحالية
                fetch(localApiUrl)
                .then(response => response.json())
                .then(data => {{
                    if (data.stream_url) {{
                        statusText.innerText = "● البث متصل ومستقر الآن 🚀";
                        
                        if (Hls.isSupported()) {{
                            var hls = new Hls();
                            hls.loadSource(data.stream_url);
                            hls.attachMedia(video);
                            hls.on(Hls.Events.MANIFEST_PARSED, function () {{
                                video.play();
                            }});
                        }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                            video.src = data.stream_url;
                            video.addEventListener('loadedmetadata', function() {{
                                video.play();
                            }});
                        }}
                    }} else {{
                        statusText.innerText = "❌ الـ API المحلي لم يقم باصطياد أي رابط بعد.";
                        statusText.style.color = "#ff3b30";
                    }}
                }})
                .catch(err => {{
                    statusText.innerText = "❌ تعذر الاتصال بحاسوبك الرئيسي. تأكد من تشغيل السكربت المحلي ومن فتح المنفذ (Ngrok).";
                    statusText.style.color = "#ff3b30";
                }});
            }} else {{
                statusText.innerText = "❌ في انتظار تشغيل الـ API على الحاسوب الرئيسي وإرساله للسحاب...";
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
    if not data or 'local_api_url' not in data:
        return jsonify({"status": "error"}), 400
    
    # استقبال رابط الـ API وحفظه
    live_session["local_api_url"] = data['local_api_url']
    live_session["is_ready"] = True
    print(f"[+] Received Local API URL: {data['local_api_url']}")
    return jsonify({"status": "success"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, threaded=True)
