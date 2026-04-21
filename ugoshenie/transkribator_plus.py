#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎙️ Whisper Audio Transcription Tool
Умный инструмент для распознавания аудио с красивым интерфейсом
"""

import os
import sys
import json
import subprocess
from datetime import datetime
import time
import itertools
import threading
import warnings

# Подавляем конкретное предупреждение о FP16
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

# Цвета для красивого вывода (работает в Windows 10/11)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Анимация загрузки
class Spinner:
    def __init__(self, message="⏳ Обработка", delay=0.1):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.delay = delay
        self.message = message
        self.running = False
        self.thread = None
        self.start_time = None

    def spin(self):
        while self.running:
            elapsed = time.time() - self.start_time if self.start_time else 0
            elapsed_str = f" [{elapsed:.1f}с]" if elapsed > 0 else ""
            sys.stdout.write(f"\r{Colors.CYAN}{next(self.spinner)} {self.message}{elapsed_str}{Colors.ENDC}")
            sys.stdout.flush()
            time.sleep(self.delay)
            # Стираем предыдущую строку
            sys.stdout.write('\b' * (len(self.message) + len(elapsed_str) + 3))

    def __enter__(self):
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        if self.thread:
            self.thread.join()
        elapsed = time.time() - self.start_time
        sys.stdout.write(f"\r{Colors.GREEN}✓ {self.message} завершено за {elapsed:.1f}с{Colors.ENDC}\n")
        sys.stdout.flush()

def print_banner():
    """Красивый баннер при запуске"""
    banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════╗
║                                                              ║
║   {Colors.BOLD}🎙️  WHISPER AUDIO TRANSCRIPTION TOOL  v3.0{Colors.CYAN}               ║
║   {Colors.BOLD}Распознавание речи с помощью OpenAI Whisper{Colors.CYAN}               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}
    """
    print(banner)

def print_step(message, status="pending"):
    """Вывод шага с статусом"""
    symbols = {
        "pending": f"{Colors.BLUE}⏳{Colors.ENDC}",
        "success": f"{Colors.GREEN}✅{Colors.ENDC}",
        "error": f"{Colors.FAIL}❌{Colors.ENDC}",
        "warning": f"{Colors.WARNING}⚠️{Colors.ENDC}",
        "info": f"{Colors.CYAN}ℹ️{Colors.ENDC}"
    }
    print(f"{symbols.get(status, '•')} {message}")

def format_time(seconds):
    """Форматирование времени в читаемый вид"""
    if seconds < 60:
        return f"{seconds:.1f} сек"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{int(minutes)} мин {secs:.1f} сек"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{int(hours)} ч {int(minutes)} мин {secs:.1f} сек"

def check_whisper_installed():
    """Проверка установки whisper"""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import whisper
        print_step("Whisper установлен", "success")
        return True, whisper
    except ImportError:
        print_step("Whisper не установлен", "error")
        return False, None

def check_ffmpeg_installed():
    """Проверка установки ffmpeg"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True,
                              creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print_step(f"FFmpeg установлен: {version[:50]}...", "success")
            
            # Автоматически добавляем ffmpeg в PATH для текущей сессии
            ffmpeg_path = shutil_which('ffmpeg')
            if ffmpeg_path:
                ffmpeg_dir = os.path.dirname(ffmpeg_path)
                os.environ['PATH'] += os.pathsep + ffmpeg_dir
            
            return True
        else:
            print_step("FFmpeg не найден в PATH", "error")
            return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_step("FFmpeg не найден", "error")
        return False

def shutil_which(cmd):
    """Альтернатива shutil.which для совместимости"""
    return next((os.path.join(path, cmd + ('.exe' if sys.platform == "win32" else '')) 
                for path in os.environ["PATH"].split(os.pathsep) 
                if os.path.exists(os.path.join(path, cmd + ('.exe' if sys.platform == "win32" else '')))), None)

def print_installation_instructions():
    """Вывод инструкций по установке"""
    instructions = f"""
{Colors.WARNING}╔══════════════════════════════════════════════════════════╗
║           ИНСТРУКЦИИ ПО УСТАНОВКЕ                      ║
╚══════════════════════════════════════════════════════════╝{Colors.ENDC}

