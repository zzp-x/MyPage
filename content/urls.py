from django.urls import path
from . import views


urlpatterns = [
    path('login', views.login),
    path('main', views.main),
    path('logout', views.logout),
    path("base_msg", views.base_msg),
    path("change_pwd", views.change_pwd),

]
