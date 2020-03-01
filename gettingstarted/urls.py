from django.urls import path, include

from django.contrib import admin

admin.autodiscover()

import hello.views

urlpatterns = [
    path("build/<kitinput>/", hello.views.buildKit, name="kitinput"),
    path("", hello.views.selectKit, name="index"),
]
