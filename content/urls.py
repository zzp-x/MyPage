from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login),
    path('content/', views.content),
    path('logout/', views.logout),

]
