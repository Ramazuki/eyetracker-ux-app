import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import gaussian_kde
import pandas as pd
import os
from datetime import datetime
from scipy.ndimage import gaussian_filter
import glob
from pathlib import Path


def load_gaze_data(csv_filename):
    """
    Returns:
        tuple: (x, y, T, Tn) массивы данных
    """
    try:
        df = pd.read_csv(csv_filename)
        
        if not all(col in df.columns for col in ['x', 'y', 'T', 'Tn']):
            raise ValueError("CSV файл не содержит необходимых колонок: x, y, T, Tn")
        
        x = df['x'].values
        y = df['y'].values  
        T = df['T'].values
        Tn = df['Tn'].values
        
        
        return x, y, T, Tn
        
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        return None, None, None, None


def find_latest_gaze_file():
    gaze_files = glob.glob("data/raw/gaze_data_*.csv")
    if not gaze_files:
        return None
    
    latest_file = max(gaze_files, key=os.path.getctime)
    return latest_file


def setup_theme():
    sns.set_theme(style="white", context="paper")


def extract_boundaries_from_calibration(data_dir="data/raw"):
    """Извлекает границы приложения из файлов калибровки"""
    data_path = Path(data_dir)
    calib_files = [
        "calib1.csv", "calib2.csv", "calib3.csv", "calib4.csv"
    ]
    
    all_x, all_y = [], []
    
    for file in calib_files:
        file_path = data_path / file
        if file_path.exists():
            df = pd.read_csv(file_path)
            all_x.extend(df['x'].tolist())
            all_y.extend(df['y'].tolist())
            print(f"✅ Обработан файл калибровки: {file}")
        else:
            print(f"⚠️  Файл калибровки не найден: {file}")
    
    if not all_x:
        return None
    
    # Вычисляем границы как min/max значения
    boundaries = {
        'x_min': np.min(all_x),
        'x_max': np.max(all_x),
        'y_min': np.min(all_y),
        'y_max': np.max(all_y)
    }
    
    print(f"📊 Извлечены границы: x=[{boundaries['x_min']:.3f}, {boundaries['x_max']:.3f}], y=[{boundaries['y_min']:.3f}, {boundaries['y_max']:.3f}]")
    return boundaries


def filter_and_normalize_gaze_data(x, y, T, Tn, boundaries):
    """Фильтрует и нормализует данные взгляда по границам калибровки"""
    if boundaries is None:
        print("❌ Границы не определены, используются исходные данные")
        return x, y, T, Tn
    
    # Фильтруем данные по границам
    mask = (
        (x >= boundaries['x_min']) & 
        (x <= boundaries['x_max']) &
        (y >= boundaries['y_min']) & 
        (y <= boundaries['y_max'])
    )
    
    x_filtered = x[mask]
    y_filtered = y[mask]
    T_filtered = T[mask]
    Tn_filtered = Tn[mask]
    
    original_count = len(x)
    filtered_count = len(x_filtered)
    
    print(f"🔍 Фильтрация: {original_count} -> {filtered_count} точек ({(filtered_count/original_count*100):.1f}%)")
    

    x_norm = (x_filtered - boundaries['x_min']) / (boundaries['x_max'] - boundaries['x_min'])
    y_norm = 1.0 - (y_filtered - boundaries['y_min']) / (boundaries['y_max'] - boundaries['y_min'])
    
    
    return x_norm, y_norm, T_filtered, Tn_filtered


def save_heatmap_transparent(fig, filename="heatmap_transparent.png"):
    """Сохраняет тепловую карту с прозрачным фоном"""
    fig.patch.set_alpha(0)  # Прозрачный фон фигуры
    for ax in fig.axes:
        ax.patch.set_alpha(0)  # Прозрачный фон осей
    
    fig.savefig(filename, dpi=300, bbox_inches='tight', 
                facecolor='none', edgecolor='none', transparent=True)
    print(f"💾 Тепловая карта сохранена: {filename}")


