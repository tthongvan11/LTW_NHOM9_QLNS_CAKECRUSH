"""Public starting page for the project skeleton."""
from django.shortcuts import render


def home(request):
    return render(request, "core/home.html")
