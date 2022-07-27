from cmath import log
from multiprocessing.sharedctypes import Value
from re import template
import re
from turtle import title
from django.shortcuts import redirect, render
from . import util
import markdown
import requests
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
import random
from django.contrib import messages

# create forms
class NewEntryForm(forms.Form):
    title = forms.CharField(label="", widget=forms.TextInput(attrs={'size': '50', "placeholder": "Title"}),)
    content = forms.CharField(label="", widget=forms.Textarea(attrs={"placeholder": "Body of Content in Markdown"}),)

class EditExistingForm(forms.Form):
    content = forms.CharField(label="", widget=forms.Textarea())

# main page
# supply context of list entries
def index(request):
    if "content" not in request.session:
        request.session["content"]= []
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        })

# entry page 
def entry(request, title):
    entry_page = util.get_entry(title)
    
    # if entry page does not exist, take to non-existent page
    if entry_page == None:
        return render(request, "encyclopedia/nonexistent_entry.html", {
            "title": title
        })
    
    # else render entry page
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": markdown.markdown(entry_page)
        })

# get list of entries and choose randomly
def random_page(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return redirect("entry", title=random_entry)

# search through list of entries
def search(request):
    search_query = request.GET.get("q","")
    entries = util.list_entries()
    for elem in entries:
        if search_query.lower() == elem.lower():
            return redirect("entry", title=search_query)
    
    # initialize empty list to match list elem with entry list elem
    search_query_match_substring = []
    for elem in entries:
        if search_query.lower() in elem.lower():
            search_query_match_substring.append(elem)
        elif search_query.lower() in elem.lower():
            search_query_match_substring = []
    return render(request, "encyclopedia/substring_search.html", {
    "search_query_match_substring":search_query_match_substring,
    "search_query": search_query
    })

# create new list elem
def create(request):
    
    # using session data to pass around context/body
    if "content" not in request.session:
        request.session["content"]= []
        
    # post to django
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        
        # preparing variables to check if title already exists inside entry list elem
        if form.is_valid():
            title=request.POST.get('title')
            content=request.POST.get('content')
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            request.session["content"] += content
            entries =  util.list_entries()
            for elem in entries:
                
                # if already exist, redirect with same title and do not edit data
                if title.lower() in elem.lower():
                    messages.add_message(request, messages.INFO, 'Error! You entered a duplicate. Item already found in index. No new entry was created')
                    return redirect("entry", title=title)
            for elem in entries:
                
                #if item not in entry list elem, append new title posted and render new page
                if title.lower() not in elem.lower():
                    entries.append(title)
                    entries = util.save_entry(title, f'# {title}\n\n{content}')
                    return render(request, "encyclopedia/index.html", {
                        "entries": util.list_entries(),
                        "content": request.session["content"]
                    })
        else:
            return render(request, "encyclopedia/create_new.html", {
                "form": form
            })
    return render(request, "encyclopedia/create_new.html", {
        "form": NewEntryForm()
    })

# to edit existing entry list elem
def edit(request, title):
    if request.method == "GET":
        request.session["content"] = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "title": title, 
            "content": request.session["content"]})
    if request.method == "POST":
        content = request.POST.get("content")
        util.save_entry(title, content)
        return redirect("entry", title)
