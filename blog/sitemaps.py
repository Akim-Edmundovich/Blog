from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSitemap(Sitemap):
    # Частота изменения страниц постов
    changefreq = 'weekly'

    # Релевантность на сайте
    priority = 0.9

    def items(self):
        """Набор запросов для включения в карту сайта"""
        return Post.published.all()

    def lastmod(self, obj):
        """Время последнего изменения"""
        return obj.updated
