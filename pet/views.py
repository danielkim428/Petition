from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.core import serializers

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
        stuco = request.POST['stuco']
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
        exist = Supporter.objects.get(first_name=request.user.first_name, last_name=request.user.last_name)
        return HttpResponseRedirect(reverse('index'))
    except:
        if (request.user.email.split("@")[1] == "woodstock.ac.in"):
            new_supporter = Supporter(first_name=request.user.first_name, last_name=request.user.last_name)
            new_supporter.save()
            return HttpResponseRedirect(reverse('index'))
        return render(request, 'petition/login.html', {"message": "Please sign in with your woodstock account."})

def about(request):
    return render(request, "petition/about.html")

def account(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    supporterid = Supporter.objects.get(first_name=request.user.first_name).id
    supporterFirst = Supporter.objects.get(first_name=request.user.first_name).first_name

    context = {
        "user": request.user,
        "signed": Post.objects.annotate(num_supporters=Count('supporters')).filter(supporters=supporterid),
        "mypetitions": Post.objects.filter(authorFirst=supporterFirst).annotate(num_supporters=Count('supporters')),
    }
    return render(request, "petition/account.html", context)

def signed (request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    supporterid = Supporter.objects.get(first_name=request.user.first_name).id

    context = {
        "user": request.user,
        "signed": Post.objects.annotate(num_supporters=Count('supporters')).filter(supporters=supporterid),
    }
    return render(request, "petition/signed.html", context)

def mypetition (request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    supporterFirst = Supporter.objects.get(first_name=request.user.first_name).first_name

    context = {
        "user": request.user,
        "mypetitions": Post.objects.filter(authorFirst=supporterFirst).annotate(num_supporters=Count('supporters')),
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

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
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

            new_supporter = Supporter(first_name=first_name, last_name=last_name)
            new_supporter.save()

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
  except Post.DoesNotExist:
      raise Http404("Post does not exist")
  if ((post.state == 0) or (post.state == 6)):
      if not request.user.is_staff:
          return HttpResponseRedirect(reverse('index'))
  if (request.user.is_staff):
      if request.method == 'POST':
          id = request.POST['id']
          post = Post.objects.get(pk=id)
          try:
              post.state = 6
              post.save()
          except:
              return render(request, 'petition/stuco.html', {"message": "Please try it again"})
  context = {
      "posts": Post.objects.all().annotate(num_supporters=Count('supporters')).order_by('-id'),
      "post": post,
      "supporters": post.supporters.all(),
      "non_supporters": Supporter.objects.exclude(posts=post).all(),
      "signed": "false"
  }
  supporter = Supporter.objects.get(first_name=request.user.first_name, last_name=request.user.last_name)
  if supporter in post.supporters.all():
      context = {
          "posts": Post.objects.all().annotate(num_supporters=Count('supporters')).order_by('-id'),
          "post": post,
          "supporters": post.supporters.all(),
          "non_supporters": Supporter.objects.exclude(posts=post).all(),
          "signed": "true"
      }
  return render(request, "petition/post.html", context)

def sign(request, post_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    supporterid = Supporter.objects.get(first_name=request.user.first_name, last_name=request.user.last_name).id
    try:
        supporter_id = supporterid
        post = Post.objects.get(pk=post_id)
        supporter = Supporter.objects.get(pk=supporter_id)

    except KeyError:
        return render(request, "petition/error.html", {"message": "No selection."})
    except Post.DoesNotExist:
        return render(request, "petition/error.html", {"message": "No post."})
    except Supporter.DoesNotExist:
        return render(request, "petition/error.html", {"message": "No supporter."})

    supporter.posts.add(post)
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
        first = request.POST['first']
        last = request.POST['last']
        title = request.POST['title']
        category = request.POST['category']
        content = request.POST['content']
        state = 0
        if not title:
            return render(request, 'petition/new.html', {"message": "Please fill in the title"})

        if not category:
            return render(request, 'petition/new.html', {"message": "Please select the category"})

        if not content:
            return render(request, 'petition/new.html', {"message": "Please fill in the content"})

        try:
            new_post = Post(title=title, category=category, content=content, authorFirst=first, authorLast=last, state=state)
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
            post = serializers.serialize('json', [ post, ])
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
            post = serializers.serialize('json', [ post, ])
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
