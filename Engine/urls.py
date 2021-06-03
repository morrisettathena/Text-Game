from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("game/<str:game_name>", views.game, name="game"),
    path("newgame", views.newgame, name="newgame"),
    path("move", views.move, name="move"),
    path("loginerror", views.loginerror, name="loginerror"),
    path("respond", views.respond, name="respond"),
    path("continuegame", views.continuegame, name="continuegame"),
    path("updatelikes", views.updatelikes, name="updatelikes"),
]