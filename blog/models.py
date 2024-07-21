from django.db import models
from django.utils import timezone
# Фреймворк аутентификации
from django.contrib.auth.models import User
# Ищет URL заданного ресурса
from django.urls import reverse


class PublishedManager(models.Manager):
    """Извлечение постов со статусом PUBLISHED"""

    def qet_queryset(self):
        return super().qet_queryset() \
            .filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    """Хранит посты блога в БД"""

    class Status(models.TextChoices):
        """Определяет варианты поста: черновик и опубликован"""
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    # slug - короткая метка
    slug = models.SlugField(max_length=250,
                            unique_for_date='publish')
    # related_name - имя обратной связи от User к Post.
    # Можно обратиться через user.blog_posts
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    # auto_now_add - автосохранение даты во время создания поста
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    # Поле статуса поста
    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)
    # Менеджер по умолчанию
    objects = models.Manager()
    # Конкретно-прикладной менеджер
    published = PublishedManager()

    class Meta:
        # Сортировка постов от новых к старым
        ordering = ['-publish']
        # Индексы - как содержание книги. Они группируют категории
        # и ускоряют доступ к отдельным элементам
        indexes = [
            models.Index(fields=['-publish'])
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # blog: post_detail - ссылка на URL детальной информации о посте
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])



