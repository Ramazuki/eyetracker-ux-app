from pydantic import BaseModel, Field
from fastapi import UploadFile
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum

class FileUploadSchema(BaseModel):
    """Схема для загрузки файла с метаданными"""
    test_token: str = Field(..., description="Токен теста")
    stage_id: int = Field(..., description="Номер этапа")
    test_name: Optional[str] = Field(None, description="Название теста")
    
class DataFileSchema(BaseModel):
    """Схема информации о сохраненном файле"""
    filename: str = Field(..., description="Имя файла")
    file_path: str = Field(..., description="Путь к файлу")
    test_token: str = Field(..., description="Токен теста")
    stage_id: int = Field(..., description="Номер этапа")
    test_name: str = Field(..., description="Название теста")
    upload_time: datetime = Field(default_factory=datetime.now, description="Время загрузки")
    file_size: int = Field(..., description="Размер файла в байтах")

class FileType(str, Enum):
    """Типы файлов данных"""
    HEATMAP = "heatmap"
    HEATMAP_FIRST = "heatmap_first" 
    HEATMAP_LONG = "heatmap_long"
    SACCADES = "saccades"

class GetFilesQuerySchema(BaseModel):
    """Схема запроса для получения файлов"""
    test_token: str = Field(..., description="Токен теста")
    file_type: Optional[FileType] = Field(None, description="Тип файла")
    stage_id: Optional[int] = Field(None, description="Номер этапа")

class HeatmapPointSchema(BaseModel):
    """Точка на тепловой карте"""
    x: float = Field(..., description="Координата X")
    y: float = Field(..., description="Координата Y")
    value: float = Field(..., description="Значение интенсивности")

class HeatmapStatsSchema(BaseModel):
    """Агрегированная статистика по тепловой карте"""
    test_token: str = Field(..., description="Токен теста")
    stage_id: int = Field(..., description="Номер этапа")
    max_point: HeatmapPointSchema = Field(..., description="Точка с максимальным значением")
    mean_value: float = Field(..., description="Среднее значение интенсивности")
    median_point: HeatmapPointSchema = Field(..., description="Точка с медианным значением")
    total_points: int = Field(..., description="Общее количество точек")

class HeatmapFirstStatsSchema(BaseModel):
    """Статистика по времени до первой фиксации"""
    test_token: str = Field(..., description="Токен теста")
    stage_id: int = Field(..., description="Номер этапа")
    fastest_point: HeatmapPointSchema = Field(..., description="Точка с наименьшим временем до первой фиксации")
    slowest_point: HeatmapPointSchema = Field(..., description="Точка с наибольшим временем до первой фиксации")
    mean_time: float = Field(..., description="Среднее время до первой фиксации (мс)")
    median_time: float = Field(..., description="Медианное время до первой фиксации (мс)")
    total_areas: int = Field(..., description="Общее количество областей")

class HeatmapLongStatsSchema(BaseModel):
    """Статистика по длительности фиксаций"""
    test_token: str = Field(..., description="Токен теста")
    stage_id: int = Field(..., description="Номер этапа")
    longest_point: HeatmapPointSchema = Field(..., description="Точка с наибольшей длительностью фиксации")
    shortest_point: HeatmapPointSchema = Field(..., description="Точка с наименьшей длительностью фиксации")
    mean_duration: float = Field(..., description="Средняя длительность фиксации (мс)")
    median_duration: float = Field(..., description="Медианная длительность фиксации (мс)")
    total_fixations: int = Field(..., description="Общее количество фиксаций")

class FileListSchema(BaseModel):
    """Список файлов"""
    files: List[DataFileSchema] = Field(..., description="Список файлов")
    total_count: int = Field(..., description="Общее количество файлов") 