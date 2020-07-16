from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("petitions/<int:post_id>", views.post, name='post'),
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
]
