import os
from flask import Flask, request, jsonify, redirect, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# الذاكرة السحابية لاستقبال الرابط من حاسوبك
live_session = {
    "stream_url": None,
    "is_ready": False
}

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>Faycal TV Instant Cloud</title>
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
        <div class="app-bar">Faycal <span>TV Live</span></div>
        <div class="container">
            <video id="player" controls autoplay playsinline>
                <source src="/redirect_stream" type="application/x-mpegURL">
                المشغل لا يدعم البث المباشر، جرب فتحه عبر تطبيق VLC أو متصفح سفاري/كروم حديث.
            </video>
            <div class="status">تم تفعيل نظام التوجيه الفوري الصاروخي 🚀</div>
        </div>
    </body>
    </html>
    """

@app.route('/update_stream', methods=['POST'])
def update_stream():
    global live_session
    data = request.json
    if not data or 'stream_url' not in data:
        return jsonify({"status": "error"}), 400
    
    live_session["stream_url"] = data['stream_url']
    live_session["is_ready"] = True
    return jsonify({"status": "success"})

@app.route('/redirect_stream')
def redirect_stream():
    global live_session
    if not live_session["is_ready"] or not live_session["stream_url"]:
        return Response("جاري انتظار الرابط من الحاسوب...", mimetype='text/plain', status=202)
    
    # تحويل الهاتف مباشرة وبسرعة خارقة إلى رابط الـ m3u8 الأصلي الشغال
    return redirect(live_session["stream_url"])

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port, threaded=True)
