import os
import time
from flask import Flask, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# مخزن الإطار الحي الحالي (Buffer)
latest_frame = b""

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>Faycal OBS Cloud TV</title>
        <style>
            body { background-color: #0c0c0e; color: #ffffff; font-family: -apple-system, sans-serif; margin: 0; padding: 0; text-align: center; }
            .app-bar { background: #16161a; padding: 15px; font-size: 20px; font-weight: bold; border-bottom: 1px solid #222227; }
            .app-bar span { color: #34c759; }
            .container { padding: 15px; max-width: 800px; margin: 0 auto; }
            .screen { width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 16px; overflow: hidden; border: 1px solid #2c2c35; box-shadow: 0px 10px 30px rgba(0,0,0,0.8); }
            .screen img { width: 100%; height: 100%; object-fit: contain; display: block; }
            .status { background: #16161a; padding: 12px; margin-top: 15px; border-radius: 8px; font-size: 14px; color: #34c759; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="app-bar">Faycal <span>OBS Stream</span></div>
        <div class="container">
            <div class="screen">
                <img src="/video_feed" alt="في انتظار انطلاق البث من حاسوب OBS الرئيسي...">
            </div>
            <div class="status">● اتصال سحابي مباشر ومستقر بنمط OBS 🚀</div>
        </div>
    </body>
    </html>
    """

# 📥 مسار استقبال البث: حاسوبك يضخ الصور هنا باستمرار عبر POST
@app.route('/push_frame', methods=['POST'])
def push_frame():
    global latest_frame
    latest_frame = request.data
    return "OK", 200

def generate_stream():
    global latest_frame
    last_sent_frame = b""
    while True:
        if latest_frame and latest_frame != last_sent_frame:
            last_sent_frame = latest_frame
            # تغليف الإطار ليفهمه المتصفح فوراً كتيار متصل
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
        else:
            time.sleep(0.02) # حماية معالج السيرفر عند انتظار إطارات جديدة

# 📤 مسار عرض البث للهواتف
@app.route('/video_feed')
def video_feed():
    return Response(generate_stream(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, threaded=True)
