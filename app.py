import os
from flask import Flask, Response, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# مخزن مؤقت لاستقبال دفق الفيديو من حاسوبك
video_buffer = b""
is_pc_connected = False

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>Faycal TV PC-Stream</title>
        <style>
            * { box-sizing: border-box; }
            body { background-color: #0c0c0e; color: #ffffff; font-family: -apple-system, sans-serif; margin: 0; padding: 0; text-align: center; }
            .app-bar { background: #16161a; padding: 15px; font-size: 20px; font-weight: bold; border-bottom: 1px solid #222227; }
            .app-bar span { color: #ff3b30; }
            .container { padding: 15px; max-width: 700px; margin: 0 auto; }
            video { width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 12px; border: 1px solid #2c2c35; display: block; }
            .status { background: #16161a; padding: 12px; margin-top: 15px; border-radius: 8px; font-size: 14px; color: #8e8e93; }
        </style>
    </head>
    <body>
        <div class="app-bar">Faycal <span>TV Live</span></div>
        <div class="container">
            <video id="player" controls autoplay playsinline>
                <source src="/video_feed" type="video/mp4">
                المشغل لا يدعم البث.
            </video>
            <div class="status">تم ربط الهاتف بالسحاب. البث يتدفق الآن مباشرة من الحاسوب الرئيسي 🚀</div>
        </div>
    </body>
    </html>
    """

# 📥 المدخل السري: حاسوبك يضخ الفيديو باستمرار إلى هنا
@app.route('/stream_input', methods=['POST'])
def stream_input():
    global video_buffer, is_pc_connected
    is_pc_connected = True
    try:
        # قراءة البيانات المتدفقة من الحاسوب وحفظها في الذاكرة
        while True:
            chunk = request.stream.read(4096)
            if not chunk:
                break
            video_buffer = chunk
        return jsonify({"status": "ended"})
    except:
        is_pc_connected = False
        return jsonify({"status": "disconnected"}), 500

def generate_stream():
    global video_buffer, is_pc_connected
    while True:
        if video_buffer:
            yield video_buffer
            time.sleep(0.01) # تنظيم التدفق لمنع الضغط

@app.route('/video_feed')
def video_feed():
    return Response(generate_stream(), mimetype='video/mp4')

if __name__ == '__main__':
    import time
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, threaded=True)
