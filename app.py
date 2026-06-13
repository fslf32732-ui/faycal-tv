import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# مجلد مؤقت داخل السيرفر لحفظ مقاطع الفيديو القادمة من حاسوبك
STREAM_DIR = "/tmp/hls_stream"
if not os.path.exists(STREAM_DIR):
    os.makedirs(STREAM_DIR)

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>Faycal Smart OBS TV</title>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>
            body { background-color: #0c0c0e; color: #ffffff; font-family: -apple-system, sans-serif; margin: 0; padding: 0; text-align: center; }
            .app-bar { background: #16161a; padding: 15px; font-size: 20px; font-weight: bold; border-bottom: 1px solid #222227; }
            .app-bar span { color: #34c759; }
            .container { padding: 15px; max-width: 700px; margin: 0 auto; }
            video { width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 12px; border: 1px solid #2c2c35; display: block; }
            .status { background: #16161a; padding: 12px; margin-top: 15px; border-radius: 8px; font-size: 14px; color: #34c759; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="app-bar">Faycal <span>Smart Failover HLS</span></div>
        <div class="container">
            <video id="video" controls autoplay playsinline></video>
            <div class="status" id="status_text">📡 منظومة التناوب الثلاثية متصلة بالسحاب وصوت وصورة بجودة خارقة...</div>
        </div>

        <script>
            var video = document.getElementById('video');
            var statusText = document.getElementById('status_text');
            var streamUrl = "/stream/index.m3u8";

            if (Hls.isSupported()) {
                var hls = new Hls({
                    maxLiveSyncPlaybackRate: 1.5,
                    liveSyncDurationCount: 2,
                    enableWorker: true
                });
                hls.loadSource(streamUrl);
                hls.attachMedia(video);
                hls.on(Hls.Events.MANIFEST_PARSED, function () {
                    video.play();
                });
            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = streamUrl;
            }
        </script>
    </body>
    </html>
    """

# 📥 مسار استقبال الملفات من حاسوبك الشخصي
@app.route('/upload/<filename>', methods=['PUT'])
def upload_file(filename):
    file_path = os.path.join(STREAM_DIR, filename)
    with open(file_path, 'wb') as f:
        f.write(request.data)
    return "OK", 200

# 📤 مسار تقديم الملفات للمشغل في الهاتف
@app.route('/stream/<filename>')
def serve_stream(filename):
    return send_from_directory(STREAM_DIR, filename)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, threaded=True)
