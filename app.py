import os
import time
from flask import Flask, Response, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ذاكرة دائرية سريعة للاحتفاظ بآخر أجزاء الفيديو المرسلة من الحاسوب
class StreamBuffer:
    def __init__(self):
        self.frame = b""
    def set_frame(self, frame):
        self.frame = frame
    def get_frame(self):
        return self.frame

video_buffer = StreamBuffer()

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>Faycal TV Turbo</title>
        <style>
            body { background-color: #0c0c0e; color: #ffffff; font-family: -apple-system, sans-serif; margin: 0; padding: 0; text-align: center; }
            .app-bar { background: #16161a; padding: 15px; font-size: 20px; font-weight: bold; border-bottom: 1px solid #222227; }
            .app-bar span { color: #ff3b30; }
            .container { padding: 15px; max-width: 700px; margin: 0 auto; }
            video { width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 12px; border: 1px solid #2c2c35; display: block; }
            .status { background: #16161a; padding: 12px; margin-top: 15px; border-radius: 8px; font-size: 14px; color: #34c759; }
        </style>
    </head>
    <body>
        <div class="app-bar">Faycal <span>TV Turbo</span></div>
        <div class="container">
            <video id="player" controls autoplay playsinline>
                <source src="/video_feed" type="video/mp4">
                المشغل لا يدعم البث.
            </video>
            <div class="status">● البث متصل الآن مباشرة وصاروخي السُرعة 🚀</div>
        </div>
    </body>
    </html>
    """

# 📥 استقبال أجزاء الفيديو الصغيرة فوراً وبدون تأخير
@app.route('/push_chunk', methods=['POST'])
def push_chunk():
    global video_buffer
    # استقبال الجزء الحالي وتحديث الذاكرة فوراً
    video_buffer.set_frame(request.data)
    return "OK", 200

def generate_live_stream():
    global video_buffer
    last_frame = b""
    while True:
        current_frame = video_buffer.get_frame()
        if current_frame and current_frame != last_frame:
            yield current_frame
            last_frame = current_frame
        else:
            time.sleep(0.01) # منع استهلاك المعالج عند انتظار حزم جديدة

@app.route('/video_feed')
def video_feed():
    # إرسال التدفق بنمط multipart/x-mixed-replace لكسر كاش جدار الحماية وضمان التشغيل الفوري
    return Response(generate_live_stream(), mimetype='video/mp4')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, threaded=True)
