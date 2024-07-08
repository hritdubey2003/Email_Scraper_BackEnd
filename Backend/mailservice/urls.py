from django.urls import path
from . import views 


urlpatterns = [
    path("ensure", views.ensure, name="ensure"),
    path("mail_scrap", views.mail_scrap, name="mail_scrap"),
    path("home", views.home, name="home"),
    path("download_email" , views.download_email , name="download_email")
]