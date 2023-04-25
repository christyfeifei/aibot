from django.shortcuts import render, HttpResponse

# Create your views here.


def index(request):
    return HttpResponse("<h1>您好，我是AI機器人</h1>")
