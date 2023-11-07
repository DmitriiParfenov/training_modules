from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


# Create your tests here.
class UserModelTestCase(APITestCase):
    def setUp(self) -> None:
        # Получение маршрутов
        self.authentication_url = '/user/token/'

        # Получение тестового пользователя
        self.user_test = User.objects.create(
            email='test@test.com',
            first_name='Ivan',
            last_name='Ivanov',
            is_staff=False,
            is_superuser=False,
            is_active=True
        )
        self.user_test.set_password('ChooseBestPassword')
        self.user_test.save()
        self.user_data = {
            'email': 'test@test.com',
            'password': 'ChooseBestPassword'
        }

        # Аутентификация тестового пользователя
        response_1 = self.client.post(
            self.authentication_url,
            self.user_data
        )

        # Получение заголовка для авторизации тестового пользователя
        self.headers_user_1 = {'Authorization': f'Bearer {response_1.json().get("access")}'}

        # Получение второго пользователя
        self.user_2 = User.objects.create(
            email='another@test.com',
            first_name='Petr',
            last_name='Petrov',
            is_staff=False,
            is_superuser=False,
            is_active=True
        )
        self.user_2.set_password('ChooseBestPassword')
        self.user_2.save()
        self.data_user_2 = {
            'email': 'another@test.com',
            'password': 'ChooseBestPassword'
        }

        # Аутентификация второго пользователя
        response_2 = self.client.post(
            self.authentication_url,
            self.data_user_2
        )

        # Получение заголовка для авторизации второго пользователя
        self.headers_user_2 = {'Authorization': f'Bearer {response_2.json().get("access")}'}

    def tearDown(self) -> None:
        return super().tearDown()


