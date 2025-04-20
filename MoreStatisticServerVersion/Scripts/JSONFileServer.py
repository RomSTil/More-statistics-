import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
import qrcode
import os
import platform
from pathlib import Path
import random
import time
import subprocess
import webbrowser


class DownloadHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, json_file_path=None, **kwargs):
        self.json_file_path = json_file_path
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/download':
            try:
                with open(self.json_file_path, 'rb') as f:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Content-Disposition', 
                                   f'attachment; filename="{os.path.basename(self.json_file_path)}"')
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_error(404, "File Not Found")
        else:
            self.send_error(404, "Not Found")


class JSONFileServer:
    def __init__(self, json_file_path: str, port: int = 8000):
        self.json_file_path = Path(json_file_path).absolute()
        self.port = port
        self.local_ip = self._get_local_ip()
        self.url = f"http://{self.local_ip}:{self.port}/download"
        self.qr_codes_dir = Path("QR-codes")
        self._setup_directories()
        self.qr_code_path = self._generate_qr_filename()

    def _setup_directories(self) -> None:
        """Создает необходимые директории, если они не существуют"""
        self.qr_codes_dir.mkdir(exist_ok=True)

    def _generate_qr_filename(self) -> Path:
        """Генерирует уникальное имя для QR-кода"""
        timestamp = int(time.time())
        random_num = random.randint(1000, 9999)
        return self.qr_codes_dir / f"qr_{timestamp}_{random_num}.png"

    @staticmethod
    def _get_local_ip() -> str:
        """Получает локальный IPv4 адрес компьютера"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"

    def _generate_qr_code(self) -> None:
        """Генерирует QR-код с URL для доступа к файлу"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(str(self.qr_code_path))
        print(f"QR-код сохранен: {self.qr_code_path}")

    def _verify_file_exists(self) -> bool:
        """Проверяет существование JSON-файла"""
        if not self.json_file_path.exists():
            print(f"Ошибка: файл {self.json_file_path} не найден!")
            print(f"Полный путь: {self.json_file_path}")
            return False
        return True

    def _open_qr_code(self) -> None:
        """Надежно открывает QR-код в подходящем приложении"""
        try:
            if platform.system() == 'Windows':
                os.startfile(self.qr_code_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', str(self.qr_code_path)], check=True)
            else:  # Linux и другие UNIX-системы
                try:
                    subprocess.run(['xdg-open', str(self.qr_code_path)], check=True)
                except (FileNotFoundError, subprocess.CalledProcessError):
                    webbrowser.open(f"file://{self.qr_code_path}")
        except Exception as e:
            print(f"Не удалось открыть QR-код: {e}")
            print(f"Вы можете открыть файл вручную: {self.qr_code_path}")

    def _start_http_server(self) -> None:
        """Запускает HTTP сервер с обработчиком скачивания"""
        server_dir = self.json_file_path.parent
        os.chdir(str(server_dir))
        
        print(f"\nСервер запущен на {self.local_ip}:{self.port}")
        print(f"Для скачивания файла откройте: {self.url}")
        print("Нажмите Ctrl+C для остановки...")
        
        # Убедимся, что передаётся полный путь к файлу
        handler_class = lambda *args: DownloadHandler(
            *args, 
            json_file_path=self.json_file_path.name  # Только имя файла (т.к. мы уже перешли в нужную директорию)
        )
        server = HTTPServer(('0.0.0.0', self.port), handler_class)
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен")
        except Exception as e:
            print(f"Ошибка сервера: {e}")

    def run(self) -> None:
        """Основной метод для запуска сервера"""
        if not self._verify_file_exists():
            return

        self._generate_qr_code()
        self._open_qr_code()
        self._start_http_server()

