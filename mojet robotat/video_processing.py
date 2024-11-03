import cv2
import socket
import numpy as np
# Установить сокет
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('<repka_pi_ip>', 5005)
# Запуск захвата видео
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    # Обработка для обнаружения объектов 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(gray, 1.1, 4)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    # Кодирование изображения для отправки
    _, buffer = cv2.imencode('.jpg', frame)
    data = np.array(buffer)
    sock.sendto(data.tobytes(), server_address)
cap.release()
sock.close()