class UserRegistrationTestCase(APITestCase):
    """Тестирование регистрации / активации и авторизации пользователей."""

    def setUp(self) -> None:
        # Получение маршрутов
        self.register_url = '/auth/users/'
        self.activation_url = '/auth/users/activation/'
        self.authentication_url = '/user/token/'

        # Данные для регистрации пользователя
        self.user_data = {
            'email': 'test@test.com',
            'password': 'ChooseBestPassword'
        }

    def test_user_cannot_register_without_data(self):
        """Для регистрации пользователя необходимо предоставить email и password."""

        # POST-запрос на создание пользователя без предоставления необходимых полей
        response = self.client.post(
            self.register_url
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        # Проверка содержимого ответа
        self.assertEqual(
            response.json(),
            {
                'email': ['Обязательное поле.'],
                'password': ['Обязательное поле.']
            }
        )

    def test_user_registration_activation_authentication(self):
        """
        Предоставив email и password, пользователь зарегистрируется на сайте, но будет неактивным, так как нужна
        верификация по email. После верификации пользователь может авторизоваться на сайте с использованием JWT-токенов.
        """

        # Регистрация пользователя
        response_registration = self.client.post(
            self.register_url,
            self.user_data,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response_registration.status_code,
            status.HTTP_201_CREATED
        )

        # Проверка количества пользователей после регистрации
        self.assertEqual(
            User.objects.count(),
            1
        )

        # Выборка конкретного пользователя и проверка на активность
        user_before = User.objects.get(email='test@test.com')
        self.assertEqual(
            user_before.is_active,
            False
        )

        # Получение uid и токена для активации зарегистрированного пользователя
        email_lines = mail.outbox[0].body.splitlines()
        activation_link = [obj for obj in email_lines if "/activate/" in obj][0]
        uid, token = activation_link.split("/")[-2:]
        act_data = {
            'uid': uid,
            'token': token
        }

        # POST-запрос на активацию пользователя
        response_activation = self.client.post(
            self.activation_url,
            act_data,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response_activation.status_code,
            status.HTTP_204_NO_CONTENT
        )

        # Проверка на активность пользователя
        user_after = User.objects.get(email='test@test.com')
        self.assertEqual(
            user_after.is_active,
            True
        )

        # POST-запрос на получения токенов для аутентификации
        response_authentication = self.client.post(
            self.authentication_url,
            self.user_data,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response_authentication.status_code,
            status.HTTP_200_OK
        )

        token_data = {
            'access': True if response_authentication.json().get('access') else False,
            'refresh': True if response_authentication.json().get('refresh') else False,

        }

        self.assertEqual(
            token_data,
            {'access': True, 'refresh': True}
        )


class UserActionTestCase(UserModelTestCase):

    def setUp(self) -> None:
        super().setUp()
        user_1 = User.objects.get(email='test@test.com')

        # Получение маршрутов
        self.user_detail_url = f'/auth/users/{user_1.pk}/'
        self.user_update_url = f'/auth/users/{user_1.pk}/'
        self.user_delete_url = f'/auth/users/{user_1.pk}/'

    def test_user_get_detail(self):
        """Информацию о пользователе могут получить только авторизованные пользователи."""

        # GET-запрос на детальную информацию о пользователе
        response = self.client.get(
            self.user_detail_url,
            headers=self.headers_user_1,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        # Проверка email пользователя
        self.assertEqual(
            response.json().get('email'),
            'test@test.com'
        )

    def test_user_cannot_get_detail_without_authentication(self):
        """Анонимные пользователи не имеют доступа к информации веб-ресурса."""

        # GET-запрос на детальную информацию о пользователе
        response = self.client.get(
            self.user_detail_url,
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

    def test_user_get_limited_info_about_another_user(self):
        """Пользователи не имеют доступа к информации других пользователей."""

        # GET-запрос на детальную информацию о пользователе
        response = self.client.get(
            self.user_detail_url,
            headers=self.headers_user_2,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        # Проверка содержимого ответа
        self.assertEqual(
            response.json(),
            {'detail': 'Страница не найдена.'}
        )

    def test_user_update_profile_without_authentication(self):
        """Анонимные пользователи не могут изменять информацию о зарегистрированных пользователях."""

        # Данные для обновления
        updated_data = {
            'first_name': 'Dima',
            'last_name': 'Dmitriev'
        }

        # PATCH-запрос на изменение данных о пользователе
        response = self.client.patch(
            self.user_update_url,
            data=updated_data,
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

    def test_user_update_profile_with_authentication(self):
        """Авторизованные пользователи могут изменять информацию о себе."""

        # Данные для обновления
        updated_data = {
            'first_name': 'Dima',
            'last_name': 'Dmitriev'
        }

        # PATCH-запрос на изменение данных о пользователе
        response = self.client.patch(
            self.user_update_url,
            data=updated_data,
            headers=self.headers_user_1,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        # Проверка содержимого ответа
        user_data = {
            'first_name': response.json().get('first_name'),
            'last_name': response.json().get('last_name')
        }
        self.assertEqual(
            user_data,
            updated_data
        )

    def test_user_cannot_update_profile_about_another_user(self):
        """Пользователи не могут изменять данные других пользователей."""

        # Данные для обновления
        updated_data = {
            'first_name': 'Dima',
            'last_name': 'Dmitriev'
        }

        # PATCH-запрос на изменение данных о пользователе
        response = self.client.patch(
            self.user_update_url,
            data=updated_data,
            headers=self.headers_user_2,
            format='json'
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        # Проверка содержимого ответа
        self.assertEqual(
            response.json(),
            {'detail': 'Страница не найдена.'}
        )

    def test_user_can_delete_their_account(self):
        """Обычные пользователи могут удалять свои аккаунты."""

        password = {
            'current_password': 'ChooseBestPassword'
        }

        # Количество пользователей до удаления
        self.assertTrue(
            User.objects.count() == 2
        )

        # DELETE-запрос на удаление пользователя
        response = self.client.delete(
            self.user_delete_url,
            data=password,
            headers=self.headers_user_1,
            format='json'
        )

        # Количество пользователей после удаления
        self.assertTrue(
            User.objects.count() == 1
        )

        # Проверка статус кода
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

    def test_user_cannot_delete_account_not_owner(self):
        """Обычные пользователи не могут удалять чужие аккаунты."""

        password = {
            'current_password': 'ChooseBestPassword'
        }

        # Количество пользователей до удаления
        self.assertTrue(
            User.objects.count() == 2
        )

        # DELETE-запрос на удаление пользователя
        response = self.client.delete(
            self.user_delete_url,
            data=password,
            headers=self.headers_user_2,
            format='json'
        )

        # Количество пользователей после удаления
        self.assertTrue(
            User.objects.count() == 2
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
