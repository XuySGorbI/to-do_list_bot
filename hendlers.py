from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from crud import *
from datetime import datetime
from typing import Optional, List, Dict

router = Router()

async def update_task_field(pool, task_name: str, user_tgteg: str, field_name: str, new_value: str) -> str:
    """
    Обновляет указанное поле задачи по пользовательскому названию поля.
    """
    # Сопоставление пользовательских названий полей с колонками базы данных
    field_mapping = {
        "задача":"name",
        "название": "name",
        "время": "time_end",
        "дата": "date_end",
        "прогресс": "prpgress"
    }

    # Приведение названия поля к нижнему регистру и проверка его допустимости
    field = field_mapping.get(field_name.lower())  # Приводим к нижнему регистру
    if not field:
        return f"Ошибка: Поле '{field_name}' не поддерживается для обновления."

    # Преобразование значения для даты или времени
    if field == "date_end":
        try:
            date_obj = datetime.strptime(new_value, "%d.%m.%y")
            new_value = date_obj.strftime("%Y-%m-%d")  # Формат YYYY-MM-DD
        except ValueError:
            return "Ошибка: Неверный формат даты. Ожидается 'ДД.ММ.ГГ'."
    elif field == "time_end":
        try:
            time_obj = datetime.strptime(new_value, "%H:%M")
            new_value = time_obj.strftime("%H:%M:%S")  # Формат HH:MM:SS
        except ValueError:
            return "Ошибка: Неверный формат времени. Ожидается 'ЧЧ:ММ'."

    # Выполнение обновления в базе данных
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            try:
                # Обновляем указанное поле
                query = f"UPDATE task SET {field} = %s WHERE name = %s AND users_tgteg = %s"
                await cur.execute(query, (new_value, task_name, user_tgteg))
                await conn.commit()
                
                # Проверяем, была ли обновлена хотя бы одна запись
                if cur.rowcount == 0:
                    return f"Ошибка: Задача '{task_name}' не найдена для пользователя '{user_tgteg}'."
                return f"Поле '{field_name}' успешно обновлено для задачи '{task_name}'. Новое значение: {new_value}."
            except Exception as e:
                return f"Ошибка: Не удалось обновить задачу: {str(e)}"




async def parse_and_add_task(pool, command: str, user_tgteg: str) -> str:
    """
    Парсит команду и добавляет задачу.
    """
    try:
        # Удаляем "/add_task" и разбиваем строку на части
        if not command.startswith("/add_task "):
            return "Ошибка: Команда должна начинаться с '/add_task'."
        
        # Извлекаем параметры задачи
        parts = command[len("/add_task "):].split(",")
        if len(parts) < 3:
            return "Ошибка: Недостаточно параметров. Ожидается: 'Название, Время, Дата'."
        
        # Чистим пробелы вокруг параметров
        task_name = parts[0].strip()
        time_raw = parts[1].strip()
        date_raw = parts[2].strip()

        # Преобразуем дату и время в нужный формат
        try:
            date_obj = datetime.strptime(date_raw, "%d.%m.%y")  # Парсим дату
            time_obj = datetime.strptime(time_raw, "%H:%M")  # Парсим время

            # Преобразуем их в строковый формат ISO 8601
            date_end = date_obj.strftime("%Y-%m-%d")  # Формат YYYY-MM-DD
            time_end = time_obj.strftime("%H:%M:%S")  # Формат HH:MM:SS
        except ValueError:
            return "Ошибка: Неверный формат даты или времени. Ожидается 'ДД.ММ.ГГ' и 'ЧЧ:ММ'."

        # Вызываем функцию создания задачи
        await create_task_with_check(
            pool=pool,
            task_name=task_name,
            user_tgteg=user_tgteg,
            date_end=date_end,
            time_end=time_end,
            progress="Pending"
        )
        return f"Задача '{task_name}' успешно добавлена для пользователя '{user_tgteg}' с датой {date_end} и временем {time_end}."
    
    except Exception as e:
        return f"Ошибка: Не удалось создать задачу: {str(e)}"


async def view_tasks(pool, user_tgteg: Optional[str] = None) -> str:
    """
    Возвращает задачи пользователя или всех пользователей.
    """
    tasks = await read_tasks(pool, user_tgteg)
    if not tasks:
        return "Задачи не найдены."
    
    # Форматируем задачи для вывода
    formatted_tasks = "\n".join(
        f"Задача: {task['name']}, Дата: {task['date_end']}, Время: {task['time_end']}, Прогресс: {task['prpgress']}"
        for task in tasks
    )
    return formatted_tasks


async def ensure_user_exists(pool, tgteg: str, name: Optional[str] = None, userscol: Optional[str] = None) -> str:
    """
    Проверяет, существует ли пользователь, если нет — создаёт.
    """
    # Проверяем, существует ли пользователь
    existing_users = await read_users(pool, tgteg)
    if not existing_users:
        # Если пользователь не найден, создаём его
        await create_user(pool, tgteg, name, userscol)
        return f"Пользователь {tgteg} создан."
    return f"Пользователь {tgteg} уже существует."


async def create_task_with_check(pool, task_name: str, user_tgteg: str, date_end: Optional[str] = None,
                                 time_end: Optional[str] = None, progress: Optional[str] = None,
                                 schedulecol: Optional[str] = None) -> str:
    """
    Проверяет существование пользователя и создаёт задачу.
    """
    # Проверяем, существует ли пользователь
    await ensure_user_exists(pool, user_tgteg)
    
    # Создаём задачу
    await create_task(pool, task_name, user_tgteg, date_end, time_end, progress, schedulecol)
    return f"Задача '{task_name}' для пользователя '{user_tgteg}' успешно создана."


@router.message(Command("start"))
async def start(message: Message):
    pool = await connect_to_db()
    result = await ensure_user_exists(pool, message.chat.username)
    await message.answer(result)


@router.message(Command("add_task"))
async def add_task(message: Message):
    pool = await connect_to_db()
    result = await parse_and_add_task(pool, message.text, message.chat.username)
    await message.answer(result)


@router.message(Command("view_task"))
async def view_task(message: Message):
    pool = await connect_to_db()
    result = await view_tasks(pool, message.chat.username)
    await message.answer(result)

@router.message(Command("update_task"))
async def update_task_handler(message: Message):
    """
    Обработчик команды /update_task для изменения задачи.
    Формат команды: /update_task <поле>, <название задачи>, <новое значение>
    Пример: /update_task прогресс, Сделать уроки, Completed
    """
    pool = await connect_to_db()
    try:
        # Извлекаем текст команды
        command = message.text[len("/update_task "):].strip()
        
        # Разделяем строку по запятым
        parts = [part.strip() for part in command.split(",")]
        if len(parts) < 3:
            await message.answer(
                "Ошибка: Неверный формат команды. Ожидается: <поле>, <название задачи>, <новое значение>.\n"
                "Пример: /update_task прогресс, Сделать уроки, Completed"
            )
            return
        
        # Извлекаем поле, название задачи и новое значение
        field_name = parts[0]
        task_name = parts[1]
        new_value = parts[2]

        # Вызываем функцию обновления задачи
        result = await update_task_field(pool, task_name, message.chat.username, field_name, new_value)
        await message.answer(result)
    finally:
        pool.close()
        await pool.wait_closed()
