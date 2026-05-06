from django.test import TestCase, Client
from django.urls import reverse

from tasks.views import evaluate_access, add_log_entry, EVENT_LOG


class VMGuardUnitTests(TestCase):
    """
    Модульные тесты для проверки логики контейнера VM Guard.
    """

    def setUp(self):
        """
        Очистка журнала событий перед каждым тестом.
        """
        EVENT_LOG.clear()

    def test_admin_access_allowed(self):
        """
        Проверка разрешения операции для администратора.
        """
        allowed, role, reason = evaluate_access(
            "kirill",
            "kirill123",
            "Удаление",
            "secure-db.img"
        )

        self.assertTrue(allowed)
        self.assertEqual(role, "admin")
        self.assertEqual(reason, "Доступ разрешён")

    def test_wrong_password_denied(self):
        """
        Проверка отказа при неверном пароле.
        """
        allowed, role, reason = evaluate_access(
            "kirill",
            "wrongpass",
            "Просмотр",
            "ubuntu-base.img"
        )

        self.assertFalse(allowed)
        self.assertIsNone(role)
        self.assertEqual(reason, "Неверный пароль")

    def test_unknown_user_denied(self):
        """
        Проверка отказа для неизвестного пользователя.
        """
        allowed, role, reason = evaluate_access(
            "unknown",
            "pass123",
            "Просмотр",
            "ubuntu-base.img"
        )

        self.assertFalse(allowed)
        self.assertIsNone(role)
        self.assertEqual(reason, "Пользователь не найден")

    def test_operator_permission_denied(self):
        """
        Проверка отказа при попытке оператора выполнить запрещенную операцию.
        """
        allowed, role, reason = evaluate_access(
            "albert",
            "albert456",
            "Изменение",
            "secure-db.img"
        )

        self.assertFalse(allowed)
        self.assertEqual(role, "operator")
        self.assertIn("запрещена", reason)

    def test_auditor_view_allowed(self):
        """
        Проверка разрешения просмотра для аудитора.
        """
        allowed, role, reason = evaluate_access(
            "ivan",
            "ivan789",
            "Просмотр",
            "ubuntu-base.img"
        )

        self.assertTrue(allowed)
        self.assertEqual(role, "auditor")
        self.assertEqual(reason, "Доступ разрешён")

    def test_archive_delete_denied(self):
        """
        Проверка запрета удаления архивного образа.
        """
        allowed, role, reason = evaluate_access(
            "kirill",
            "kirill123",
            "Удаление",
            "archive-template.img"
        )

        self.assertFalse(allowed)
        self.assertEqual(role, "admin")
        self.assertEqual(reason, "Архивный образ запрещено удалять через веб-интерфейс")

    def test_log_entry_added(self):
        """
        Проверка добавления записи в журнал событий безопасности.
        """
        add_log_entry(
            username="kirill",
            role="admin",
            image_name="secure-db.img",
            operation="Удаление",
            action="Разрешено",
            reason="Доступ разрешён"
        )

        self.assertEqual(len(EVENT_LOG), 1)
        self.assertEqual(EVENT_LOG[0]["user"], "kirill")
        self.assertEqual(EVENT_LOG[0]["role"], "admin")
        self.assertEqual(EVENT_LOG[0]["action"], "Разрешено")


class VMGuardWebTests(TestCase):
    """
    Функциональные тесты маршрутов Django-приложения.
    """

    def setUp(self):
        """
        Создание тестового клиента Django и очистка журнала.
        """
        self.client = Client()
        EVENT_LOG.clear()

    def test_index_page_available(self):
        """
        Проверка доступности главной страницы приложения.
        """
        response = self.client.get(reverse("tasks:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Проверка доступа")

    def test_logs_page_available(self):
        """
        Проверка доступности страницы журнала событий.
        """
        response = self.client.get(reverse("tasks:logs"))

        self.assertEqual(response.status_code, 200)

    def test_check_access_allowed(self):
        """
        Проверка обработки разрешенной операции через веб-форму.
        """
        response = self.client.post(reverse("tasks:check_access"), {
            "username": "kirill",
            "password": "kirill123",
            "image_name": "secure-db.img",
            "operation": "Удаление",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Разрешено")
        self.assertEqual(len(EVENT_LOG), 1)
        self.assertEqual(EVENT_LOG[0]["action"], "Разрешено")

    def test_check_access_denied_wrong_password(self):
        """
        Проверка обработки отказа при неверном пароле через веб-форму.
        """
        response = self.client.post(reverse("tasks:check_access"), {
            "username": "kirill",
            "password": "wrongpass",
            "image_name": "ubuntu-base.img",
            "operation": "Просмотр",
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неверный пароль")
        self.assertEqual(len(EVENT_LOG), 1)
        self.assertEqual(EVENT_LOG[0]["action"], "Отклонено")