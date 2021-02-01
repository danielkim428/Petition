from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.core import serializers
import json

# Create your views here
from .models import *

def stuco(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('index'))
    context = {
        "user": request.user,
        "yet": Post.objects.filter(state=0).annotate(num_supporters=Count('supporters')).order_by('-id'),
        "answered": Post.objects.filter(state=3).annotate(num_supporters=Count('supporters')).order_by('-id'),
        "disapproved": Post.objects.filter(state=6).annotate(num_supporters=Count('supporters')).order_by('-id'),
    }
    if request.method == 'POST':
        id = request.POST['id']
        stuco = request.user
        post = Post.objects.get(pk=id)
        state = request.POST['state']
        try:
            post.state = state
            post.stuco = stuco
            post.save()
        except:
            return render(request, 'petition/stuco.html', {"message": "Please try it again"})
        return render(request, "petition/stuco.html", context)
    else:
        return render(request, "petition/stuco.html", context)

def init(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    try:
        exist = Supporter.objects.get(user=request.user)
        return HttpResponseRedirect(reverse('index'))
    except:
        if (request.user.email.split("@")[1] == "woodstock.ac.in"):
            new_supporter = Supporter(user=request.user)
            new_supporter.save()
            return HttpResponseRedirect(reverse('index'))
        return render(request, 'petition/login.html', {"message": "Please sign in with your school account."})

def about(request):
    return render(request, "petition/about.html")

def account(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    context = {
        "user": request.user,
    }
    return render(request, "petition/account.html", context)

def signed(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    supporterid = Supporter.objects.get(user=request.user).id

    context = {
        "user": request.user,
        "signed": Post.objects.annotate(num_supporters=Count('supporters')).filter(supporters=supporterid),
    }
    return render(request, "petition/signed.html", context)

def mypetition(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    context = {
        "user": request.user,
        "mypetitions": Post.objects.filter(author=request.user).annotate(num_supporters=Count('supporters')),
    }
    return render(request, "petition/mypetition.html", context)

def index(request):
    pageSize = 5
    numPosts = Post.objects.filter(state=1).all().count()
    page = int((numPosts+pageSize-1)/pageSize)
    top = Post.objects.filter(state=1).annotate(num_supporters=Count('supporters')).order_by('-num_supporters')[:5]
    if not request.user.is_authenticated:
        context = {
            "page": range(1, page+1),
            "posts": Post.objects.filter(state=1).annotate(num_supporters=Count('supporters')).order_by('-id')[:pageSize],
            "top": top,
        }
        return render(request, "petition/index.html", context)
    context = {
        "page": range(1, page+1),
        "user": request.user,
        "posts": Post.objects.filter(state=1).annotate(num_supporters=Count('supporters')).order_by('-id')[:pageSize],
        "top": top,
    }
    return render(request, "petition/index.html", context)

def closed(request):
    if not request.user.is_authenticated:
        context = {
            "posts": Post.objects.filter(state=2).annotate(num_supporters=Count('supporters')).order_by('-num_supporters'),
        }
        return render(request, "petition/closed.html", context)
    context = {
        "user": request.user,
        "posts": Post.objects.filter(state=2).annotate(num_supporters=Count('supporters')).order_by('-num_supporters')
    }
    return render(request, "petition/closed.html", context)

def answered(request):
    if request.method == "POST":
        if request.user.is_staff:
            try:
                pk = request.POST['pk']
                content = request.POST['content']
                post = Post.objects.get(pk=pk)
                post.answer = content
                post.save()
                return HttpResponseRedirect(reverse('answered'))
            except:
                return render(request, "petition/error.html", {"message": "Something went wrong."})

    if not request.user.is_authenticated:
        context = {
            "posts": Post.objects.filter(state=3).annotate(num_supporters=Count('supporters')).order_by('-num_supporters'),
        }
        return render(request, "petition/answered.html", context)
    context = {
        "user": request.user,
        "posts": Post.objects.filter(state=3).annotate(num_supporters=Count('supporters')).order_by('-num_supporters')
    }
    return render(request, "petition/answered.html", context)

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('init'))

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('init'))
        else:
            return render(request, 'petition/login.html', {"message": "Invalid credentials."})
    else:
        return render(request, 'petition/login.html')

def logout_view(request):
    logout(request)
    return render(request, "petition/login.html", {"message": "Logged out."})

def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']

        try:
            new_user = User.objects.create_user(username, email, password)
            new_user.first_name = first_name
            new_user.last_name = last_name
            new_user.save()

        except IntegrityError:
            return render(request, 'petition/register.html', {"message": "User already exists"})
        except:
            return render(request, 'petition/register.html', {"message": "Invalid credentials."})

        return HttpResponseRedirect(reverse('login'))

    else:
        return render(request, 'petition/register.html')

def post(request, post_id):
    try:
        post = Post.objects.annotate(num_supporters=Count('supporters')).get(pk=post_id)
        comments = Comment.objects.filter(post=post).filter(parent_comment__isnull=True).all()
    except Post.DoesNotExist:
        raise Http404("Post does not exist")
    if ((post.state == 0) or (post.state == 6)):
        if not request.user.is_staff:
            return HttpResponseRedirect(reverse('index'))
    context = {
        "top": Post.objects.filter(state=1).annotate(num_supporters=Count('supporters')).order_by('-num_supporters'),
        "posts": Post.objects.filter(state=1).annotate(num_supporters=Count('supporters')).order_by('-id'),
        "post": post,
        "supporters": post.supporters.all(),
        "non_supporters": Supporter.objects.exclude(posts=post).all(),
        "comments": comments,
        "signed": "false"
    }
    supporter = Supporter.objects.get(user=request.user)
    if supporter in post.supporters.all():
        context = {
            "top": Post.objects.filter(state=1).annotate(num_supporters=Count('supporters')).order_by('-num_supporters'),
            "posts": Post.objects.filter(state=1).annotate(num_supporters=Count('supporters')).order_by('-id'),
            "post": post,
            "supporters": post.supporters.all(),
            "non_supporters": Supporter.objects.exclude(posts=post).all(),
            "comments": comments,
            "signed": "true"
        }
    if request.method == 'POST':
        type = request.POST['type']
        content = request.POST['content']
        if not content:
            context = {
                "post": post,
                "posts": posts,
                "comments": comments,
                "message": "Please fill in the content"
            }
            return render(request, 'petition/post.html', context)
        if type == "comment":
            try:
                new_comment = Comment(author=request.user, post=post, content=content)
                new_comment.save()
            except:
                context = {
                    "post": post,
                    "posts": posts,
                    "comments": comments,
                    "message": "Please try it again"
                }
                return render(request, 'petition/post.html', context)
        if type == "reply":
            try:
                parent = request.POST['parent']
                new_comment = Comment(author=request.user, post=post, content=content, parent_comment=Comment.objects.get(pk=parent))
                new_comment.save()
            except:
                context = {
                    "post": post,
                    "posts": posts,
                    "comments": comments,
                    "message": "Please try it again"
                }
                return render(request, 'petition/post.html', context)
        url = reverse('post', kwargs={'post_id': post_id})
        return HttpResponseRedirect(url)
    return render(request, "petition/post.html", context)

def remove(request, post_id):
    if (request.user.is_staff):
        if request.method == 'POST':
            try:
                id = request.POST['id']
                post = Post.objects.get(pk=id)
                post.state = 6
                post.save()
                return HttpResponseRedirect(reverse("post", args=(post_id,)))
            except:
                return render(request, 'petition/stuco.html', {"message": "Please try it again"})


def sign(request, post_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    try:
        post = Post.objects.get(pk=post_id)
        supporter = Supporter.objects.get(user=request.user)

    except KeyError:
        return render(request, "petition/error.html", {"message": "No selection."})
    except Post.DoesNotExist:
        return render(request, "petition/error.html", {"message": "No post."})
    except Supporter.DoesNotExist:
        return render(request, "petition/error.html", {"message": "No supporter."})

    if post.state == 1:
        supporter.posts.add(post)
    else:
        return render(request, "petition/error.html", {"message": "This petition is not open for signatures."})

    return HttpResponseRedirect(reverse("post", args=(post_id,)))

def changeaccount(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            change_user = User.objects.get(username=request.user.username)
            if not (username == request.user.username):
                change_user.username = username
            if not (password == ""):
                change_user.set_password(password)
            change_user.save()

        except IntegrityError:
            return render(request, 'petition/account.html', {"message": "Username already exists"})
        except:
            return render(request, 'petition/account.html', {"message": "Invalid credentials."})

    return HttpResponseRedirect(reverse('account'))

def new(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if request.method == 'POST':
        title = request.POST['title']
        category = request.POST['category']
        content = request.POST['content']
        if not title:
            return render(request, 'petition/new.html', {"message": "Please fill in the title"})

        if not category:
            return render(request, 'petition/new.html', {"message": "Please select the category"})

        if not content:
            return render(request, 'petition/new.html', {"message": "Please fill in the content"})

        try:
            new_post = Post(title=title, category=category, content=content, author=request.user, state=0)
            new_post.save()
        except:
            return render(request, 'petition/new.html', {"message": "Please try it again"})

        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, 'petition/new.html')

def ajax_stuco(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        id = request.headers.get('id')
        postid = Post.objects.get(pk=id)
        post = serializers.serialize('json', [ postid, ])
        name = ', "firstname": "'+postid.author.first_name+'", "lastname": "'+postid.author.last_name+'"}}]'
        post = post.split("}}]")[0]+name

        data = {
                'post': post,
        }
        return JsonResponse(data)

def loadmore(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        perPage = 5
        show = int(request.headers.get('show'))
        show = show*perPage+perPage
        posts = Post.objects.filter(state=0).order_by('-id')[show-perPage:show]
        list = []
        for post in posts:
            name = ', "firstname": "'+post.author.first_name+'", "lastname": "'+post.author.last_name+'"}}]'
            post = serializers.serialize('json', [ post, ])
            post = post.split("}}]")[0]+name
            list.append(post)
        data = {
            'show': list,
        }
        return JsonResponse(data)

def disloadmore(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        perPage = 2
        show = int(request.headers.get('show'))
        show = show*perPage+perPage
        posts = Post.objects.filter(state=6).order_by('-id')[show-perPage:show]
        list = []
        for post in posts:
            name = ', "firstname": "'+post.author.first_name+'", "lastname": "'+post.author.last_name+'"}}]'
            post = serializers.serialize('json', [ post, ])
            post = post.split("}}]")[0]+name
            list.append(post)
        data = {
            'show': list,
        }
        return JsonResponse(data)

def indexPage(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        perPage = 5
        show = int(request.headers.get('page'))
        show = show*perPage
        posts = Post.objects.filter(state=1).annotate(num_supporters=Count('supporters')).order_by('-id')[show-perPage:show]
        list = []
        for post in posts:
            num_supporters = '"num": "'+str(post.num_supporters)+'", '
            post = serializers.serialize('json', [ post, ])
            post = post[:2]+num_supporters+post[2:]
            list.append(post)
        data = {
            'show': list,
        }
        return JsonResponse(data)
