from datetime import datetime, timedelta
import pytest

from django.conf import settings
from django.test.client import Client
from django.utils import timezone
from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Новость',
        text='Просто текст.',
        date=datetime.today()
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def many_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comments(news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def id_for_args(news):
    return (news.id,)


@pytest.fixture
def form_data():
    return {'text': 'Новый текст комментария'}


@pytest.fixture
def detail_url(news):
    url = reverse('news:detail', args=(news.id,))
    return url


@pytest.fixture
def delete_url(comment):
    url = reverse('news:delete', args=(comment.id,))
    return url


@pytest.fixture
def edit_url(comment):
    url = reverse('news:edit', args=(comment.id,))
    return url