def create_clean_heatmap_image(Z_kde, x_range, y_range, filename="heatmap_clean.png"):
    """Создает чистое изображение тепловой карты 16:9 без шкалы и с прозрачными нулевыми областями"""
    
    # Создаем фигуру в точном соотношении 16:9 без осей и отступов
    fig = plt.figure(figsize=(16, 9))
    ax = fig.add_axes((0, 0, 1, 1))  # Заполняем всю фигуру
    ax.set_xlim(x_range[0], x_range[1])
    ax.set_ylim(y_range[0], y_range[1])
    ax.axis('off')  # Убираем все оси и подписи
    
    # Создаем маску для нулевых значений
    Z_masked = np.ma.masked_where(Z_kde == 0, Z_kde)
    
    # Отображаем тепловую карту с прозрачностью для нулевых значений
    im = ax.imshow(Z_masked, extent=(x_range[0], x_range[1], y_range[0], y_range[1]), 
                   origin='lower', cmap='Spectral_r', interpolation='bilinear', 
                   aspect='equal')
    
    # Сохраняем без отступов и с прозрачным фоном
    fig.savefig(filename, dpi=300, bbox_inches='tight', pad_inches=0,
                facecolor='none', edgecolor='none', transparent=True)
    
    plt.close(fig)  # Закрываем фигуру чтобы не отображать
    print(f"💾 Чистое изображение тепловой карты сохранено: {filename}")


