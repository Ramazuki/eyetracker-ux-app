import httpx
import socket
import threading
import time
import xml.etree.ElementTree as ET
from datetime import datetime
import sys
import csv
import os
import math
from typing import Optional, List, Tuple


class GazepointTracker:
    def __init__(self, host='127.0.0.1', port=4242):
        """
        Инициализация трекера Gazepoint
        :param host: IP адрес сервера Gazepoint (по умолчанию localhost)
        :param port: Порт сервера Gazepoint (по умолчанию 4242)
        """
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.tracking = False
        self.data_thread = None
        self.control_thread = None
        self.stop_flag = threading.Event()
        
        # Данные для CSV
        self.csv_data: List[Tuple[float, float, float, float]] = []
        self.start_time = 0.0
        self.last_time = 0.0
        self.last_x = None
        self.last_y = None
        self.position_threshold = 0.01  # Порог для определения "одинаковых" позиций
        self.current_fixation_start = 0.0
        
        # Файл для сохранения
        self.csv_filename = ""
        
        # Настройки автоматического завершения
        self.max_duration = None  # Максимальная продолжительность в секундах
        self.tracking_start_time = 0.0
        
        # Файл команд для внешнего управления
        self.command_file = "tracker_commands.txt"
        
    def connect(self):
        """Подключение к серверу Gazepoint"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            print(f"✓ Подключено к Gazepoint сервер на {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"✗ Ошибка подключения: {e}")
            return False
    
    def disconnect(self):
        """Отключение от сервера"""
        if self.socket:
            self.socket.close()
            self.connected = False
            print("✓ Отключено от сервера Gazepoint")
    
    def send_command(self, command):
        """Отправка XML команды на сервер"""
        if not self.connected or not self.socket:
            print("✗ Не подключено к серверу")
            return False
        
        try:
            message = f"{command}\r\n"
            self.socket.send(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"✗ Ошибка отправки команды: {e}")
            return False
    
    def receive_data(self):
        """Получение данных от сервера"""
        if not self.connected or not self.socket:
            return None
            
        try:
            # Получаем данные с таймаутом
            self.socket.settimeout(1.0)
            data = self.socket.recv(1024).decode('utf-8')
            return data.strip()
        except socket.timeout:
            return None
        except Exception as e:
            print(f"✗ Ошибка получения данных: {e}")
            return None
    
    def configure_tracker(self):
        """Настройка трекера для получения данных Best POG и времени"""
        print("⚙️ Настройка трекера...")
        
        # Включаем отправку времени
        self.send_command('<SET ID="ENABLE_SEND_TIME" STATE="1" />')
        time.sleep(0.1)
        
        # Включаем счетчик пакетов
        self.send_command('<SET ID="ENABLE_SEND_COUNTER" STATE="1" />')
        time.sleep(0.1)
        
        # Включаем отправку Best POG
        self.send_command('<SET ID="ENABLE_SEND_POG_BEST" STATE="1" />')
        time.sleep(0.1)
        
        print("✓ Трекер настроен")
    
    def start_tracking(self, max_duration_sec=None):
        """
        Начать сбор данных
        :param max_duration_sec: Максимальная продолжительность в секундах (опционально)
        """
        if not self.connected:
            print("✗ Не подключено к серверу")
            return False
        
        # Настраиваем трекер
        self.configure_tracker()
        
        # Устанавливаем ограничение по времени
        self.max_duration = max_duration_sec
        self.tracking_start_time = time.time()
        
        # Создаем файл CSV в папке data/raw
        os.makedirs("data/raw", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_filename = f"data/raw/gaze_data_{timestamp}.csv"
        
        # Инициализируем данные
        self.csv_data = []
        self.start_time = time.time() * 1000  # в миллисекундах
        self.last_time = self.start_time
        self.last_x = None
        self.last_y = None
        
        # Создаем заголовок CSV
        with open(self.csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['x', 'y', 'T', 'Tn'])
        
        # Очищаем файл команд
        with open(self.command_file, 'w') as f:
            f.write("")
        
        # Включаем отправку данных
        success = self.send_command('<SET ID="ENABLE_SEND_DATA" STATE="1" />')
        if success:
            self.tracking = True
            self.stop_flag.clear()
            
            # Запускаем поток для получения данных
            self.data_thread = threading.Thread(target=self._data_loop, daemon=True)
            self.data_thread.start()
            
            # Запускаем поток для контроля команд
            self.control_thread = threading.Thread(target=self._control_loop, daemon=True)
            self.control_thread.start()
            
            print("🎯 Начат сбор данных с айтрекера")
            print(f"📁 Данные сохраняются в файл: {self.csv_filename}")
            
            if max_duration_sec:
                print(f"⏰ Автоматическое завершение через {max_duration_sec} секунд")
            
            print("💡 Способы завершения:")
            print("   1. Подождите автоматического завершения (если установлено)")
            print(f"   2. Создайте файл '{self.command_file}' с командой 'finish'")
            print("   3. Запустите 'python control_tracker.py finish' в другой консоли")
            print("   4. Ctrl+C для принудительного завершения")
            
            return True
        else:
            print("✗ Не удалось начать отслеживание")
            return False
    
    def stop_tracking(self):
        """Остановить сбор данных"""
        if self.tracking:
            # Выключаем отправку данных
            self.send_command('<SET ID="ENABLE_SEND_DATA" STATE="0" />')
            self.tracking = False
            self.stop_flag.set()
            
            # Сохраняем последнюю фиксацию если есть
            if self.last_x is not None and self.last_y is not None:
                current_time_ms = time.time() * 1000
                T = current_time_ms - self.start_time
                Tn = current_time_ms - self.last_time
                self.csv_data.append((self.last_x, self.last_y, T, Tn))
            
            # Сохраняем данные в CSV
            self._save_csv_data()
            
            print("⏹️ Сбор данных остановлен")
            print(f"📊 Сохранено {len(self.csv_data)} записей в {self.csv_filename}")
            return True
        return False
    
    def _save_csv_data(self):
        """Сохранение накопленных данных в CSV"""
        if self.csv_data and self.csv_filename:
            with open(self.csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['x', 'y', 'T', 'Tn'])
                writer.writerows(self.csv_data)
    
    def _is_same_position(self, x1, y1, x2, y2):
        """Проверяет, находятся ли две точки в одной позиции (в пределах порога)"""
        if x2 is None or y2 is None:
            return False
        distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return distance < self.position_threshold
    
    def _control_loop(self):
        """Цикл контроля команд и автоматического завершения"""
        while self.tracking and not self.stop_flag.is_set():
            try:
                # Проверяем автоматическое завершение по времени
                if self.max_duration:
                    elapsed = time.time() - self.tracking_start_time
                    if elapsed >= self.max_duration:
                        print(f"\n⏰ Автоматическое завершение через {self.max_duration} секунд")
                        self.stop_tracking()
                        break
                
                # Проверяем файл команд
                if os.path.exists(self.command_file):
                    try:
                        with open(self.command_file, 'r') as f:
                            command = f.read().strip().lower()
                        
                        if command == 'finish' or command == 'stop':
                            print(f"\n📄 Получена команда '{command}' из файла")
                            self.stop_tracking()
                            # Очищаем файл команд
                            os.remove(self.command_file)
                            break
                        elif command == 'status':
                            elapsed = time.time() - self.tracking_start_time
                            print(f"\n🔄 Статус: собрано {len(self.csv_data)} записей, прошло {elapsed:.1f} сек")
                            # Очищаем команду
                            with open(self.command_file, 'w') as f:
                                f.write("")
                    except Exception:
                        pass
                
                time.sleep(0.5)  # Проверяем каждые 0.5 секунды
                
            except Exception:
                break
    
    def _data_loop(self):
        """Основной цикл получения данных"""
        while self.tracking and self.connected and not self.stop_flag.is_set():
            data = self.receive_data()
            if data:
                self._parse_and_display_data(data)
    
    def _parse_and_display_data(self, data):
        """Парсинг и отображение XML данных"""
        try:
            # Ищем REC теги в данных
            if '<REC' in data and '/>' in data:
                # Разбираем каждый REC тег отдельно
                lines = data.split('\r\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('<REC') and line.endswith('/>'):
                        self._parse_rec_data(line)
        except Exception as e:
            # Игнорируем ошибки парсинга, чтобы не засорять вывод
            pass
    
    def _parse_rec_data(self, rec_line):
        """Парсинг отдельной записи REC"""
        try:
            # Парсим XML
            root = ET.fromstring(rec_line)
            
            # Извлекаем атрибуты
            time_val = root.get('TIME')
            bpogx = root.get('BPOGX')
            bpogy = root.get('BPOGY')
            bpogv = root.get('BPOGV')
            
            # Отображаем только если есть данные Best POG
            if time_val and bpogx and bpogy and bpogv:
                current_x = float(bpogx)
                current_y = float(bpogy)
                is_valid = bpogv == "1"
                
                # Показываем только валидные данные
                if is_valid and current_x > 0 and current_y > 0:
                    current_time_ms = time.time() * 1000
                    T = current_time_ms - self.start_time
                    
                    # Проверяем, изменилась ли позиция
                    if not self._is_same_position(current_x, current_y, self.last_x, self.last_y):
                        # Новая позиция - сохраняем предыдущую фиксацию (если была)
                        if self.last_x is not None and self.last_y is not None:
                            # Время фиксации в предыдущей позиции
                            Tn = current_time_ms - self.last_time
                            
                            # Добавляем запись в CSV
                            self.csv_data.append((self.last_x, self.last_y, T, Tn))
                            
                            # Выводим в консоль
                            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                            elapsed = time.time() - self.tracking_start_time
                            print(f"[{timestamp}] POG: ({self.last_x:.4f}, {self.last_y:.4f}) T={T:.0f}ms Tn={Tn:.0f}ms | Записей: {len(self.csv_data)} | Время: {elapsed:.1f}с")
                            
                            self.last_time = current_time_ms
                        
                        # Начинаем новую фиксацию
                        self.last_x = current_x
                        self.last_y = current_y
                        self.current_fixation_start = current_time_ms
                    
                    # Если позиция та же, просто продолжаем фиксацию (не создаем запись)
                    
        except Exception as e:
            # Игнорируем ошибки парсинга отдельных записей
            pass
    
    def run_with_commands(self):
        """Запуск трекера с обработкой команд"""
        print("Управление:")
        print("- Введите 'start' для начала сбора данных")
        print("- Введите 'start 10' для сбора данных на 10 секунд")
        print("- Введите 'quit' для выхода из программы")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                
                if command.startswith('start'):
                    if not self.tracking:
                        # Проверяем, есть ли указание времени
                        parts = command.split()
                        duration = None
                        if len(parts) > 1:
                            try:
                                duration = int(parts[1])
                            except ValueError:
                                print("❌ Неверный формат времени. Используйте: start 10")
                                continue
                        
                        if self.start_tracking(duration):
                            # Ждем завершения трекинга
                            try:
                                while self.tracking:
                                    time.sleep(1)
                            except KeyboardInterrupt:
                                print("\n🛑 Принудительное завершение...")
                                self.stop_tracking()
                    else:
                        print("Сбор данных уже активен")
                
                elif command == 'quit' or command == 'exit':
                    break
                
                elif command == 'help' or command == '?':
                    print("Доступные команды:")
                    print("  start     - начать сбор данных")
                    print("  start N   - начать сбор на N секунд")
                    print("  quit      - выйти из программы")
                
                elif command != '':
                    print(f"Неизвестная команда: '{command}'. Введите 'help' для справки")
                    
            except (EOFError, KeyboardInterrupt):
                break


def main():
    """Основная функция программы"""
    print("🎯 Gazepoint Eye Tracker v2.0 - Сбор данных Best POG")
    print("=" * 60)
    
    # Создаем трекер
    tracker = GazepointTracker()
    
    # Подключаемся
    if not tracker.connect():
        print("Не удалось подключиться к серверу Gazepoint")
        print("Убедитесь, что:")
        print("1. Gazepoint Control запущен")
        print("2. Айтрекер подключен")
        print(f"3. Сервер работает на {tracker.host}:{tracker.port}")
        return
    
    try:
        # Запускаем трекер с командами
        tracker.run_with_commands()
    
    finally:
        # Останавливаем трекинг и отключаемся
        if tracker.tracking:
            tracker.stop_tracking()
        tracker.disconnect()
        print("\n👋 Программа завершена")


if __name__ == "__main__":
    main() 