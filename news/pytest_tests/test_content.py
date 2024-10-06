# В файле test_content.py:
# + Количество новостей на главной странице — не более 10.
# + Новости отсортированы от самой свежей к самой старой.
# + Свежие новости в начале списка.
# + Комментарии на странице отдельной новости отсортированы
# + в хронологическом порядке: старые в начале списка, новые — в конце.
# + Анонимному пользователю недоступна форма для отправки
# комментария на странице отдельной новости, а авторизованному доступна.

import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.usefixtures('news_multiple')
def test_news_count_on_home_page(client, home_url):
    response = client.get(home_url)
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('news_multiple')
def test_news_sorting_on_home_page(client):
    """Проверка сортировки новостей по дате создания на главной странице."""
    url = reverse('news:home')
    response = client.get(url)
    all_dates = [news.date for news in response.context['object_list']]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.usefixtures('comment_multiple')
def test_comments_sorting_on_news_page(author_client, detail_url, news_one):
    """Проверка сортировки комментариев по дате создания."""
    response = author_client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_author_has_form_for_comment(author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
