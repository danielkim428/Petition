from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Count
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

# Create your views here
from .models import *

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
    if not request.user.is_authenticated:
        context = {
            "posts": Post.objects.all().annotate(num_supporters=Count('supporters')).order_by('-id'),
        }
        return render(request, "petition/index.html", context)
    context = {
        "user": request.user,
        "posts": Post.objects.all().annotate(num_supporters=Count('supporters')).order_by('-id'),
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
  context = {
      "posts": Post.objects.all().annotate(num_supporters=Count('supporters')).order_by('-id'),
      "post": post,
      "supporters": post.supporters.all(),
      "non_supporters": Supporter.objects.exclude(posts=post).all(),
  }
  return render(request, "petition/post.html", context)

def sign(request, post_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    supporterid = Supporter.objects.get(first_name=request.user.first_name).id
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
        if not title:
            return render(request, 'petition/new.html', {"message": "Please fill in the title"})
        
        if not category:
            return render(request, 'petition/new.html', {"message": "Please select the category"})

        if not content:
            return render(request, 'petition/new.html', {"message": "Please fill in the content"})

        try:
            new_post = Post(title=title, category=category, content=content, authorFirst=first, authorLast=last)
            new_post.save() 
        except:
            return render(request, 'petition/new.html', {"message": "Please try it again"})

        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, 'petition/new.html')