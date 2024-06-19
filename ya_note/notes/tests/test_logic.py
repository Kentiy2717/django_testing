from pytils.translit import slugify
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()
SLUG = 'note-slug'
LOGIN_URL = reverse('users:login')
EDIT_URL = reverse('notes:edit', args=(SLUG,))
DELETE_URL = reverse('notes:delete', args=(SLUG,))
ADD_URL = reverse('notes:add')
DONE_URL = reverse('notes:success')


class TestLogicCreate(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        """Тест - авторизованный пользователь может создать заметку."""
        self.assertEqual(Note.objects.count(), 0)
        response = self.author_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, DONE_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Тест - анонимный пользователь не может создать заметку."""
        note_count = Note.objects.count()
        response = self.client.post(ADD_URL, data=self.form_data)
        expected_url = f'{LOGIN_URL}?next={ADD_URL}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), note_count)

    def test_empty_slug(self):
        """
        Тест - автосоздание 'slug',
        если он не был заполнен при создании заметки.
        """
        self.form_data.pop('slug')
        self.assertEqual(Note.objects.count(), 0)
        response = self.author_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, DONE_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.author, self.author)


class TestLogicEdit(TestCase):

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
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_not_unique_slug(self):
        """Тест - невозможно создать две заметки с одинаковым slug."""
        note_count_now = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(ADD_URL, data=self.form_data)
        self.assertFormError(response, 'form', 'slug', errors=(
            self.note.slug + WARNING
        ))
        self.assertEqual(Note.objects.count(), note_count_now)

    def test_author_can_edit_note(self):
        """Тест - автор может удалить свою заметку."""
        note_count_now = Note.objects.count()
        response = self.author_client.post(EDIT_URL, self.form_data)
        self.assertRedirects(response, DONE_URL)
        note_from_db = note = Note.objects.get()
        self.assertEqual(Note.objects.count(), note_count_now)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, note_from_db.author)

    def test_other_user_cant_edit_note(self):
        """Тест - пользователь не может редактировать чужие заметки."""
        note_count_now = Note.objects.count()
        response = self.not_author_client.post(EDIT_URL, self.form_data)
        self.assertEqual(Note.objects.count(), note_count_now)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get()
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, note_from_db.author)

    def test_author_can_delete_note(self):
        """Тест - автор может удалить свою заметку."""
        note_count_now = Note.objects.count()
        response = self.author_client.post(DELETE_URL)
        self.assertRedirects(response, DONE_URL)
        self.assertEqual(note_count_now - 1, Note.objects.count())

    def test_other_user_cant_delete_note(self):
        """Тест - пользователь не может удалить чужую заметку."""
        note_count = Note.objects.count()
        response = self.not_author_client.post(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), note_count)
