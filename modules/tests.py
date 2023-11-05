from unittest.mock import patch

from rest_framework import status

from modules.models import Module
from users.tests import UserModelTestCase


# Create your tests here.
class ModuleAPITestCase(UserModelTestCase):
    """Класс для создания тестовых объектов модели Module."""
    def setUp(self) -> None:
        super().setUp()

        # Создание объекта Module для тестового пользователя
        self.module_object_1 = Module.objects.create(
            title='математика',
            description='работа с числами',
            module_user=self.user_test
        )
        self.module_object_1.save()

        # Создание объекта Module для второго пользователя
        self.module_object_2 = Module.objects.create(
            title='русский язык',
            description='работа с буквами',
            module_user=self.user_2
        )
        self.module_object_2.save()

        # Сырые данные для создания объекта Module
        self.raw_data = {
            'description': 'тестовое описание',
            'module_user': 'test@test.com'
        }

    def tearDown(self) -> None:
        super().tearDown()


class ModuleCreateTestCase(ModuleAPITestCase):
    """Для тестирования API-запросов на создание объектов модели Module."""
    def setUp(self) -> None:
        super().setUp()

        # Получение маршрутов
        self.create_url = '/modules/create/'

    def test_user_cannot_create_module_without_authentication(self):
        """Неавторизованные пользователи не могут создавать объекты модели Module."""

        # Дополнение сырых данных недостающими полями
        self.raw_data['title'] = 'Тестовое название'

        # Количество модулей до создания
        self.assertTrue(
            Module.objects.count() == 2
        )

        # Отключение отложенной задачи
        self.patcher = patch('modules.tasks.send_email_creation.delay')
        self.mock_task = self.patcher.start()

        # POST-запрос на создание модуля
        response = self.client.post(
            self.create_url,
            self.raw_data,
            headers=None,
            format='json'
        )

        # Количество модулей после создания
        self.assertTrue(
            Module.objects.count() == 2
        )

        # Проверка статуса
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        # Проверка содержимого ответа
        self.assertEqual(
            response.json(),
            {'detail': 'Учетные данные не были предоставлены.'}
        )

        # Включение отложенной задачи
        self.patcher.stop()

    def test_user_cannot_create_module_with_incorrect_title(self):
        """Авторизованные пользователи не могут создавать объекты модели Module с запрещенными словами."""

        # Дополнение сырых данных недостающими полями
        self.raw_data['title'] = 'казино'

        # Количество модулей до создания
        self.assertTrue(
            Module.objects.count() == 2
        )

        # Отключение отложенной задачи
        self.patcher = patch('modules.tasks.send_email_creation.delay')
        self.mock_task = self.patcher.start()

        # POST-запрос на создание модуля
        response = self.client.post(
            self.create_url,
            self.raw_data,
            headers=self.headers_user_1,
            format='json'
        )

        # Количество модулей после создания
        self.assertTrue(
            Module.objects.count() == 2
        )

        # Проверка статуса
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        # Проверка содержимого ответа
        self.assertEqual(
            response.json(),
            {'banned_words': ['Нельзя публиковать запрещенные материалы']}
        )

        # Включение отложенной задачи
        self.patcher.stop()

    def test_user_can_create_module_correctly(self):
        """Авторизованные пользователи могут создавать объекты модели Module корректно."""

        # Дополнение сырых данных недостающими полями
        self.raw_data['title'] = 'Data science'

        # Количество модулей до создания
        self.assertTrue(
            Module.objects.count() == 2
        )

        # Отключение отложенной задачи
        self.patcher = patch('modules.tasks.send_email_creation.delay')
        self.mock_task = self.patcher.start()

        # POST-запрос на создание модуля
        response = self.client.post(
            self.create_url,
            self.raw_data,
            headers=self.headers_user_1,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        # Количество модулей после создания
        self.assertTrue(
            Module.objects.count() == 3
        )

        # Включение отложенной задачи
        self.patcher.stop()


class ModuleGetTestCase(ModuleAPITestCase):
    """Для тестирования API-запросов на получение объектов модели Module."""
    def setUp(self) -> None:
        super().setUp()

        # Получение маршрутов
        self.get_url = '/modules/'

    def test_user_can_get_modules_correctly(self):
        """Авторизованные пользователи могут получать информацию об объектах модели Module корректно."""

        # GET-запрос на получение всех модулей
        response = self.client.get(
            self.get_url,
            headers=self.headers_user_1,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        # Проверка количества объектов в содержании ответа
        self.assertTrue(
            len(response.json()) == 2
        )

        # Проверка количества объектов в базе данных
        self.assertTrue(
            Module.objects.count() == 2
        )

    def test_user_cannot_get_modules_without_authentication(self):
        """Неавторизованные пользователи не могут получать информацию об объектах модели Module."""

        # GET-запрос на получение всех модулей
        response = self.client.get(
            self.get_url,
            headers=None,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        # Проверка содержимого ответа
        self.assertEqual(
            response.json(),
            {'detail': 'Учетные данные не были предоставлены.'}
        )

    def test_user_can_get_detail_module_correctly_owner(self):
        """Авторизованные пользователи могут получать детальную информацию об объектах модели Module, чьими
        владельцами они являются."""

        # маршрут до объекта Module тестового пользователя
        self.get_detail_url = f'/modules/{self.module_object_1.pk}/'

        # GET-запрос на получение конкретного модуля
        response = self.client.get(
            self.get_detail_url,
            headers=self.headers_user_1,
            format='json'
        )
        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        # Проверка на пользователя объекта Module
        self.assertEqual(
            response.json().get('module_user').get('email'),
            self.user_test.email
        )

    def test_user_cannot_get_detail_module_without_authentication(self):
        """Неавторизованные пользователи не могут получать детальную информацию об объектах модели Module."""

        # маршрут до объекта Module тестового пользователя
        self.get_detail_url = f'/modules/{self.module_object_1.pk}/'

        # GET-запрос на получение конкретного модуля
        response = self.client.get(
            self.get_detail_url,
            headers=None,
            format='json'
        )
        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        # Проверка содержимого ответа
        self.assertEqual(
            response.json(),
            {'detail': 'Учетные данные не были предоставлены.'}
        )

    def test_user_cannot_detail_module_not_owner(self):
        """Авторизованные пользователи не могут получать детальную информацию об объектах модели Module, чьими
        владельцами они не являются."""

        # маршрут до объекта Module тестового пользователя
        self.get_detail_url = f'/modules/{self.module_object_1.pk}/'

        # GET-запрос на получение модуля тестового пользователя вторым пользователем
        response = self.client.get(
            self.get_detail_url,
            headers=self.headers_user_2,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        # Проверка содержимого ответа
        self.assertEqual(
            response.json(),
            {'detail': 'У вас недостаточно прав для выполнения данного действия.'}
        )


class ModuleUpdateTestCase(ModuleAPITestCase):
    """Для тестирования API-запросов на изменение информации объектов модели Module."""

    def setUp(self) -> None:
        super().setUp()

        # Получение маршрута объекта Module тестового пользователя
        self.update_url = f'/modules/update/{self.module_object_1.pk}/'

        # Данные для обновления объекта модуля
        self.update_data = {
            'title': 'Астрономия'
        }

    def test_user_cannot_update_module_without_authentication(self):
        """Неавторизованные пользователи не могут изменять детальную информацию объектов модели Module."""

        # PATCH-запрос на обновление объекта модели тестового пользователя
        response = self.client.patch(
            self.update_url,
            self.update_data,
            headers=None,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        # Проверка содержимого ответа
        self.assertEqual(
            response.json(),
            {'detail': 'Учетные данные не были предоставлены.'}
        )

    def test_user_cannot_update_module_with_banned_word(self):
        """Авторизованные пользователи не могут изменять детальную информацию объектов модели Module с использованием
        запрещенных слов."""

        # PATCH-запрос на обновление объекта модели тестового пользователя
        response = self.client.patch(
            self.update_url,
            {'title': 'казино'},
            headers=self.headers_user_1,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        # Проверка содержимого ответа
        self.assertEqual(
            response.json(),
            {'banned_words': ['Нельзя публиковать запрещенные материалы']}
        )

    def test_user_cannot_update_module_another_user(self):
        """Авторизованные пользователи не могут изменять детальную информацию объектов модели Module чужих
        пользователей."""

        # PATCH-запрос на обновление объекта модели тестового пользователя вторым пользователем
        response = self.client.patch(
            self.update_url,
            self.update_data,
            headers=self.headers_user_2,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        # Проверка содержимого ответа
        self.assertEqual(
            response.json(),
            {'detail': 'У вас недостаточно прав для выполнения данного действия.'}
        )

    def test_user_can_update_module_correctly(self):
        """Авторизованные пользователи могут изменять детальную информацию объектов модели Module корректно."""

        # PATCH-запрос на обновление объекта модели тестового пользователя
        response = self.client.patch(
            self.update_url,
            self.update_data,
            headers=self.headers_user_1,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        # Проверка изменения поля <title> на <Астрономия>
        self.assertEqual(
            response.json().get('title'),
            'Астрономия'
        )


class ModuleDeleteTestCase(ModuleAPITestCase):
    """Для тестирования API-запросов на удаление объектов модели Module."""

    def setUp(self) -> None:
        super().setUp()

        # Получение маршрута объекта Module тестового пользователя
        self.delete_url = f'/modules/delete/{self.module_object_1.pk}/'

    def test_user_cannot_delete_module_without_authentication(self):
        """Неавторизованные пользователи могут удалять объекты модели Module."""

        # DELETE-запрос на удаление объекта модели тестового пользователя
        response = self.client.delete(
            self.delete_url,
            headers=None,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

        # Проверка содержимого ответа
        self.assertEqual(
            response.json(),
            {'detail': 'Учетные данные не были предоставлены.'}
        )

    def test_user_cannot_delete_module_another_user(self):
        """Авторизованные пользователи могут удалять объекты модели Module чужих пользователей."""

        # DELETE-запрос на удаление объекта модели тестового пользователя вторым пользователем
        response = self.client.delete(
            self.delete_url,
            headers=self.headers_user_2,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

        # Проверка содержимого ответа
        self.assertEqual(
            response.json(),
            {'detail': 'У вас недостаточно прав для выполнения данного действия.'}
        )

    def test_user_can_delete_module_correctly(self):
        """Авторизованные пользователи могут удалять объекты модели Module корректно."""

        # Количество объектов модели Module до удаления
        self.assertTrue(
            Module.objects.count() == 2
        )

        # DELETE-запрос на удаление объекта модели тестового пользователя
        response = self.client.delete(
            self.delete_url,
            headers=self.headers_user_1,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        # Количество объектов модели Module после удаления
        self.assertTrue(
            Module.objects.count() == 1
        )
