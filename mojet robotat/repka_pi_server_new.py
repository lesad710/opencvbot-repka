import cv2
import socket
import numpy as np
from flask import Flask, render_template, Response, request
import wiringpi
# Настройка библиотеки WiringPi
wiringpi.wiringPiSetup()
# Определите пины для управления моторчиками
motor1_forward = 0  # WiringPi pin 0 corresponds to BCM 17
motor1_backward = 1  # WiringPi pin 1 corresponds to BCM 18
motor2_forward = 2  # WiringPi pin 2 corresponds to BCM 22
motor2_backward = 3  # WiringPi pin 3 corresponds to BCM 23
# Установить пины как выходные
wiringpi.pinMode(motor1_forward, 1)  # 1 = OUTPUT
wiringpi.pinMode(motor1_backward, 1)
wiringpi.pinMode(motor2_forward, 1)
wiringpi.pinMode(motor2_backward, 1)
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
            # Обработка для обнаружения объектов (
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
            wiringpi.digitalWrite(motor1_forward, 1)
            wiringpi.digitalWrite(motor1_backward, 0)
        elif direction == "backward":
            wiringpi.digitalWrite(motor1_forward, 0)
            wiringpi.digitalWrite(motor1_backward, 1)
    elif motor_num == 2:
        if direction == "forward":
            wiringpi.digitalWrite(motor2_forward, 1)
            wiringpi.digitalWrite(motor2_backward, 0)
        elif direction == "backward":
            wiringpi.digitalWrite(motor2_forward, 0)
            wiringpi.digitalWrite(motor2_backward, 1)
    return "OK"
@app.route('/stop')
def stop():
    wiringpi.digitalWrite(motor1_forward, 0)
    wiringpi.digitalWrite(motor1_backward, 0)
    wiringpi.digitalWrite(motor2_forward, 0)
    wiringpi.digitalWrite(motor2_backward, 0)
    return "Stopped"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)