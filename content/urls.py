from django.urls import path
from . import views


urlpatterns = [
    path('login', views.login),
    path('content', views.main),
    path('logout', views.logout),
    path("base_msg", views.base_msg),
    path("change_pwd", views.change_pwd),
    path("change_user", views.change_user),

    path("network/local_msg", views.local_msg),
    path("network/ping", views.ping),
    path("network/tcp_port", views.tcp_port),
    path("network/arp_table", views.arp_table),
    path("network/packet_capture", views.packet_capture),
    path("network/download_packet", views.download_packet),
    path("network/download_packet_del", views.download_packet_del),


    path("arp/local_area_network", views.local_area_network),
    path("arp/arp_cheat", views.arp_cheat),


    path("demo", views.demo),
    path("main", views.main),
    path("", views.main),
]
