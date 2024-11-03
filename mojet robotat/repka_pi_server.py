import cv2
import socket
import numpy as np
from flask import Flask, render_template, Response, request
import RPi.GPIO as GPIO
# Настройка GPIO
GPIO.setmode(GPIO.BCM)
motor1_forward = 17
motor1_backward = 18
motor2_forward = 22
motor2_backward = 23
GPIO.setup(motor1_forward, GPIO.OUT)
GPIO.setup(motor1_backward, GPIO.OUT)
GPIO.setup(motor2_forward, GPIO.OUT)
GPIO.setup(motor2_backward, GPIO.OUT)
app = Flask(__name__)
# Создаем сокет для получения видео
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 5005))
# Инициализация каскадного классификатора
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
def gen_frames():
    while True:
        data, _ = sock.recvfrom(65536)
        np_data = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
        if frame is not None:
            # Обработка для обнаружения объектов 
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            # Преобразовать в JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/move', methods=['POST'])
def move():
    direction = request.form.get('direction')
    motor_num = int(request.form.get('motor'))
    if motor_num == 1:
        if direction == "forward":
            GPIO.output(motor1_forward, GPIO.HIGH)
            GPIO.output(motor1_backward, GPIO.LOW)
        elif direction == "backward":
            GPIO.output(motor1_forward, GPIO.LOW)
            GPIO.output(motor1_backward, GPIO.HIGH)
    elif motor_num == 2:
        if direction == "forward":
            GPIO.output(motor2_forward, GPIO.HIGH)
            GPIO.output(motor2_backward, GPIO.LOW)
        elif direction == "backward":
            GPIO.output(motor2_forward, GPIO.LOW)
            GPIO.output(motor2_backward, GPIO.HIGH)
    return "OK"
@app.route('/stop')
def stop():
    GPIO.output(motor1_forward, GPIO.LOW)
    GPIO.output(motor1_backward, GPIO.LOW)
    GPIO.output(motor2_forward, GPIO.LOW)
    GPIO.output(motor2_backward, GPIO.LOW)
    return "Stopped"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)