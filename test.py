import unittest
from unittest.mock import AsyncMock, MagicMock
import aiomysql
from crud import *  # Измените 'your_module' на правильное имя вашего модуля

class TestCreateTask(unittest.TestCase):

    def setUp(self):
        self.pool = MagicMock()
        self.db = connect_to_db()  # Пул соединений
        self.name = "Task 1"
        self.users_tgteg = "user1"
        self.date_end = "2024-12-16"
        self.time_end = "12:00"
        self.progress = "In Progress"
        self.schedulecol = "schedule1"

    async def test_create_task_success(self):
        self.pool.acquire = AsyncMock(return_value=MagicMock())
        self.pool.acquire().cursor = AsyncMock(return_value=MagicMock())

        await create_task(self.pool, self.name, self.users_tgteg, self.date_end, self.time_end, self.progress, self.schedulecol)

        self.pool.acquire().cursor().execute.assert_called_once_with(
            "INSERT INTO task (name, users_tgteg, date_end, time_end, prpgress, schedulecol) VALUES (%s, %s, %s, %s, %s, %s)",
            (self.name, self.users_tgteg, self.date_end, self.time_end, self.progress, self.schedulecol)
        )
        self.pool.acquire().commit.assert_called_once()

    async def test_create_task_missing_name(self):
        with self.assertRaises(TypeError):  # or ValueError, depending on implementation
            await create_task(self.pool, None, self.users_tgteg, self.date_end, self.time_end, self.progress, self.schedulecol)

    async def test_create_task_invalid_date(self):
        with self.assertRaises(TypeError):  # Assuming date_end and time_end are expected to be strings
            await create_task(self.pool, self.name, self.users_tgteg, 123, self.time_end, self.progress, self.schedulecol)

# Further tests for `read_tasks`, `update_task`, `delete_task`, `create_user`, `read_users`, and `delete_user`
# would follow a similar structure.


class TestReadTasks(unittest.TestCase):

    def setUp(self):
        self.pool = MagicMock()
        self.db = connect_to_db()  # Пул соединений
        self.users_tgteg = "user1"

    async def test_read_tasks_no_filter(self):
        self.pool.acquire = AsyncMock(return_value=MagicMock())
        self.pool.acquire().cursor = AsyncMock(return_value=MagicMock())
        self.pool.acquire().cursor().fetchall = AsyncMock(return_value=[{'id': 1, 'name': 'Task 1'}])

        result = await read_tasks(self.pool)

        self.assertEqual(result, [{'id': 1, 'name': 'Task 1'}])
        self.pool.acquire().cursor().execute.assert_called_once_with("SELECT * FROM task", [])
        self.pool.acquire().commit.assert_not_called()

    async def test_read_tasks_with_filter(self):
        self.pool.acquire = AsyncMock(return_value=MagicMock())
        self.pool.acquire().cursor = AsyncMock(return_value=MagicMock())
        self.pool.acquire().cursor().fetchall = AsyncMock(return_value=[{'id': 1, 'name': 'Task 1'}])

        result = await read_tasks(self.pool, self.users_tgteg)

        self.assertEqual(result, [{'id': 1, 'name': 'Task 1'}])
        self.pool.acquire().cursor().execute.assert_called_once_with("SELECT * FROM task WHERE users_tgteg = %s", [self.users_tgteg])
        self.pool.acquire().commit.assert_not_called()

# Additional tests for `update_task`, `delete_task`, `create_user`, `read_users`, and `delete_user`
# would follow a similar pattern.

class TestUpdateTask(unittest.TestCase):

    def setUp(self):
        self.pool = MagicMock()
        self.db = connect_to_db()  # Пул соединений
        self.name = "Task 1"
        self.users_tgteg = "user1"
        self.updates = {"prpgress": "Completed"}

    async def test_update_task_success(self):
        self.pool.acquire = AsyncMock(return_value=MagicMock())
        self.pool.acquire().cursor = AsyncMock(return_value=MagicMock())

        await update_task(self.pool, self.name, self.users_tgteg, self.updates)

        set_clause = ", ".join(f"{key} = %s" for key in self.updates.keys())
        params = list(self.updates.values()) + [self.name, self.users_tgteg]

        self.pool.acquire().cursor().execute.assert_called_once_with(
            f"UPDATE task SET {set_clause} WHERE name = %s AND users_tgteg = %s",
            params
        )
        self.pool.acquire().commit.assert_called_once()

    async def test_update_task_nonexistent(self):
        with self.assertRaises(ValueError):  # or appropriate exception based on implementation
            await update_task(self.pool, "Nonexistent Task", self.users_tgteg, self.updates)

