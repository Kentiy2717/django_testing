from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()
SLUG = 'note-slug'
HOME_URL = reverse('notes:home')
EDIT_URL = reverse('notes:edit', args=(SLUG,))
DELETE_URL = reverse('notes:delete', args=(SLUG,))
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')


class TestContent(TestCase):

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
            slug=SLUG,
            author=cls.author,
        )

    def test_notes_list_for_author(self):
        """
        Тест - отдельная заметка
        передаётся на страницу со списком заметок
        в списке 'object_list' в словаре 'context'.
        """
        response = self.author_client.get(LIST_URL)
        object_list = response.context['object_list']
        note_count = object_list.count()
        self.assertEqual(note_count, 1)
        self.assertIn(self.note, object_list)
        note = object_list[0]
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)

    def test_notes_list_for_not_author(self):
        """
        Тест - в список заметок одного пользователя не попадают
        заметки другого пользователя.
        """
        response = self.not_author_client.get(LIST_URL)
        object_list = response.context['object_list']
        note_count = object_list.count()
        self.assertEqual(note_count, 0)

    def test_pages_contains_form(self):
        """
        Тест - на страницы создания и редактирования заметки
        передаются формы.
        """
        urls = (EDIT_URL, ADD_URL)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
