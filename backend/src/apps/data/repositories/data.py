from typing import Protocol, Optional, List
import os
import asyncio
import csv
import statistics
from pathlib import Path
from fastapi import UploadFile, HTTPException
from ..schemas.data import DataFileSchema, FileType, HeatmapStatsSchema, HeatmapFirstStatsSchema, HeatmapLongStatsSchema, HeatmapPointSchema, FileListSchema
from datetime import datetime

class DataRepositoryProtocol(Protocol):
    async def save_data_file(self, file: UploadFile, test_token: str, stage_id: int, test_name: str) -> DataFileSchema:
        """Сохраняет файл данных в структурированную папку"""
        ...
    
    async def get_file_info(self, test_token: str, stage_id: int) -> Optional[DataFileSchema]:
        """Получает информацию о файле"""
        ...
    
    async def file_exists(self, test_token: str, stage_id: int) -> bool:
        """Проверяет существование файла"""
        ...
    
    async def get_files_list(self, test_token: str, file_type: Optional[FileType] = None, stage_id: Optional[int] = None) -> FileListSchema:
        """Получает список файлов с фильтрацией"""
        ...
    
    async def get_file_content(self, test_token: str, stage_id: int, file_type: FileType) -> bytes:
        """Получает содержимое файла"""
        ...
    
    async def get_heatmap_stats(self, test_token: str, stage_id: int) -> HeatmapStatsSchema:
        """Вычисляет агрегированную статистику по тепловой карте"""
        ...
    
    async def get_heatmap_first_stats(self, test_token: str, stage_id: int) -> HeatmapFirstStatsSchema:
        """Вычисляет статистику по времени до первой фиксации"""
        ...
    
    async def get_heatmap_long_stats(self, test_token: str, stage_id: int) -> HeatmapLongStatsSchema:
        """Вычисляет статистику по длительности фиксаций"""
        ...

