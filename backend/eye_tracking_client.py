#!/usr/bin/env python3
"""
Клиентское приложение айтрекинга

Логика:
1. Получает токен теста (от фронта или вручную)
2. Слушает команды старт/стоп от сервера по этому токену
3. При получении команды - показывает индикацию
4. При работе - выводит статус раз в секунду
5. При стопе - создает CSV файл и отправляет на сервер
"""
import asyncio
import aiohttp
import csv
import random
import time
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import tempfile

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TrackingSession:
    """Активная сессия трекинга"""
    token: str
    stage_id: int
    start_time: float
    data_points: list
    test_number: Optional[int] = None
    calibration_point: Optional[int] = None

class EyeTrackingClient:
    """Клиентское приложение айтрекинга"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.current_token: Optional[str] = None
        self.active_sessions: Dict[int, TrackingSession] = {}
        self.running = True
        self.last_command_check = 0
        self.processed_stop_commands: set = set()  # Отслеживаем обработанные команды stop
        
    async def start(self):
        """Главный цикл приложения"""
        logger.info("🎯 Eye Tracking Client запущен")
        
        # Получаем токен теста
        await self.get_test_token()
        
        if not self.current_token:
            logger.error("❌ Не удалось получить токен теста. Завершение работы.")
            return
        
        logger.info(f"✅ Работаем с тестом: {self.current_token[:16]}...")
        logger.info("👂 Ожидание команд от сервера...")
        
        # Запускаем основные задачи
        await asyncio.gather(
            self.simulate_eye_tracking(),
            self.listen_for_commands(),
            self.status_reporter()
        )
    
    async def get_test_token(self):
        """Получение токена теста"""
        print("\n🔑 Получение токена теста:")
        print("1. Ввести токен вручную")
        print("2. Создать новый тест")
        
        choice = input("Выберите опцию (1-2): ").strip()
        
        if choice == "1":
            token = input("Введите токен теста: ").strip()
            if await self.validate_token(token):
                self.current_token = token
                logger.info(f"✅ Токен принят: {token[:16]}...")
            else:
                logger.error("❌ Недействительный токен")
        elif choice == "2":
            test_name = input("Введите название теста: ").strip() or "Тест айтрекинга"
            token = await self.create_test(test_name)
            if token:
                self.current_token = token
                logger.info(f"✅ Создан новый тест: {token[:16]}...")
        else:
            logger.error("❌ Неверный выбор")
    
    async def validate_token(self, token: str) -> bool:
        """Проверка валидности токена"""
        return True  # Упрощенная проверка
    
    async def create_test(self, test_name: str) -> Optional[str]:
        """Создание нового теста"""
        url = f"{self.api_base_url}/tracking/test/create"
        data = {"name": test_name}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["token"]
                    else:
                        logger.error(f"Ошибка создания теста: {response.status}")
                        return None
            except Exception as e:
                logger.error(f"Ошибка создания теста: {e}")
                return None
    
    async def simulate_eye_tracking(self):
        """Имитация сбора данных айтрекинга"""
        while self.running:
            await asyncio.sleep(0.1)  # Высокая частота сбора данных
            
            current_time = time.time()
            
            for stage_id, session in self.active_sessions.items():
                # Генерируем случайные данные айтрекинга
                x = random.uniform(0, 1920)  # Координата X на экране
                y = random.uniform(0, 1080)  # Координата Y на экране
                timestamp = current_time - session.start_time
                
                # Добавляем точку данных
                session.data_points.append({
                    'timestamp': timestamp,
                    'x': x,
                    'y': y,
                    'pupil_diameter': random.uniform(2.0, 8.0),
                    'confidence': random.uniform(0.8, 1.0)
                })
    
    async def listen_for_commands(self):
        """Прослушивание команд от сервера"""
        if not self.current_token:
            return
        
        while self.running:
            await asyncio.sleep(2)  # Проверяем каждые 2 секунды
            
            # Получаем команды от сервера
            try:
                commands = await self.fetch_commands()
                if commands:
                    await self.process_commands(commands)
            except Exception as e:
                logger.error(f"Ошибка получения команд: {e}")
    
    async def fetch_commands(self) -> list:
        """Получение команд от API сервера"""
        if not self.current_token:
            return []
            
        url = f"{self.api_base_url}/tracking/test/{self.current_token}/commands"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return []
            except Exception as e:
                logger.error(f"Ошибка запроса команд: {e}")
                return []
    
    async def process_commands(self, commands: list):
        """Обработка полученных команд"""
        for command in commands:
            stage_id = command.get("stage_id")
            command_type = command.get("command")
            status = command.get("status")
            
            if command_type == "start" and status == "started":
                if stage_id not in self.active_sessions:
                    await self.handle_start_command(command)
            elif command_type == "stop" and status == "stopped":
                # Проверяем что команда stop еще не была обработана
                if stage_id in self.active_sessions and stage_id not in self.processed_stop_commands:
                    await self.handle_stop_command(stage_id)
                    self.processed_stop_commands.add(stage_id)
    
    async def handle_start_command(self, command: dict):
        """Обработка команды старт"""
        if not self.current_token:
            return
            
        stage_id = command.get("stage_id")
        if not isinstance(stage_id, int):
            logger.error(f"Неверный stage_id: {stage_id}")
            return
            
        test_number = command.get("test_number")
        calibration_point = command.get("calibration_point")
        
        logger.info(f"📨 ПОЛУЧЕНА КОМАНДА: START #{stage_id}")
        
        # Начинаем локальную сессию
        session = TrackingSession(
            token=self.current_token,
            stage_id=stage_id,
            start_time=time.time(),
            data_points=[],
            test_number=test_number,
            calibration_point=calibration_point
        )
        self.active_sessions[stage_id] = session
        logger.info(f"🚀 ЗАПУЩЕН этап #{stage_id} (тест:{test_number}, калибровка:{calibration_point})")
    
    async def handle_stop_command(self, stage_id: int):
        """Обработка команды стоп"""
        if not self.current_token:
            return
            
        logger.info(f"📨 ПОЛУЧЕНА КОМАНДА: STOP #{stage_id}")
        
        if stage_id in self.active_sessions:
            # Сохраняем и отправляем данные
            await self.save_and_upload_data(stage_id)
            
            # Удаляем сессию
            del self.active_sessions[stage_id]
            logger.info(f"🛑 ОСТАНОВЛЕН этап #{stage_id}")
    

    
    async def status_reporter(self):
        """Периодический вывод статуса работы"""
        while self.running:
            await asyncio.sleep(1)  # Каждую секунду
            
            if self.active_sessions:
                active_stages = list(self.active_sessions.keys())
                points_count = sum(len(s.data_points) for s in self.active_sessions.values())
                logger.info(f"⚡ АКТИВНЫЕ ЭТАПЫ: {active_stages} | Собрано точек: {points_count}")
            # Убрал спам "ожидание команд" - выводится только при активных этапах
    
    async def save_and_upload_data(self, stage_id: int):
        """Сохранение и загрузка данных этапа"""
        if stage_id not in self.active_sessions:
            logger.error(f"❌ Сессия {stage_id} не найдена")
            return
            
        session = self.active_sessions[stage_id]
        
        # Создаем основной файл тепловой карты
        await self.create_heatmap_file(session, stage_id)
        
        # Создаем файл времени до первой фиксации
        await self.create_heatmap_first_file(session, stage_id)
        
        # Создаем файл длительности фиксаций
        await self.create_heatmap_long_file(session, stage_id)
    
    async def create_heatmap_file(self, session: TrackingSession, stage_id: int):
        """Создание основного файла тепловой карты"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            
            # Записываем CSV данные для основной тепловой карты
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'x', 'y', 'pupil_diameter', 'confidence'])
            
            for point in session.data_points:
                writer.writerow([
                    f"{point['timestamp']:.3f}",
                    f"{point['x']:.1f}",
                    f"{point['y']:.1f}",
                    f"{point['pupil_diameter']:.2f}",
                    f"{point['confidence']:.3f}"
                ])
        
        filename = f"heatmap_{stage_id}.csv"
        logger.info(f"💾 Сохранен файл: {filename} ({len(session.data_points)} точек)")
        
        await self.upload_data_file(temp_path, filename, session.token, stage_id)
        Path(temp_path).unlink()
    
    async def create_heatmap_first_file(self, session: TrackingSession, stage_id: int):
        """Создание файла времени до первой фиксации"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            
            # Симулируем данные времени до первой фиксации
            # Разбиваем экран на сетку и для каждой области вычисляем время до первой фиксации
            writer = csv.writer(f)
            writer.writerow(['x', 'y', 'time_to_first_fixation'])
            
            # Создаем сетку 20x15 для анализа
            for grid_x in range(0, 1920, 96):  # 20 областей по горизонтали
                for grid_y in range(0, 1080, 72):  # 15 областей по вертикали
                    # Находим первую точку в этой области
                    first_fixation_time = None
                    area_center_x = grid_x + 48
                    area_center_y = grid_y + 36
                    
                    for point in session.data_points:
                        if (grid_x <= point['x'] < grid_x + 96 and 
                            grid_y <= point['y'] < grid_y + 72 and
                            point['confidence'] > 0.7):  # Только уверенные фиксации
                            time_from_start = (point['timestamp'] - session.start_time) * 1000  # в миллисекундах
                            if first_fixation_time is None or time_from_start < first_fixation_time:
                                first_fixation_time = time_from_start
                    
                    # Записываем результат (0 если фиксации не было)
                    writer.writerow([
                        area_center_x,
                        area_center_y,
                        f"{first_fixation_time:.1f}" if first_fixation_time else "0"
                    ])
        
        filename = f"heatmap_first_{stage_id}.csv"
        logger.info(f"💾 Сохранен файл: {filename} (время до первой фиксации)")
        
        await self.upload_data_file(temp_path, filename, session.token, stage_id)
        Path(temp_path).unlink()
    
    async def create_heatmap_long_file(self, session: TrackingSession, stage_id: int):
        """Создание файла длительности фиксаций"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            
            # Симулируем данные длительности фиксаций
            writer = csv.writer(f)
            writer.writerow(['x', 'y', 'fixation_duration'])
            
            # Группируем соседние точки в фиксации и вычисляем их длительность
            fixations = []
            current_fixation = None
            
            for point in session.data_points:
                if point['confidence'] < 0.7:  # Пропускаем неуверенные точки
                    continue
                    
                if current_fixation is None:
                    current_fixation = {
                        'x': point['x'],
                        'y': point['y'],
                        'start_time': point['timestamp'],
                        'end_time': point['timestamp'],
                        'points': [point]
                    }
                else:
                    # Проверяем, близко ли к текущей фиксации
                    distance = ((point['x'] - current_fixation['x'])**2 + 
                               (point['y'] - current_fixation['y'])**2)**0.5
                    
                    if distance < 50:  # Радиус фиксации 50 пикселей
                        current_fixation['end_time'] = point['timestamp']
                        current_fixation['points'].append(point)
                        # Обновляем центр фиксации
                        current_fixation['x'] = sum(p['x'] for p in current_fixation['points']) / len(current_fixation['points'])
                        current_fixation['y'] = sum(p['y'] for p in current_fixation['points']) / len(current_fixation['points'])
                    else:
                        # Сохраняем текущую фиксацию если она достаточно длительная
                        duration = (current_fixation['end_time'] - current_fixation['start_time']) * 1000
                        if duration >= 100:  # Минимум 100 мс
                            fixations.append({
                                'x': current_fixation['x'],
                                'y': current_fixation['y'],
                                'duration': duration
                            })
                        
                        # Начинаем новую фиксацию
                        current_fixation = {
                            'x': point['x'],
                            'y': point['y'],
                            'start_time': point['timestamp'],
                            'end_time': point['timestamp'],
                            'points': [point]
                        }
            
            # Добавляем последнюю фиксацию
            if current_fixation:
                duration = (current_fixation['end_time'] - current_fixation['start_time']) * 1000
                if duration >= 100:
                    fixations.append({
                        'x': current_fixation['x'],
                        'y': current_fixation['y'],
                        'duration': duration
                    })
            
            # Записываем фиксации
            for fixation in fixations:
                writer.writerow([
                    f"{fixation['x']:.1f}",
                    f"{fixation['y']:.1f}",
                    f"{fixation['duration']:.1f}"
                ])
        
        filename = f"heatmap_long_{stage_id}.csv"
        logger.info(f"💾 Сохранен файл: {filename} ({len(fixations)} фиксаций)")
        
        await self.upload_data_file(temp_path, filename, session.token, stage_id)
        Path(temp_path).unlink()
    
    async def upload_data_file(self, file_path: str, filename: str, token: str, stage_id: int):
        """Загрузка файла данных на сервер"""
        url = f"{self.api_base_url}/data/upload"
        
        async with aiohttp.ClientSession() as session:
            try:
                # Подготавливаем форму
                data = aiohttp.FormData()
                data.add_field('test_token', token)
                data.add_field('stage_id', str(stage_id))
                
                # Добавляем файл
                with open(file_path, 'rb') as f:
                    data.add_field('file', f, filename=filename, content_type='text/csv')
                    
                    async with session.post(url, data=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            logger.info(f"📤 Файл загружен: {result.get('file_path', filename)}")
                        else:
                            error_text = await response.text()
                            logger.error(f"Ошибка загрузки файла {response.status}: {error_text}")
                            
            except Exception as e:
                logger.error(f"Ошибка загрузки файла: {e}")
    
    async def send_start_command(self, token: str, test_number: Optional[int], 
                               calibration_point: Optional[int]) -> Optional[dict]:
        """Отправка команды старт"""
        url = f"{self.api_base_url}/tracking/test/{token}/start"
        data = {}
        
        if test_number is not None:
            data["test_number"] = test_number
        if calibration_point is not None:
            data["calibration_point"] = calibration_point
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Ошибка команды старт: {response.status}")
                        return None
            except Exception as e:
                logger.error(f"Ошибка команды старт: {e}")
                return None
    
    async def send_stop_command(self, token: str, stage_id: int) -> Optional[dict]:
        """Отправка команды стоп"""
        url = f"{self.api_base_url}/tracking/test/{token}/stop"
        data = {"stage_id": stage_id}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Ошибка команды стоп: {response.status}")
                        return None
            except Exception as e:
                logger.error(f"Ошибка команды стоп: {e}")
                return None
    
    async def shutdown(self):
        """Корректное завершение работы"""
        logger.info("🔄 Завершение работы...")
        self.running = False
        
        # Останавливаем все активные сессии
        if self.current_token:
            for stage_id in list(self.active_sessions.keys()):
                await self.save_and_upload_data(stage_id)
                await self.send_stop_command(self.current_token, stage_id)
        
        logger.info("✅ Работа завершена")

async def main():
    """Точка входа"""
    client = EyeTrackingClient()
    
    try:
        await client.start()
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
        await client.shutdown()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        await client.shutdown()

if __name__ == "__main__":
    asyncio.run(main()) 