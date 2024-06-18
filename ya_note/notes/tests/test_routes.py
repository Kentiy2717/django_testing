from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()
SLUG = 'note-slug'
HOME_URL = reverse('notes:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
DETAIL_URL = reverse('notes:detail', args=(SLUG,))
EDIT_URL = reverse('notes:edit', args=(SLUG,))
DELETE_URL = reverse('notes:delete', args=(SLUG,))
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
DONE_URL = reverse('notes:success')


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
        cls.urls = (
            HOME_URL,
            LOGIN_URL,
            SIGNUP_URL,
            DETAIL_URL,
            EDIT_URL,
            LIST_URL,
            ADD_URL,
            DONE_URL,
            DELETE_URL,
            LOGOUT_URL,
        )

    def test_pages_availability_for_anonymous_user(self):
        """
        Тест - доступность страниц и редирект для анонимного пользователя.
        """
        url_for_anonymous_user = (
            HOME_URL,
            LOGIN_URL,
            SIGNUP_URL,
            LOGOUT_URL,
        )
        for url in self.urls:
            response = self.client.get(url)
            with self.subTest(url=url):
                if url in url_for_anonymous_user:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    expected_url = f'{LOGIN_URL}?next={url}'
                    self.assertRedirects(response, expected_url)

    def test_pages_availability_for_author(self):
        """Тест - доступность всех страниц для автора."""
        for url in self.urls:
            response = self.author_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Тест - доступность страниц для авторизованного пользователя."""
        url_for_auth_user = (
            HOME_URL,
            LOGIN_URL,
            SIGNUP_URL,
            LIST_URL,
            ADD_URL,
            DONE_URL,
            LOGOUT_URL,
        )
        for url in self.urls:
            response = self.not_author_client.get(url)
            with self.subTest(url=url):
                if url in url_for_auth_user:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(
                        response.status_code, HTTPStatus.NOT_FOUND
                    )