# Further tests for `delete_task`, `create_user`, `read_users`, and `delete_user`
# would follow a similar structure.

class TestUpdateTask(unittest.TestCase):

    def setUp(self):
        self.pool = MagicMock()
        self.db = connect_to_db()  # Пул соединений
        self.name = "Task 1"
        self.users_tgteg = "user1"
        self.updates = {"prpgress": "Completed"}

    async def test_update_task_success(self):
        self.pool.acquire = AsyncMock(return_value=MagicMock())
        self.pool.acquire().cursor = AsyncMock(return_value=MagicMock())

        await update_task(self.pool, self.name, self.users_tgteg, self.updates)

        set_clause = ", ".join(f"{key} = %s" for key in self.updates.keys())
        params = list(self.updates.values()) + [self.name, self.users_tgteg]

        self.pool.acquire().cursor().execute.assert_called_once_with(
            f"UPDATE task SET {set_clause} WHERE name = %s AND users_tgteg = %s",
            params
        )
        self.pool.acquire().commit.assert_called_once()

    async def test_update_task_nonexistent(self):
        with self.assertRaises(ValueError):  # or appropriate exception based on implementation
            await update_task(self.pool, "Nonexistent Task", self.users_tgteg, self.updates)

# Further tests for `delete_task`, `create_user`, `read_users`, and `delete_user`
# would follow a similar structure.


class TestUserFunctions(unittest.TestCase):

    def setUp(self):
        self.pool = MagicMock()
        self.db = connect_to_db()  # Пул соединений
        self.tgteg = "user1"
        self.name = "John Doe"

    async def test_create_user_success(self):
        self.pool.acquire = AsyncMock(return_value=MagicMock())
        self.pool.acquire().cursor = AsyncMock(return_value=MagicMock())

        await create_user(self.pool, self.tgteg, self.name)

        self.pool.acquire().cursor().execute.assert_called_once_with(
            "INSERT INTO users (tgteg, name, userscol) VALUES (%s, %s, %s)",
            (self.tgteg, self.name, None)
        )
        self.pool.acquire().commit.assert_called_once()

    async def test_read_users_no_filter(self):
        self.pool.acquire = AsyncMock(return_value=MagicMock())
        self.pool.acquire().cursor = AsyncMock(return_value=MagicMock())
        self.pool.acquire().cursor().fetchall = AsyncMock(return_value=[{'tgteg': 'user1', 'name': 'John Doe'}])

        result = await read_users(self.pool)

        self.assertEqual(result, [{'tgteg': 'user1', 'name': 'John Doe'}])
        self.pool.acquire().cursor().execute.assert_called_once_with("SELECT * FROM users", [])
        self.pool.acquire().commit.assert_not_called()

    async def test_read_users_with_filter(self):
        self.pool.acquire = AsyncMock(return_value=MagicMock())
        self.pool.acquire().cursor = AsyncMock(return_value=MagicMock())
        self.pool.acquire().cursor().fetchall = AsyncMock(return_value=[{'tgteg': 'user1', 'name': 'John Doe'}])

        result = await read_users(self.pool, self.tgteg)

        self.assertEqual(result, [{'tgteg': 'user1', 'name': 'John Doe'}])
        self.pool.acquire().cursor().execute.assert_called_once_with("SELECT * FROM users WHERE tgteg = %s", [self.tgteg])
        self.pool.acquire().commit.assert_not_called()

    async def test_delete_user_success(self):
        self.pool.acquire = AsyncMock(return_value=MagicMock())
        self.pool.acquire().cursor = AsyncMock(return_value=MagicMock())

        await delete_user(self.pool, self.tgteg)

        self.pool.acquire().cursor().execute.assert_called_once_with(
            "DELETE FROM users WHERE tgteg = %s",
            (self.tgteg,)
        )
        self.pool.acquire().commit.assert_called_once()

    async def test_delete_user_nonexistent(self):
        with self.assertRaises(ValueError):  # or appropriate exception based on implementation
            await delete_user(self.pool, "nonexistent_user")

# Additional tests can be added similarly.