{Colors.BOLD}1. Установка Whisper:{Colors.ENDC}
   {Colors.CYAN}pip install -U openai-whisper{Colors.ENDC}

{Colors.BOLD}2. Установка FFmpeg (Windows 10/11):{Colors.ENDC}
   {Colors.CYAN}winget install ffmpeg{Colors.ENDC}
   
   Или вручную:
   • Скачайте с: https://www.gyan.dev/ffmpeg/builds/
   • Распакуйте в C:\\ffmpeg
   • Добавьте C:\\ffmpeg\\bin в PATH

{Colors.BOLD}3. Установка дополнительных зависимостей:{Colors.ENDC}
   {Colors.CYAN}pip install torch torchaudio torchvision{Colors.ENDC}

{Colors.GREEN}После установки перезапустите программу.{Colors.ENDC}
    """
    print(instructions)

def check_dependencies():
    """Полная проверка зависимостей"""
    print_step("Проверка зависимостей...", "info")
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        
        whisper_ok, whisper_module = check_whisper_installed()
        ffmpeg_ok = check_ffmpeg_installed()
        
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                print_step(f"PyTorch установлен (GPU доступен: {torch.cuda.get_device_name(0)})", "success")
            else:
                print_step("PyTorch установлен (режим CPU)", "info")
        except ImportError:
            print_step("PyTorch не установлен", "warning")
    
    return whisper_ok and ffmpeg_ok, whisper_module if whisper_ok else None

def get_audio_path():
    """Функция для получения пути к аудиофайлу"""
    
    print(f"\n{Colors.BOLD}📂 ВЫБОР АУДИОФАЙЛА{Colors.ENDC}")
    print("─" * 50)
    
    if len(sys.argv) > 1:
        audio_path = sys.argv[1].strip('"').strip("'")
        if os.path.exists(audio_path):
            print_step(f"Аудиофайл из аргумента: {os.path.basename(audio_path)}", "success")
            return audio_path
        else:
            print_step(f"Файл не найден: {audio_path}", "error")
    
    print(f"{Colors.CYAN}📝 Укажите путь к аудиофайлу:{Colors.ENDC}")
    print("   • Можно перетащить файл в окно терминала")
    print("   • Введите 'q' для выхода")
    print("─" * 50)
    
    while True:
        user_input = input(f"{Colors.BOLD}Путь >{Colors.ENDC} ").strip().strip('"').strip("'")
        
        if user_input.lower() == 'q':
            print_step("Выход из программы", "info")
            return None
        
        if os.path.exists(user_input):
            file_size = os.path.getsize(user_input) / (1024 * 1024)
            print_step(f"Файл найден: {os.path.basename(user_input)} ({file_size:.1f} MB)", "success")
            return user_input
        else:
            print_step(f"Файл не найден: {user_input}", "error")

def select_model():
    """Выбор модели с описанием"""
    models = {
        "tiny": {"desc": "⚡ Самая быстрая, наименее точная (~1 GB RAM)", "speed": "🚀"},
        "base": {"desc": "🚀 Быстрая, базовая точность (~1 GB RAM)", "speed": "⚡"},
        "small": {"desc": "✅ Рекомендуемая, хороший баланс (~2 GB RAM)", "speed": "📊"},
        "medium": {"desc": "🐢 Точная, но медленная (~5 GB RAM)", "speed": "🐌"},
        "large": {"desc": "🐌 Самая точная, очень медленная (~10 GB RAM)", "speed": "⏰"}
    }
    
    print(f"\n{Colors.BOLD}🤖 ВЫБОР МОДЕЛИ{Colors.ENDC}")
    print("─" * 50)
    
    for key, info in models.items():
        default = " (по умолчанию)" if key == "small" else ""
        print(f"  {info['speed']} {Colors.BOLD}{key}{Colors.ENDC}: {info['desc']}{default}")
    
    print("─" * 50)
    
    while True:
        model_size = input(f"{Colors.BOLD}Модель >{Colors.ENDC} ").strip().lower() or "small"
        
        if model_size in models:
            print_step(f"Выбрана модель: {model_size} {models[model_size]['speed']}", "success")
            return model_size
        else:
            print_step("Неверный выбор. Используйте: tiny/base/small/medium/large", "error")

def get_audio_duration(audio_path):
    """Получение длительности аудиофайла с помощью ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, 
                              creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except:
        pass
    return None

