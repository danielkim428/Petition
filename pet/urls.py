from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("petitions/<int:post_id>", views.post, name='post'),
    path("petitions/<int:post_id>/remove", views.remove, name='remove'),
    path("petitions/<int:post_id>/sign", views.sign, name="sign"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("about", views.about, name="about"),
    path("new", views.new, name="new"),
    path("account/details", views.account, name="account"),
    path("account/signed", views.signed, name="signed"),
    path("account/mypetition", views.mypetition, name="mypetitions"),
    path("account/changeaccount", views.changeaccount, name="changeaccount"),
    path("init", views.init, name="init"),
    path("stuco", views.stuco, name="stuco"),
    path("stuco/ajax_stuco", views.ajax_stuco, name="ajax_stuco"),
    path("stuco/loadmore", views.loadmore, name="loadmore"),
    path("stuco/disloadmore", views.disloadmore, name="disloadmore"),
    path("indexPage", views.indexPage, name="indexPage"),
    path("closed", views.closed, name="closed"),
    path("answered", views.answered, name="answered"),
]
