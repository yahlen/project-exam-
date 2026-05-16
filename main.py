import cv2
import time
import requests
import json
import base64

# =======================================================
#    ( AIzaSyCxfXfjzkvOMmAvgfdsv8wUpDN9yFlBn24    )
# =======================================================
GEMINI_API_KEY = "AIzaSyCxfXfjzkvOMmAvgfdsv8wUpDN9yFlBn24 "
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

def ask_gemini(image_path):
    """دالة لترجمة الصورة وإرسالها لـ Gemini واستقبال الإجابة"""
    try:
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Read the question in this image and choose the correct answer from (A, B, C, D). Provide ONLY the final answer as a single letter and the option text (e.g., 'A) Option Text'). Be very concise."},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_data
                        }
                    }
                ]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload), timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            answer = result['contents'][0]['parts'][0]['text']
            return answer.strip()
        else:
            return "Error calling Gemini"
    except Exception as e:
        return f"Connection Error: {str(e)}"

# تشغيل كاميرا الموبايل الخلفية
cap = cv2.VideoCapture(0)

last_capture_time = 0
cooldown_period = 10  # مدة الانتظار (10 ثواني)
gemini_answer = "Waiting for alignment..."
status_color = (0, 0, 255) # أحمر في البداية

print("تم تشغيل التطبيق... وجه الكاميرا نحو الشاشة")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w, _ = frame.shape
    
    # 1. معالجة الصورة لكشف حدود الشاشة
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    screen_detected = False
    direction_text = "Align Screen"
    
    # البحث عن أكبر مستطيل (الشاشة)
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > (w * h * 0.25):  # الشاشة تشغل على الأقل 25% من الكادر
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            if len(approx) == 4:  # شكل رباعي الأركان
                screen_detected = True
                cv2.drawContours(frame, [approx], -1, (0, 255, 0), 3) # رسم خط أخضر حولها
                
                # حساب مركز الشاشة لضبط الاتجاه
                M = cv2.moments(approx)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    
                    # مقارنة مركز الشاشة بمركز كادر الكاميرا
                    if cX < (w // 2) - 40:
                        direction_text = "Move Right ->"
                        status_color = (0, 165, 255) # برتقالي
                    elif cX > (w // 2) + 40:
                        direction_text = "<- Move Left"
                        status_color = (0, 165, 255)
                    elif cY < (h // 2) - 40:
                        direction_text = "Move Down v"
                        status_color = (0, 165, 255)
                    elif cY > (h // 2) + 40:
                        direction_text = "Move Up ^"
                        status_color = (0, 165, 255)
                    else:
                        direction_text = "Screen Matched! [OK]"
                        status_color = (0, 255, 0) # أخضر
                break

    current_time = time.time()
    
    # 2. إذا كانت الشاشة مظبوطة تماماً ومرت 10 ثواني على آخر سؤال
    if screen_detected and direction_text == "Screen Matched! [OK]":
        if current_time - last_capture_time > cooldown_period:
            gemini_answer = "Analyzing Question..."
            # حفظ لقطة شاشة مؤقتة
            cv2.imwrite("question.jpg", frame)
            # إرسال لـ Gemini
            gemini_answer = ask_gemini("question.jpg")
            # تحديث الوقت
            last_capture_time = current_time

    # 3. عرض البيانات على شاشة الموبايل بشكل واضح
    # شريط سفلي لعرض الإجابة
    cv2.rectangle(frame, (0, h - 80), (w, h), (0, 0, 0), -1)
    cv2.putText(frame, f"Ans: {gemini_answer}", (15, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # مؤشر التوجيه في الأعلى
    cv2.rectangle(frame, (0, 0), (w, 60), (30, 30, 30), -1)
    cv2.putText(frame, direction_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
    
    # عرض العداد التنازلي للـ 10 ثواني
    time_left = int(cooldown_period - (current_time - last_capture_time))
    if time_left > 0 and gemini_answer != "Waiting for alignment...":
        cv2.putText(frame, f"Next in: {time_left}s", (w - 150, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    # عرض البث المباشر على شاشة التلفون
    cv2.imshow("Study Assistant", frame)

    # للخروج اضغط على زر الإغلاق في النافذة
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()