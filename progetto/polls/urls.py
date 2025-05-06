from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home", views.home, name="home"),
    path("info", views.info, name="info"),
    path("testi", views.testi, name="testi"),
    path("correzioni", views.correzioni, name="correzioni"),
    path("suggerimenti", views.suggerimenti, name="suggerimenti"),
    path("inserisci_file", views.inserisci_file, name="inserisci_file"),
    path("testi_vari", views.testi_vari, name="testi_vari")
]