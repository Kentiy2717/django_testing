from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_notes_list_for_different_users(self):
        name = 'notes:list'
        users_statuses = (
            (self.author, True),
            (self.not_author, False),
        )
        for user, note_in_list in users_statuses:
            self.client.force_login(user)
            with self.subTest(name):
                url = reverse(name)
                response = self.client.get(url)
                object_list = response.context['object_list']
                assert (self.note in object_list) is note_in_list

    def test_pages_contains_form(self):
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None),
        )
        for name, args in urls:
            self.client.force_login(self.author)
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                assert 'form' in response.context
                assert isinstance(response.context['form'], NoteForm)
