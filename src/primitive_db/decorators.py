import time
from functools import wraps


def handle_db_errors(func):
    """Decorator for centralized database error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден.",
                  "Возможно, база данных не инициализирована.")
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper


def confirm_action(action_name: str):
    """Decorator factory for confirming dangerous operations (y/n)."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            prompt = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            answer = input(prompt).strip().lower()
            if answer == "y":
                return func(*args, **kwargs)
            else:
                print("Операция отменена пользователем.")
                return args[0] if args else None
        return wrapper
    return decorator


def log_time(func):
    """Decorator for measuring function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()
        elapsed = end_time - start_time
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд")
        return result
    return wrapper


def create_cacher():
    """Creates a cacher using a closure.."""
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            print("[Кэш] Возвращаем данные из кэша.")
            return cache[key]
        
        print("[Кэш] Выполняем запрос к данным...")
        result = value_func()
        cache[key] = result
        return result

    return cache_result
