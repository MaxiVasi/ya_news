import pytest

from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from datetime import datetime, timedelta

from news.models import Comment, News

NEWS_COUNT_ON_HOME_PAGE = 10
NEW_COMMENT_TEXT = 'Совсем новый текст комментария'


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
    news = News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст новости',
            date=today - timedelta(days=index))
        for index in range(NEWS_COUNT_ON_HOME_PAGE + 1))
    return news


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
    return comment


@pytest.fixture
def pk_for_one_news(news_one):
    return (news_one.pk,)


@pytest.fixture
def pk_comment(comment):
    return (comment.pk,)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст комментария',
    }


@pytest.fixture
def detail_url(news_one):
    return reverse('news:detail', args=(news_one.pk,))


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.pk,))
