from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from .forms import PostForm

POSTS_PER_PAGE = 10


def authorized_only(func):
    def check_user(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        return redirect('/auth/login/')
    return check_user


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    title = group.title
    description = group.description
    template = 'posts/group_list.html'
    # posts = group.posts.all().order_by('-pub_date')[:POSTS_PER_PAGE]
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
        'description': description,
    }
    return render(
        request,
        template,
        context,
    )


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(
        request,
        template,
        context
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.author_posts.all().order_by('-pub_date')
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Профайл пользователя'
    context = {
        'title': title,
        'page_obj': page_obj,
        'author': author,
        'posts_count': post_list.count(),
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    context = {
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


@authorized_only
def post_create(request):
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.text = form.cleaned_data['text']
            post.save()
            return redirect('posts:profile', request.user)
        return render(
            request,
            template,
            {'form': form},
        )
    form = PostForm()
    form.fields['text'].required = True
    return render(
        request,
        template,
        {'form': form},
    )


@authorized_only
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    is_edit = True
    post = get_object_or_404(Post, id=post_id)
    groups = Group.objects.all()
    form = PostForm(instance=post)
    form.fields['text'].required = True
    context = {
        'form': form,
        'is_edit': is_edit,
        'post_id': post_id,
        'groups': groups,
    }
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.text = form.cleaned_data['text']
            post.group = form.cleaned_data['group']
            post.save()
            return redirect('posts:post_detail', post_id)
        return render(
            request,
            template,
            context,
        )
    return render(
        request,
        template,
        context,
    )