def transcribe_with_progress(audio_path, model_size, whisper_module):
    """Транскрибация с визуализацией прогресса и сбором статистики"""
    
    print(f"\n{Colors.BOLD}🎯 НАЧАЛО ОБРАБОТКИ{Colors.ENDC}")
    print("─" * 50)
    
    stats = {
        "start_time": time.time(),
        "model_load_time": 0,
        "transcribe_time": 0,
        "total_time": 0,
        "audio_duration": get_audio_duration(audio_path)
    }
    
    # Загрузка модели
    print_step(f"Загрузка модели {model_size}...", "pending")
    model_load_start = time.time()
    
    try:
        with Spinner(f"Загрузка модели {model_size}"):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = whisper_module.load_model(model_size)
        
        stats["model_load_time"] = time.time() - model_load_start
        print_step(f"Модель {model_size} загружена", "success")
    except Exception as e:
        print_step(f"Ошибка загрузки модели: {e}", "error")
        return None, stats
    
    # Распознавание
    print_step(f"Распознавание аудио: {os.path.basename(audio_path)}", "pending")
    transcribe_start = time.time()
    
    try:
        with Spinner("Распознавание речи"):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = model.transcribe(audio_path)
        
        stats["transcribe_time"] = time.time() - transcribe_start
        stats["total_time"] = time.time() - stats["start_time"]
        print_step("Аудио обработано", "success")
        
        return result, stats
    except Exception as e:
        print_step(f"Ошибка распознавания: {e}", "error")
        return None, stats

def print_statistics(stats, result, audio_path):
    """Вывод статистики распознавания"""
    
    print(f"\n{Colors.BOLD}📊 СТАТИСТИКА РАСПОЗНАВАНИЯ{Colors.ENDC}")
    print("─" * 50)
    
    # Информация о файле
    file_size = os.path.getsize(audio_path) / (1024 * 1024)
    print(f"{Colors.CYAN}Файл:{Colors.ENDC} {os.path.basename(audio_path)}")
    print(f"{Colors.CYAN}Размер файла:{Colors.ENDC} {file_size:.1f} MB")
    
    if stats["audio_duration"]:
        audio_duration_str = format_time(stats["audio_duration"])
        print(f"{Colors.CYAN}Длительность аудио:{Colors.ENDC} {audio_duration_str}")
    
    # Временные показатели
    print(f"\n{Colors.BOLD}⏱️  Временные показатели:{Colors.ENDC}")
    print(f"  • Загрузка модели: {stats['model_load_time']:.1f} сек")
    print(f"  • Распознавание: {stats['transcribe_time']:.1f} сек")
    print(f"  • Общее время: {stats['total_time']:.1f} сек")
    
    # Коэффициент ускорения/замедления
    if stats["audio_duration"] and stats["transcribe_time"] > 0:
        ratio = stats["transcribe_time"] / stats["audio_duration"]
        print(f"  • Коэффициент обработки: {ratio:.2f}x (в {ratio:.1f} раз медленнее реального времени)")
    
    # Информация о тексте
    word_count = len(result["text"].split())
    char_count = len(result["text"])
    print(f"\n{Colors.BOLD}📝 Информация о тексте:{Colors.ENDC}")
    print(f"  • Количество слов: {word_count}")
    print(f"  • Количество символов: {char_count}")
    print(f"  • Язык: {result.get('language', 'не определен')}")
    
    # Скорость распознавания
    if stats["transcribe_time"] > 0:
        words_per_second = word_count / stats["transcribe_time"]
        print(f"  • Скорость: {words_per_second:.1f} слов/сек")

