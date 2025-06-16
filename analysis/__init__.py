"""
Модуль для анализа данных айтрекинга и построения тепловых карт
"""

from .heatmap_analyzer import create_gaze_heatmap, analyze_all_gaze_files

__all__ = ['create_gaze_heatmap', 'analyze_all_gaze_files'] 