def create_clean_heatmap_opencv(Z_kde, x_range, y_range, filename="heatmap_clean_cv.png"):
    """Создает чистое изображение 16:9 и удаляет фиолетовый фон через OpenCV"""
    try:
        import cv2
        
        # Создаем изображение с точным соотношением 16:9
        width, height = 1920, 1080  
        fig = plt.figure(figsize=(width/100, height/100))
        ax = fig.add_axes((0, 0, 1, 1))
        ax.set_xlim(x_range[0], x_range[1])
        ax.set_ylim(y_range[0], y_range[1])
        ax.axis('off')
        
        im = ax.imshow(Z_kde, extent=(x_range[0], x_range[1], y_range[0], y_range[1]), 
                       origin='lower', cmap='Spectral_r', interpolation='bilinear', 
                       aspect='auto')
        
        temp_filename = "temp_heatmap.png"
        fig.savefig(temp_filename, dpi=100, bbox_inches='tight', pad_inches=0,
                    facecolor='black')
        plt.close(fig)
        
        # Загружаем изображение через OpenCV
        img = cv2.imread(temp_filename, cv2.IMREAD_UNCHANGED)
        
        # Проверяем, что изображение загружено
        if img is None:
            print(f"❌ Не удалось загрузить временное изображение: {temp_filename}")
            return
        
        # Конвертируем в HSV для лучшего выделения фиолетового
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Определяем диапазон фиолетового/темно-синего цвета для Spectral_r
        lower_purple = np.array([100, 30, 30])
        upper_purple = np.array([160, 255, 255])
        
        # Создаем маску для фиолетового цвета
        mask = cv2.inRange(hsv, lower_purple, upper_purple)
        
        # Инвертируем маску (делаем фиолетовые области прозрачными)
        mask_inv = cv2.bitwise_not(mask)
        
        # Создаем 4-канальное изображение с альфа-каналом
        img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
        img_rgba[:, :, 3] = mask_inv  # Устанавливаем альфа-канал
        
        # Принудительно изменяем размер к точному 16:9 если нужно
        target_height = 1080
        target_width = 1920
        if img_rgba.shape[:2] != (target_height, target_width):
            img_rgba = cv2.resize(img_rgba, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
        
        # Сохраняем результат
        cv2.imwrite(filename, img_rgba)
        
        # Удаляем временный файл
        os.remove(temp_filename)
        
        print(f"💾 Изображение 16:9 ({target_width}x{target_height}) сохранено: {filename}")
        
    except ImportError:
        print("❌ OpenCV не установлен. Используйте: pip install opencv-python")
    except Exception as e:
        print(f"❌ Ошибка при обработке изображения: {e}")


def save_analysis_files(x, y, T, Tn, X, Y, Z, output_dir="data/analysis"):
    """ 
    Args:
        x, y: координаты точек
        T, Tn: временные ряды
        X, Y: координатные сетки
        Z: матрица плотности KDE
        output_dir: папка для сохранения
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    kde_matrix = pd.DataFrame(Z)
    kde_matrix.to_csv(f"{output_dir}/kde_heatmap_{timestamp}.csv", index=False)
    
    np.savez(f"{output_dir}/coordinate_grids_{timestamp}.npz", X=X, Y=Y)
    
    
    print(f"📁 Результаты анализа сохранены в папку: {output_dir}")
    print(f"   Создано 3 файла с временной меткой: {timestamp}")


def compute_kde(data, x_range, y_range, grid_size=100):
    """
    Вычисляет KDE для координатных данных
    """
    x_grid = np.linspace(x_range[0], x_range[1], grid_size)
    y_grid = np.linspace(y_range[0], y_range[1], grid_size)
    X, Y = np.meshgrid(x_grid, y_grid)
    positions = np.vstack([X.ravel(), Y.ravel()])
    
    kde = gaussian_kde(data, bw_method='scott')
    Z = kde(positions).reshape(grid_size, grid_size)
    
    return X, Y, Z


def plot_scatter_time(x, y, time_values, title_suffix, ax):
    """Создает scatter plot с цветовым кодированием по времени"""
    if title_suffix == 'длительность фиксации':
        cmap = sns.color_palette("Spectral_r", as_cmap=True)
    else:
        cmap = sns.color_palette("Spectral", as_cmap=True)
    
    scatter = ax.scatter(x, y, c=time_values, s=30, alpha=0.7, cmap=cmap)
    plt.colorbar(scatter, ax=ax, label='мс')
    ax.set_title(f'Точки - {title_suffix}', fontsize=14)
    ax.set_xlabel('X координата', fontsize=12)
    ax.set_ylabel('Y координата', fontsize=12)


def plot_contour_time(X, Y, Z, title_suffix, ax):
    """Создает контурный график объединения точек без весов"""
    cmap = sns.color_palette("Spectral_r", as_cmap=True)
    
    contour = ax.contourf(X, Y, Z, levels=15, cmap=cmap, alpha=0.7)
    ax.contour(X, Y, Z, levels=15, colors='black', alpha=0.3, linewidths=0.5)
    plt.colorbar(contour, ax=ax, label='Плотность точек')
    ax.set_title(f'Зоны объединения точек (без весов)', fontsize=14)
    ax.set_xlabel('X координата', fontsize=12)
    ax.set_ylabel('Y координата', fontsize=12)


def create_weighted_kde_heatmap(x, y, weights, x_range, y_range, grid_size=100):
    """
    Создает тепловую карту используя Gaussian KDE с весами
    
    Args:
        x, y: координаты точек
        weights: веса для каждой точки (нормализованы [0;1])
        x_range, y_range: диапазоны осей
        grid_size: размер сетки
    """
    # Создаем сетку
    x_grid = np.linspace(x_range[0], x_range[1], grid_size)
    y_grid = np.linspace(y_range[0], y_range[1], grid_size)
    X, Y = np.meshgrid(x_grid, y_grid)
    positions = np.vstack([X.ravel(), Y.ravel()])
    
    data = np.vstack([x, y])
    
    kde = gaussian_kde(data, weights=weights, bw_method='scott')
    kde.covariance_factor = lambda: 0.5 * kde.scotts_factor()
    kde._compute_covariance()
    
    Z = kde(positions).reshape(grid_size, grid_size)
    
    return X, Y, Z


def create_gaze_heatmap(csv_filename=None, use_calibration=True):
    setup_theme()
    
    if csv_filename is None:
        csv_filename = find_latest_gaze_file()
        if csv_filename is None:
            print("❌ Не найдено файлов с данными трекера (gaze_data_*.csv)")
            print("   Проверьте папки: data/raw/ и корневую папку")
            return
        print(f"📁 Автоматически выбран файл: {csv_filename}")
    
    x, y, T, Tn = load_gaze_data(csv_filename)
    if x is None:
        return
    
    # Извлекаем границы из калибровки и нормализуем данные
    if use_calibration:
        boundaries = extract_boundaries_from_calibration()
        x, y, T, Tn = filter_and_normalize_gaze_data(x, y, T, Tn, boundaries)
        # Для нормализованных данных диапазон всегда [0, 1]
        x_range = (0, 1)
        y_range = (0, 1)
    else:
        # Определяем диапазоны с отступом
        x_range = (float(np.min(x)) - 0.05, float(np.max(x)) + 0.05) # type: ignore
        y_range = (float(np.min(y)) - 0.05, float(np.max(y)) + 0.05) # type: ignore
    
    # Нормализуем временные данные в диапазон [0;1]
    T_normalized = (T - np.min(T)) / (np.max(T) - np.min(T)) if len(np.unique(T)) > 1 else np.zeros_like(T) # type: ignore
    Tn_normalized = (Tn - np.min(Tn)) / (np.max(Tn) - np.min(Tn)) if len(np.unique(Tn)) > 1 else np.zeros_like(Tn) # type: ignore
    
    

    data = np.vstack([x, y]) # type: ignore
    X, Y, Z_kde = compute_kde(data, x_range, y_range)
    
    X_time, Y_time, Z_time = create_weighted_kde_heatmap(x, y, 1.0 - T_normalized, x_range, y_range)  # Инвертируем T
    X_duration, Y_duration, Z_duration = create_weighted_kde_heatmap(x, y, Tn_normalized, x_range, y_range)
    
    fig1, axes1 = plt.subplots(1, 3, figsize=(18, 6))
    fig1.suptitle('Анализ времени до первой фиксации (T)\nКрасный = раннее внимание, Синий = позднее внимание', 
                  fontsize=16, fontweight='bold')
    
    plot_scatter_time(x, y, T, 'время до первой фиксации', axes1[0])
    axes1[0].set_xlim(0, 1)
    axes1[0].set_ylim(0, 1)
    
    im1 = axes1[1].imshow(Z_time, extent=[x_range[0], x_range[1], y_range[0], y_range[1]], 
                         origin='lower', cmap='Spectral_r', alpha=0.8)
    #axes1[1].scatter(x, y, s=10, c='black', alpha=0.3)
    plt.colorbar(im1, ax=axes1[1], label='Плотность (раннее внимание)')
    axes1[1].set_title('Тепловая карта - раннее внимание', fontsize=14)
    axes1[1].set_xlabel('X координата', fontsize=12)
    axes1[1].set_ylabel('Y координата', fontsize=12)
    
    plot_contour_time(X, Y, Z_kde, 'зоны раннего внимания', axes1[2])
    
    plt.tight_layout()
    
    # === ВТОРОЕ ОКНО: Анализ длительности фиксаций (Tn) ===
    fig2, axes2 = plt.subplots(1, 3, figsize=(18, 6))
    fig2.suptitle('Анализ длительности фиксаций (Tn)\nКрасный = длительные фиксации, Синий = короткие фиксации', 
                  fontsize=16, fontweight='bold')
    
    plot_scatter_time(x, y, Tn, 'длительность фиксации', axes2[0])
    axes2[0].set_xlim(0, 1)
    axes2[0].set_ylim(0, 1)
    
    im2 = axes2[1].imshow(Z_duration, extent=[x_range[0], x_range[1], y_range[0], y_range[1]], 
                         origin='lower', cmap='Spectral_r', alpha=0.8)
    #axes2[1].scatter(x, y, s=10, c='black', alpha=0.3)
    plt.colorbar(im2, ax=axes2[1], label='Плотность (длительные фиксации)')
    axes2[1].set_title('Тепловая карта - длительность фиксаций', fontsize=14)
    axes2[1].set_xlabel('X координата', fontsize=12)
    axes2[1].set_ylabel('Y координата', fontsize=12)
    
    plot_contour_time(X, Y, Z_kde, 'зоны длительных фиксаций', axes2[2])
    
    plt.tight_layout()
    
    # Создаем дополнительную простую тепловую карту для сохранения без фона
    fig_simple = plt.figure(figsize=(16, 9))
    plt.imshow(Z_kde, extent=(x_range[0], x_range[1], y_range[0], y_range[1]), 
               origin='lower', cmap='Spectral_r', alpha=0.8, interpolation='bilinear')
    plt.colorbar(label='Плотность взглядов')
    plt.title('Нормализованная тепловая карта взглядов', fontsize=16, fontweight='bold')
    if use_calibration:
        plt.xlabel('X (нормализованная координата)', fontsize=12)
        plt.ylabel('Y (нормализованная координата)', fontsize=12)
    else:
        plt.xlabel('X координата', fontsize=12)
        plt.ylabel('Y координата', fontsize=12)
    plt.tight_layout()
    
    # Извлекаем название теста из имени файла
    import re
    test_name = "unknown"
    if csv_filename:
        match = re.search(r'gaze_data_(.+?)\.csv', csv_filename)
        if match:
            test_name = match.group(1)
    
    # Создаем только OpenCV версию с названием теста
    output_filename = f"{test_name}.png"
    create_clean_heatmap_opencv(Z_kde, x_range, y_range, output_filename)
    
    save_analysis_files(x, y, T, Tn, X, Y, Z_kde)
    
    plt.show()
    
    print("✅ Анализ завершен!")
    print(f"📊 Проанализировано {len(x)} точек фиксации")


def analyze_all_gaze_files():
    """Анализирует все найденные файлы с данными трекера"""
    # Ищем файлы в обеих локациях
    gaze_files = glob.glob("data/raw/gaze_data_*.csv") + glob.glob("gaze_data_*.csv")
    
    if not gaze_files:
        print("❌ Не найдено файлов с данными трекера")
        print("   Проверьте папки: data/raw/ и корневую папку")
        return
    
    print(f"🔍 Найдено {len(gaze_files)} файлов с данными:")
    for i, file in enumerate(gaze_files, 1):
        file_time = datetime.fromtimestamp(os.path.getctime(file))
        print(f"   {i}. {file} (создан: {file_time.strftime('%Y-%m-%d %H:%M:%S')})")
    
    choice = input(f"\nВыберите файл для анализа (1-{len(gaze_files)}) или нажмите Enter для последнего: ").strip()
    
    if choice == "":
        # Берем последний файл
        selected_file = max(gaze_files, key=os.path.getctime)
    else:
        try:
            index = int(choice) - 1
            if 0 <= index < len(gaze_files):
                selected_file = gaze_files[index]
            else:
                print("❌ Неверный номер файла")
                return
        except ValueError:
            print("❌ Неверный ввод")
            return
    
    print(f"📁 Выбран файл: {selected_file}")
    create_gaze_heatmap(selected_file)


def main():
    """Функция main для запуска анализатора"""
    print("🎯 Анализатор тепловых карт")
    print("=" * 50)
    
    # Проверяем наличие файлов с данными
    gaze_files = glob.glob("data/raw/gaze_data_*.csv") + glob.glob("gaze_data_*.csv")
    
    if not gaze_files:
        print("❌ Не найдено файлов с данными трекера (gaze_data_*.csv)")
        print("   Сначала запустите трекер и соберите данные")
        print("   Или создайте тестовые данные с помощью генератора")
    elif len(gaze_files) == 1:
        print(f"📁 Найден 1 файл с данными: {gaze_files[0]}")
        create_gaze_heatmap(gaze_files[0])
    else:
        analyze_all_gaze_files()


if __name__ == "__main__":
    main() 