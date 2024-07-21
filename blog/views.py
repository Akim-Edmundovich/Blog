from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator


def post_list(request):
    post_list = Post.published.all()
    # Постраничная разбивка с 3 постами на страницу
    paginator = Paginator(post_list, 2)
    # Содержит запрошенный номер страницы.
    # Если page нет в GET-параметрах запроса, то загрузит 1-ю страницу
    page_number = request.GET.get('page', 1)
    # Получаем объекты для желаемой страницы и сохраняем в posts
    posts = paginator.page(page_number)
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts})


def post_detail(request, year, month, day, post):
    """Детальная информация о посте"""
    # Извлекает объект с параметрами или выдает 404
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request,
                  'blog/post/detail.html',
                  {'post': post})
