import aiomysql
from typing import List, Dict, Optional
from config import DB_SETTINGS

# Настройки для подключения к базе данных



async def create_task(pool, name: str, users_tgteg: str, date_end: Optional[str] = None, 
                      time_end: Optional[str] = None, progress: Optional[str] = None, 
                      schedulecol: Optional[str] = None):

    async with pool.acquire() as conn:  # Получаем соединение из пула
        async with conn.cursor() as cur:  # Создаем курсор для выполнения SQL-запросов
            # Выполняем SQL-запрос для добавления записи в таблицу task
            await cur.execute("""
                INSERT INTO task (name, users_tgteg, date_end, time_end, prpgress, schedulecol) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, users_tgteg, date_end, time_end, progress, schedulecol))
            await conn.commit()  # Сохраняем изменения


async def read_tasks(pool, users_tgteg: Optional[str] = None) -> List[Dict]:
    """
    Считывает задачи из таблицы task. Может фильтровать по идентификатору пользователя.

    :param pool: Пул соединений с базой данных.
    :param users_tgteg: (опционально) Идентификатор пользователя для фильтрации задач.
    :return: Список задач в виде словарей.
    """
    async with pool.acquire() as conn:  # Получаем соединение из пула
        async with conn.cursor(aiomysql.DictCursor) as cur:  # Используем DictCursor для возврата данных в виде словарей
            query = "SELECT * FROM task"  # Базовый SQL-запрос
            params = []  # Параметры для фильтрации
            if users_tgteg:
                query += " WHERE users_tgteg = %s"  # Добавляем условие фильтрации по users_tgteg
                params.append(users_tgteg)  # Добавляем значение в параметры
            await cur.execute(query, params)  # Выполняем запрос с параметрами
            return await cur.fetchall()  # Возвращаем все найденные записи


async def update_task(pool, name: str, users_tgteg: str, updates: Dict):
    """
    Обновляет существующую задачу в таблице task.

    :param pool: Пул соединений с базой данных.
    :param name: Название задачи, которую нужно обновить (обязательный параметр).
    :param users_tgteg: Идентификатор пользователя, владельца задачи (обязательный параметр).
    :param updates: Словарь обновляемых значений (например, {"prpgress": "Completed"}).
    """
    async with pool.acquire() as conn:  # Получаем соединение из пула
        async with conn.cursor() as cur:  # Создаем курсор
            # Формируем часть SQL-запроса SET, где обновляем только указанные поля
            set_clause = ", ".join(f"{key} = %s" for key in updates.keys())
            query = f"""
                UPDATE task
                SET {set_clause}
                WHERE name = %s AND users_tgteg = %s
            """
            params = list(updates.values()) + [name, users_tgteg]  # Параметры для SQL-запроса
            await cur.execute(query, params)  # Выполняем запрос
            await conn.commit()  # Сохраняем изменения


async def delete_task(pool, name: str, users_tgteg: str):
    """
    Удаляет задачу из таблицы task.

    :param pool: Пул соединений с базой данных.
    :param name: Название задачи, которую нужно удалить.
    :param users_tgteg: Идентификатор пользователя, владельца задачи.
    """
    async with pool.acquire() as conn:  # Получаем соединение из пула
        async with conn.cursor() as cur:  # Создаем курсор
            # Выполняем SQL-запрос на удаление задачи
            await cur.execute("""
                DELETE FROM task 
                WHERE name = %s AND users_tgteg = %s
            """, (name, users_tgteg))
            await conn.commit()  # Сохраняем изменения
            

# Функция для создания пользователя
async def create_user(pool, tgteg: str, name: Optional[str] = None, userscol: Optional[str] = None):
    """
    Добавляет нового пользователя в таблицу users.

    :param pool: Пул соединений с базой данных.
    :param tgteg: Уникальный идентификатор пользователя (обязательный параметр).
    :param name: Имя пользователя (опционально).
    :param userscol: Дополнительное описание или параметры пользователя (опционально).
    """
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                INSERT INTO users (tgteg, name, userscol) 
                VALUES (%s, %s, %s)
            """, (tgteg, name, userscol))
            await conn.commit()

# Функция для чтения пользователей
async def read_users(pool, tgteg: Optional[str] = None) -> List[Dict]:
    """
    Извлекает список пользователей. Может фильтровать по tgteg.

    :param pool: Пул соединений с базой данных.
    :param tgteg: (опционально) Уникальный идентификатор пользователя для фильтрации.
    :return: Список пользователей в виде словарей.
    """
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            query = "SELECT * FROM users"  # Базовый SQL-запрос
            params = []
            if tgteg:
                query += " WHERE tgteg = %s"  # Условие фильтрации
                params.append(tgteg)
            await cur.execute(query, params)
            return await cur.fetchall()

# Функция для удаления пользователя
async def delete_user(pool, tgteg: str):
    """
    Удаляет пользователя из таблицы users.

    :param pool: Пул соединений с базой данных.
    :param tgteg: Уникальный идентификатор пользователя, которого нужно удалить.
    """
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                DELETE FROM users 
                WHERE tgteg = %s
            """, (tgteg,))
            await conn.commit()

async def connect_to_db():
    """
    Создает пул соединений для работы с базой данных.

    :return: Пул соединений aiomysql.
    """
    return await aiomysql.create_pool(**DB_SETTINGS)  # Создаем и возвращаем пул соединений


