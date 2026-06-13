import os
from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS

app = Flask(__name__)
# تفعيل الـ CORS بشكل كامل لجميع المسارات
CORS(app, resources={r"/*": {"origins": "*"}})

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
        <title>Faycal TV Pro</title>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>
            body { background-color: #0e0e10; color: #ffffff; font-family: sans-serif; margin: 0; padding: 0; text-align: center; }
            .header-bar { background: #1f1f23; padding: 15px; font-size: 18px; font-weight: bold; border-bottom: 1px solid #2a2a30; }
            .header-bar span { color: #34c759; }
            .main-container { padding: 20px; max-width: 720px; margin: 0 auto; }
            video { width: 100%; aspect-ratio: 16/9; background: #000000; border-radius: 8px; border: 1px solid #2d2d34; display: block; }
            .status-log { background: #1f1f23; padding: 10px; margin-top: 15px; border-radius: 6px; font-size: 14px; color: #34c759; }
        </style>
    </head>
    <body>
        <div class="header-bar">Faycal TV - <span>HLS Stream Player</span></div>
        <div class="main-container">
            <video id="video" controls autoplay playsinline></video>
            <div class="status-log" id="status_message">جاري التحقق من اتصال البث...</div>
        </div>

        <script>
            var video = document.getElementById('video');
            var statusMessage = document.getElementById('status_message');
            var m3u8Url = "/stream/index.m3u8";

            if (Hls.isSupported()) {
                var hls = new Hls({
                    maxLiveSyncPlaybackRate: 1.5,
                    liveSyncDurationCount: 3,
                    enableWorker: true,
                    lowLatencyMode: true
                });
                hls.loadSource(m3u8Url);
                hls.attachMedia(video);
                hls.on(Hls.Events.MANIFEST_PARSED, function () {
                    statusMessage.innerText = "● البث المباشر شغال الآن بنجاح.";
                    video.play();
                });
                hls.on(Hls.Events.ERROR, function (event, data) {
                    if (data.fatal) {
                        statusMessage.innerText = "⚠️ في انتظار استقبال مقاطع الفيديو من الحاسوب الرئيسي...";
                        statusMessage.style.color = "#ffcc00";
                    }
                });
            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = m3u8Url;
                statusMessage.innerText = "● الاتصال مباشر عبر مشغل النظام.";
            }
        </script>
    </body>
    </html>
    """

# 📥 استقبال ملفات الـ m3u8 والـ ts من السكربت المحلي
@app.route('/upload/<filename>', methods=['PUT'])
def upload_file(filename):
    file_path = os.path.join(STREAM_DIR, filename)
    with open(file_path, 'wb') as f:
        f.write(request.data)
    return "OK", 200

# 📤 تقديم الملفات للمشغل في المتصفح مع إرسال الهيدرز الصحيحة وتخطي حظر CORS
@app.route('/stream/<filename>')
def serve_stream(filename):
    response = make_response(send_from_directory(STREAM_DIR, filename))
    
    # تصحيح نوع الـ Mime-Type بناءً على اللاحقة لكي يفهمها الهاتف فوراً
    if filename.endswith('.m3u8'):
        response.headers['Content-Type'] = 'application/vnd.apple.mpegurl'
    elif filename.endswith('.ts'):
        response.headers['Content-Type'] = 'video/mp2t'
        
    # إضافة هيدرز السماح بالوصول من أي مكان لمنع حظر المتصفح للمقاطع
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, threaded=True)
