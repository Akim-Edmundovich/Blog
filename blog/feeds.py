import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy
from .models import Post


class LatestPostsFeed(Feed):
    title = 'My blog'
    # Генерация URL-адресов по их имени и передача опциональных параметров
    link = reverse_lazy('blog:post_list')

    description = 'New posts of my blog.'

    def items(self):
        """Извлекает об-ты из новостной ленты"""
        return Post.published.all()[:5]

    def item_title(self, item):
        """Получает от items() заголовок"""
        return item.title

    def item_description(self, item):
        """Конвертация из MD to HTML;
        Сокращение до 30-и символов"""
        return truncatewords_html(markdown.markdown(item.body), 30)

    def item_pubdate(self, item):
        return item.publish
