from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_for_all_tests(db):
    """Все тесты используют базу."""


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
def news_one():
    news = News.objects.create(
        title='Новость',
        text='Просто текст новости')
    return news


@pytest.fixture
def news_multiple():
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст новости',
            date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1))


@pytest.fixture
def comment(news_one, author):
    comment = Comment.objects.create(
        news=news_one,
        text='Текст комментария',
        author=author,
    )
    return comment


@pytest.fixture
def comment_multiple(news_one, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news_one,
            text=f'Tекст {index}',
            author=author,)
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def home_url():
    return reverse('news:home')


@pytest.fixture
def user_login_url():
    return reverse('users:login')


@pytest.fixture
def user_logout_url():
    return reverse('users:logout')


@pytest.fixture
def user_signup_url():
    return reverse('users:signup')


@pytest.fixture
def detail_url(news_one):
    return reverse('news:detail', args=(news_one.pk,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))
