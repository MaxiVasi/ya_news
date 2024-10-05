# В файле test_content.py:
# + Количество новостей на главной странице — не более 10.
# + Новости отсортированы от самой свежей к самой старой.
# + Свежие новости в начале списка.
# + Комментарии на странице отдельной новости отсортированы
# + в хронологическом порядке: старые в начале списка, новые — в конце.
# + Анонимному пользователю недоступна форма для отправки
# комментария на странице отдельной новости, а авторизованному доступна.

import pytest
from django.urls import reverse

from news.forms import CommentForm
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('news_multiple')
def test_news_count_on_home_page(client, home_url):
    """Проверяем, что на странице Home не более 10 новостей."""
    response = client.get(home_url)
    news_count = response.context['object_list'].count()
    assert news_count == NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('news_multiple')
def test_news_sorting_on_home_page(client):
    """Проверка сортировки новостей по дате создания на главной странице."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
@pytest.mark.usefixtures('comment_multiple')
def test_comments_sorting_on_news_page(author_client, news_one):
    """Проверка сортировки комментариев по дате создания."""
    url = reverse('news:detail', args=(news_one.pk,))
    response = author_client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_one):
    url = reverse('news:detail', args=(news_one.pk,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_author_has_form_for_comment(author_client, news_one):
    url = reverse('news:detail', args=(news_one.pk,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
