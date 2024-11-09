from flask import Flask, Response
import cv2

app = Flask(__name__)

# Функция для захвата видео с веб-камеры
def generate_frames():
    camera = cv2.VideoCapture(0)  # 0 - это индекс вашей веб-камеры
    while True:
        success, frame = camera.read()  # Чтение кадра из веб-камеры
        if not success:
            break
        else:
            # Конвертация кадра в нужный формат для передачи по сети
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()  # Преобразование в байты

            # Возвращаем кадры в виде потока
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Роут для отображения видео
@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Главная страница
@app.route('/')
def index():
    return '<h1>Трансляция видео с веб-камеры</h1><img src="/video">'

# Запуск сервера
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # Доступно на всех интерфейсах и порту 5000
