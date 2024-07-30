from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
# Общее кол-во об-тов
from django.db.models import Count
from django.contrib.postgres.search import TrigramSimilarity


class PostListView(ListView):
    """Альтернативное представление списка постов"""
    # В запросе будут все посты
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 5
    template_name = 'blog/post/list.html'


def post_list(request, tag_slug=None):
    """
    Список постов с тегами
    """
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        # Извлекаются все посты со слагом данного тега
        tag = get_object_or_404(Tag, slug=tag_slug)
        # Фильтр
        post_list = post_list.filter(tags__in=[tag])
    # Постраничная разбивка с 5 постами на страницу
    paginator = Paginator(post_list, 5)
    # Содержит запрошенный номер страницы.
    # Если page нет в GET-параметрах запроса, то загрузит 1-ю страницу
    page_number = request.GET.get('page', 1)
    try:
        # Получаем объекты для желаемой страницы и сохраняем в posts
        posts = paginator.page(page_number)

    except PageNotAnInteger:
        # Если page_number не целое число,
        # то выдать первую страницу
        posts = paginator.page(1)
    except EmptyPage:
        # Если страницы не существует
        # показать последнюю страницу (общее число страниц)
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts,
                   'tag': tag})


def post_detail(request, year, month, day, post):
    """Детальная информация о посте"""
    # Извлекает объект с параметрами или выдает 404
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)

    # Извлечение всех активных комментов (набор QuerySet)
    comments = post.comments.filter(active=True)

    # Форма для комментирования пользователями
    form = CommentForm()

    # Список схожих постов. flat=True - [1, 2, 3..], а не [(1,), (2,)...]
    post_tags_ids = post.tags.values_list('id', flat=True)

    # Взять все посты с этими тегами, исключая текущий пост
    similar_posts = Post.published.filter(tags__in=post_tags_ids) \
        .exclude(id=post.id)

    # Count - генерирует число общих тегов со всеми запрошенными
    similar_posts = similar_posts.annotate(same_tags=Count('tags')) \
                        .order_by('-same_tags', '-publish')[:4]

    # Вернет шаблон с указанными полями
    return render(request,
                  'blog/post/detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts': similar_posts})


def post_share(request, post_id):
    # Извлечь пост по идентификатору
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        # Форма передана обработку
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля формы успешно прошли валидацию
            cd = form.cleaned_data
            # Ссылка на пост вставится в электронное письмо
            # URI - в HTML, XML и других файлах
            # URL - в веб-страницах
            post_url = request.build_absolute_uri(
                # Формируем полный URL-адрес
                post.get_absolute_url())
            subject = (f"{cd['name']} recommends you read "
                       f"{post.title}")
            message = (f"Read \"{post.title}\" at {post_url}\n\n"
                       f"{cd['name']}\'s comments: {cd['comments']}")
            send_mail(subject, message, 'monstrillo6gigov@gmail.com',
                      [cd['to']])
            # После отправки меняем на True
            sent = True

    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


@require_POST
def post_comment(request, post_id):
    # Извлекается опубликованный пост
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    # Переменная для хранения комментария при его создании
    comment = None
    # Комментарий был отправлен
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Создать объект класса Comment, не сохраняя его в БД - commit=False
        comment = form.save(commit=False)
        # Назначить пост комментарию
        comment.post = post
        # Сохранить коммент в БД
        comment.save()

    return render(request, 'blog/post/comment.html',
                  {'post': post,
                   'form': form,
                   'comment': comment}, )


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    # Если запрос в словаре request.GET
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']

            results = Post.published.annotate(
                similarity=TrigramSimilarity('title', query),
            ).filter(similarity__gt=0.1).order_by('-similarity')

    return render(request,
                  'blog/post/search.html',
                  {'form': form,
                   'query': query,
                   'results': results})