class DataRepositoryImpl:
    def __init__(self, base_data_dir: str = "data"):
        self.base_data_dir = Path(base_data_dir)
        # Создаем базовую директорию если её нет
        self.base_data_dir.mkdir(exist_ok=True)
    
    def _get_test_directory(self, test_name: str, test_token: str) -> Path:
        """Получает директорию для теста"""
        # Очищаем имя теста для использования в пути
        clean_test_name = "".join(c for c in test_name if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_test_name = clean_test_name.replace(' ', '_')
        
        # Создаем путь: data/[имя теста]_[токен теста]/
        test_dir = self.base_data_dir / f"{clean_test_name}_{test_token[:8]}"
        test_dir.mkdir(exist_ok=True)
        return test_dir
    
    def _get_file_path(self, test_name: str, test_token: str, filename: str) -> Path:
        """Получает полный путь к файлу"""
        test_dir = self._get_test_directory(test_name, test_token)
        return test_dir / filename
    
    async def save_data_file(self, file: UploadFile, test_token: str, stage_id: int, test_name: str) -> DataFileSchema:
        """Сохраняет файл данных в структурированную папку"""
        if not file.filename:
            raise HTTPException(status_code=400, detail="Имя файла не указано")
        
        file_path = self._get_file_path(test_name, test_token, file.filename)
        
        # Читаем и сохраняем файл
        content = await file.read()
        file_size = len(content)
        
        # Записываем файл асинхронно
        await asyncio.to_thread(file_path.write_bytes, content)
        
        return DataFileSchema(
            filename=file_path.name,
            file_path=str(file_path),
            test_token=test_token,
            stage_id=stage_id,
            test_name=test_name,
            upload_time=datetime.now(),
            file_size=file_size
        )
    
    async def get_file_info(self, test_token: str, stage_id: int) -> Optional[DataFileSchema]:
        """Получает информацию о файле (упрощенная версия)"""
        # В реальности здесь был бы поиск в БД по метаданным
        # Пока возвращаем None, так как нет постоянного хранения метаданных
        return None
    
    async def file_exists(self, test_token: str, stage_id: int) -> bool:
        """Проверяет существование файла"""
        # Проверяем все возможные папки с данным токеном
        pattern = f"*_{test_token[:8]}"
        for test_dir in self.base_data_dir.glob(pattern):
            if test_dir.is_dir():
                file_path = test_dir / f"heatmap_{stage_id}.csv"
                if file_path.exists():
                    return True
        return False
    
    async def get_files_list(self, test_token: str, file_type: Optional[FileType] = None, stage_id: Optional[int] = None) -> FileListSchema:
        """Получает список файлов с фильтрацией"""
        files = []
        
        # Ищем директории тестов по токену
        pattern = f"*_{test_token[:8]}"
        for test_dir in self.base_data_dir.glob(pattern):
            if not test_dir.is_dir():
                continue
                
            # Получаем имя теста из названия директории
            test_name = test_dir.name.rsplit('_', 1)[0]
            
            # Ищем файлы в директории
            for file_path in test_dir.glob("*.csv"):
                # Парсим имя файла: heatmap_1.csv, heatmap_first_1.csv, heatmap_long_1.csv, saccades_1.csv
                name_parts = file_path.stem.split('_')
                if len(name_parts) < 2:
                    continue
                
                # Последняя часть всегда stage_id
                stage_str = name_parts[-1]
                try:
                    current_stage_id = int(stage_str)
                except ValueError:
                    continue
                
                # Все части кроме последней составляют тип файла
                current_file_type = '_'.join(name_parts[:-1])
                
                # Применяем фильтры
                if file_type and current_file_type != file_type.value:
                    continue
                if stage_id and current_stage_id != stage_id:
                    continue
                
                # Получаем размер файла
                file_size = file_path.stat().st_size
                upload_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                files.append(DataFileSchema(
                    filename=file_path.name,
                    file_path=str(file_path),
                    test_token=test_token,
                    stage_id=current_stage_id,
                    test_name=test_name,
                    upload_time=upload_time,
                    file_size=file_size
                ))
        
        return FileListSchema(
            files=files,
            total_count=len(files)
        )
    
    async def get_file_content(self, test_token: str, stage_id: int, file_type: FileType) -> bytes:
        """Получает содержимое файла"""
        # Ищем файл
        pattern = f"*_{test_token[:8]}"
        for test_dir in self.base_data_dir.glob(pattern):
            if test_dir.is_dir():
                file_path = test_dir / f"{file_type.value}_{stage_id}.csv"
                if file_path.exists():
                    return await asyncio.to_thread(file_path.read_bytes)
                
                # Также проверим .png файлы
                png_path = test_dir / f"{file_type.value}_{stage_id}.png"
                if png_path.exists():
                    return await asyncio.to_thread(png_path.read_bytes)
        
        raise HTTPException(status_code=404, detail=f"Файл {file_type.value}_{stage_id} не найден")
    
    async def get_heatmap_stats(self, test_token: str, stage_id: int) -> HeatmapStatsSchema:
        """Вычисляет агрегированную статистику по тепловой карте"""
        # Получаем содержимое CSV файла
        try:
            csv_content = await self.get_file_content(test_token, stage_id, FileType.HEATMAP)
        except HTTPException:
            raise HTTPException(status_code=404, detail=f"Файл heatmap_{stage_id}.csv не найден")
        
        # Парсим CSV данные
        csv_text = csv_content.decode('utf-8')
        lines = csv_text.strip().split('\n')
        
        if len(lines) < 2:
            raise HTTPException(status_code=400, detail="CSV файл пустой или некорректный")
        
        # Пропускаем заголовок и парсим данные
        data_points = []
        max_value = 0
        max_point = None
        
        reader = csv.DictReader(lines)
        for row in reader:
            try:
                x = float(row.get('x', 0))
                y = float(row.get('y', 0))
                # Используем confidence как значение интенсивности
                value = float(row.get('confidence', 0))
                
                point = {'x': x, 'y': y, 'value': value}
                data_points.append(point)
                
                if value > max_value:
                    max_value = value
                    max_point = point
                    
            except (ValueError, KeyError):
                continue
        
        if not data_points or max_point is None:
            raise HTTPException(status_code=400, detail="Нет валидных данных в CSV файле")
        
        # Сортируем по значению для поиска медианной точки
        sorted_points = sorted(data_points, key=lambda p: p['value'])
        median_index = len(sorted_points) // 2
        median_point_data = sorted_points[median_index]
        
        # Среднее значение интенсивности
        mean_value = statistics.mean([p['value'] for p in data_points])
        
        return HeatmapStatsSchema(
            test_token=test_token,
            stage_id=stage_id,
            max_point=HeatmapPointSchema(x=max_point['x'], y=max_point['y'], value=max_point['value']),
            mean_value=mean_value,
            median_point=HeatmapPointSchema(
                x=median_point_data['x'], 
                y=median_point_data['y'], 
                value=median_point_data['value']
            ),
            total_points=len(data_points)
        )
    
    async def get_heatmap_first_stats(self, test_token: str, stage_id: int) -> HeatmapFirstStatsSchema:
        """Вычисляет статистику по времени до первой фиксации"""
        # Получаем содержимое CSV файла
        try:
            csv_content = await self.get_file_content(test_token, stage_id, FileType.HEATMAP_FIRST)
        except HTTPException:
            raise HTTPException(status_code=404, detail=f"Файл heatmap_first_{stage_id}.csv не найден")
        
        # Парсим CSV данные
        csv_text = csv_content.decode('utf-8')
        lines = csv_text.strip().split('\n')
        
        if len(lines) < 2:
            raise HTTPException(status_code=400, detail="CSV файл пустой или некорректный")
        
        # Парсим данные: ожидаем x, y, time_to_first_fixation
        data_points = []
        min_time = float('inf')
        max_time = 0
        fastest_point = None
        slowest_point = None
        
        reader = csv.DictReader(lines)
        for row in reader:
            try:
                x = float(row.get('x', 0))
                y = float(row.get('y', 0))
                time_value = float(row.get('time_to_first_fixation', 0))
                
                point = {'x': x, 'y': y, 'time': time_value}
                data_points.append(point)
                
                if time_value < min_time and time_value > 0:  # Исключаем 0 как отсутствие фиксации
                    min_time = time_value
                    fastest_point = point
                
                if time_value > max_time:
                    max_time = time_value
                    slowest_point = point
                    
            except (ValueError, KeyError):
                continue
        
        if not data_points or fastest_point is None or slowest_point is None:
            raise HTTPException(status_code=400, detail="Нет валидных данных в CSV файле")
        
        # Фильтруем точки с реальными фиксациями (time > 0)
        valid_points = [p for p in data_points if p['time'] > 0]
        
        if not valid_points:
            raise HTTPException(status_code=400, detail="Нет данных о фиксациях")
        
        # Среднее и медианное время
        times = [p['time'] for p in valid_points]
        mean_time = statistics.mean(times)
        median_time = statistics.median(times)
        
        return HeatmapFirstStatsSchema(
            test_token=test_token,
            stage_id=stage_id,
            fastest_point=HeatmapPointSchema(x=fastest_point['x'], y=fastest_point['y'], value=fastest_point['time']),
            slowest_point=HeatmapPointSchema(x=slowest_point['x'], y=slowest_point['y'], value=slowest_point['time']),
            mean_time=mean_time,
            median_time=median_time,
            total_areas=len(data_points)
        )
    
    async def get_heatmap_long_stats(self, test_token: str, stage_id: int) -> HeatmapLongStatsSchema:
        try:
            csv_content = await self.get_file_content(test_token, stage_id, FileType.HEATMAP_LONG)
        except HTTPException:
            raise HTTPException(status_code=404, detail=f"Файл heatmap_long_{stage_id}.csv не найден")
        
        # Парсим CSV данные
        csv_text = csv_content.decode('utf-8')
        lines = csv_text.strip().split('\n')
        
        if len(lines) < 2:
            raise HTTPException(status_code=400, detail="CSV файл пустой или некорректный")
        
        # Парсим данные: ожидаем x, y, fixation_duration
        data_points = []
        min_duration = float('inf')
        max_duration = 0
        shortest_point = None
        longest_point = None
        
        reader = csv.DictReader(lines)
        for row in reader:
            try:
                x = float(row.get('x', 0))
                y = float(row.get('y', 0))
                duration = float(row.get('fixation_duration', 0))
                
                point = {'x': x, 'y': y, 'duration': duration}
                data_points.append(point)
                
                if duration < min_duration and duration > 0:  # Исключаем 0 как отсутствие фиксации
                    min_duration = duration
                    shortest_point = point
                
                if duration > max_duration:
                    max_duration = duration
                    longest_point = point
                    
            except (ValueError, KeyError):
                continue
        
        if not data_points or shortest_point is None or longest_point is None:
            raise HTTPException(status_code=400, detail="Нет валидных данных в CSV файле")
        
        # Фильтруем точки с реальными фиксациями (duration > 0)
        valid_points = [p for p in data_points if p['duration'] > 0]
        
        if not valid_points:
            raise HTTPException(status_code=400, detail="Нет данных о фиксациях")
        
        # Среднее и медианное время
        durations = [p['duration'] for p in valid_points]
        mean_duration = statistics.mean(durations)
        median_duration = statistics.median(durations)
        
        return HeatmapLongStatsSchema(
            test_token=test_token,
            stage_id=stage_id,
            longest_point=HeatmapPointSchema(x=longest_point['x'], y=longest_point['y'], value=longest_point['duration']),
            shortest_point=HeatmapPointSchema(x=shortest_point['x'], y=shortest_point['y'], value=shortest_point['duration']),
            mean_duration=mean_duration,
            median_duration=median_duration,
            total_fixations=len(valid_points)
        )

class DataRepositoryFactoryProtocol(Protocol):
    async def make(self) -> DataRepositoryProtocol:
        ...

class DataRepositoryFactoryImpl:
    async def make(self) -> DataRepositoryProtocol:
        return DataRepositoryImpl() 