def save_results(audio_path, result, model_size, stats):
    """Сохранение результатов только в TXT и JSON форматах"""
    
    print(f"\n{Colors.BOLD}💾 СОХРАНЕНИЕ РЕЗУЛЬТАТОВ{Colors.ENDC}")
    print("─" * 50)
    
    # Создаем базовое имя для файлов
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Папка для сохранения результатов
    audio_dir = os.path.dirname(audio_path)
    output_dir = os.path.join(audio_dir, "transcriptions")
    os.makedirs(output_dir, exist_ok=True)
    
    output_base = os.path.join(output_dir, f"{base_name}_{timestamp}")
    
    saved_files = []
    
    # 1. TXT файл (только текст)
    txt_file = f"{output_base}.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(result["text"])
    print_step(f"TXT сохранен: {os.path.basename(txt_file)}", "success")
    saved_files.append(txt_file)
    
    # 2. JSON файл (полная информация + статистика)
    json_file = f"{output_base}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        output_data = {
            "file_info": {
                "path": audio_path,
                "name": os.path.basename(audio_path),
                "size_mb": os.path.getsize(audio_path) / (1024 * 1024),
                "duration_sec": stats.get("audio_duration")
            },
            "processing_info": {
                "model": model_size,
                "timestamp": timestamp,
                "load_time_sec": stats["model_load_time"],
                "transcribe_time_sec": stats["transcribe_time"],
                "total_time_sec": stats["total_time"],
                "language": result.get("language", "unknown")
            },
            "text_info": {
                "full_text": result["text"],
                "word_count": len(result["text"].split()),
                "char_count": len(result["text"])
            },
            "segments": result["segments"]
        }
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print_step(f"JSON сохранен: {os.path.basename(json_file)}", "success")
    saved_files.append(json_file)
    
    return output_dir, saved_files

def show_preview(text, max_length=300):
    """Показ предпросмотра текста"""
    print(f"\n{Colors.BOLD}📝 ПРЕДПРОСМОТР ТЕКСТА{Colors.ENDC}")
    print("─" * 50)
    
    if len(text) > max_length:
        preview = text[:max_length] + "..."
    else:
        preview = text
    
    print(f"{Colors.CYAN}{preview}{Colors.ENDC}")
    print("─" * 50)

def main():
    """Главная функция"""
    
    # Очищаем экран
    os.system('cls' if sys.platform == 'win32' else 'clear')
    
    # Показываем баннер
    print_banner()
    
    # Проверяем зависимости
    deps_ok, whisper_module = check_dependencies()
    
    if not deps_ok:
        print_installation_instructions()
        input(f"\n{Colors.CYAN}Нажмите Enter для выхода...{Colors.ENDC}")
        return
    
    # Основной цикл
    while True:
        # Получаем путь к аудио
        audio_path = get_audio_path()
        if not audio_path:
            break
        
        # Выбираем модель
        model_size = select_model()
        
        # Транскрибация со статистикой
        result, stats = transcribe_with_progress(audio_path, model_size, whisper_module)
        
        if result:
            # Показываем статистику
            print_statistics(stats, result, audio_path)
            
            # Сохраняем результаты
            output_dir, saved_files = save_results(audio_path, result, model_size, stats)
            
            # Показываем предпросмотр
            show_preview(result["text"])
            
            # Финальное сообщение
            print(f"\n{Colors.GREEN}╔══════════════════════════════════════════════════════════╗{Colors.ENDC}")
            print(f"{Colors.GREEN}║{Colors.ENDC}            🎉  ГОТОВО! ФАЙЛЫ СОХРАНЕНЫ              {Colors.GREEN}║{Colors.ENDC}")
            print(f"{Colors.GREEN}╚══════════════════════════════════════════════════════════╝{Colors.ENDC}")
            print(f"{Colors.BOLD}Папка:{Colors.ENDC} {output_dir}")
            for file in saved_files:
                print(f"  {Colors.CYAN}📄{Colors.ENDC} {os.path.basename(file)}")
        
        # Спрашиваем о продолжении
        print(f"\n{Colors.BOLD}🔄 ПРОДОЛЖИТЬ?{Colors.ENDC}")
        print("─" * 50)
        again = input(f"{Colors.BOLD}Обработать еще файл? (y/n):{Colors.ENDC} ").strip().lower()
        
        if again != 'y':
            print(f"\n{Colors.GREEN}👋 Спасибо за использование! До свидания!{Colors.ENDC}")
            break
        
        # Очищаем экран для следующего файла
        os.system('cls' if sys.platform == 'win32' else 'clear')
        print_banner()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️ Программа прервана пользователем{Colors.ENDC}")
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Неожиданная ошибка: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n{Colors.CYAN}Нажмите Enter для выхода...{Colors.ENDC}")
        input()