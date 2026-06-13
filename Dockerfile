# استخدام نسخة بايثون رسمية مجهزة لـ Playwright
FROM mcr.microsoft.com/playwright:v1.42.0-jammy

# تحديد مجلد العمل داخل السيرفر
WORKDIR /app

# نسخ ملفات المشروع
COPY . /app

# تثبيت مكتبات البايثون
RUN pip3 install --no-cache-dir -r requirements.txt

# تثبيت متصفح كروميوم التابع لـ Playwright داخل السيرفر
RUN playwright install chromium

# فتح المنفذ الصادر من السيرفر
EXPOSE 8000

# أمر تشغيل السكربت (سنستخدم منفذ 8000 ليتوافق مع السحاب)
CMD ["python3", "app.py"]
