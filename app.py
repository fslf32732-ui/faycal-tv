import os
from flask import Flask, Response, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# مخزن الإطار الحالي للبث
current_frame = b""

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>Faycal TV MJPEG</title>
        <style>
            * { box-sizing: border-box; }
            body { background-color: #0c0c0e; color: #ffffff; font-family: -apple-system, sans-serif; margin: 0; padding: 0; }
            .app-bar { background: #16161a; padding: 15px; font-size: 20px; font-weight: bold; text-align: center; border-bottom: 1px solid #222227; }
            .app-bar span { color: #ff3b30; }
            .container { padding: 15px; max-width: 800px; margin: 0 auto; text-align: center; }
            .stream-viewport { width: 100%; aspect-ratio: 16/9; background: #000; border-radius: 16px; overflow: hidden; border: 1px solid #2c2c35; box-shadow: 0px 10px 30px rgba(0,0,0,0.8); }
            .stream-viewport img { width: 100%; height: 100%; object-fit: contain; display: block; }
            .status { background: #16161a; padding: 12px; margin-top: 15px; border-radius: 8px; font-size: 14px; color: #34c759; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="app-bar">Faycal <span>TV Live</span></div>
        <div class="container">
            <div class="stream-viewport">
                <img src="/video_feed" alt="جاري الاتصال بمصدر البث الرئيسي...">
            </div>
            <br>
            <div class="status">● متصل وفيصل فائق السرعة 🚀</div>
        </div>
    </body>
    </html>
    """

@app.route('/push_frame', methods=['POST'])
def push_frame():
    global current_frame
    current_frame = request.data
    return "OK", 200

def generate_mjpeg_stream():
    global current_frame
    while True:
        if current_frame:
            # تغليف الإطار بمعيار الـ MJPEG الصامت ليفهمه المتصفح فوراً دون دوران
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + current_frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    # كسر جدار الحماية وبدء الدفق الصاروخي المستمر
    return Response(generate_mjpeg_stream(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, threaded=True)
