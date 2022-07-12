from cmath import log
from django.shortcuts import redirect, render
from . import util
import markdown
import requests
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
import random

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
        })


def entry(request, title):
    entry_page = util.get_entry(title)
    if entry_page == None:
        return render(request, "encyclopedia/nonexistent_entry.html", {
            "title": title
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": markdown.markdown(entry_page)
        })

def random_page(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return redirect('entry', title=random_entry)






   