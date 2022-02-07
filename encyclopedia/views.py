from ast import arg
from cProfile import label
from logging import PlaceHolder
from pydoc import resolve
from django.shortcuts import render
from markdown2 import Markdown
from . import util
from django import forms
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
import random
# class for search form
class SearchForm(forms.Form):
    keyword = forms.CharField(label=False,widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia'}))

# create form
class CreateForm(forms.Form):
    title = forms.CharField(label="Title")
    content = forms.CharField(label="Markdown Content",widget=forms.Textarea)

# Edit Form
class EditForm(forms.Form):
    content = forms.CharField(label="Content", widget=forms.Textarea)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "searchForm":SearchForm()
    })

def getEntry(request, title):
    entry = util.get_entry(title)
    if entry != None:
        md = Markdown()
        html_entry = md.convert(entry)
        return render(request,"encyclopedia/entry.html",{
        "title":title,
        "entry":html_entry,
        "searchForm":SearchForm()
        })
    else:
        return render(request, "encyclopedia/err.html",{
            "msg":"The entry you're looking not found!"
        })

def search(request):
    searchValue = ''
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            searchValue = form.cleaned_data["keyword"]
            entry = util.get_entry(searchValue)
            if entry != None:
                return redirect(reverse('encyclopedia:getEntry', args=[searchValue]))
            else:
                # search using like
                results = util.like_search(searchValue)
                return render(request,"encyclopedia/search_results.html",{
                    "tile":searchValue,
                    "results":results,
                    "searchForm":SearchForm()
                })
        # end of vaidation

    else:
        return redirect(reverse('encyclopedia:index'))

def create(request):
    if request.method == 'POST':
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            # check if entry already exists
            if util.get_entry(title):
                messages.error(request,"The page is already exists in the system!, try another title!")
                return render(request, "encyclopedia/create.html", {
                    "createForm": form,
                    "searchForm": SearchForm()
            })
            else:
                util.save_entry(title, content)
                messages.success(request, f'The page "{title}" created successfully')
                return redirect(reverse('encyclopedia:getEntry', args=[title]))
        else:
            messages.error(request,"Invalid inputs!, Try again")
            return render(request,"encyclopedia/create.html",{
                "title":"Create New Page",
                "createForm":form,
                "searchForm":SearchForm()
            })
    else:
        return render(request,"encyclopedia/create.html",{
                "title":"Create New Page",
                "createForm":CreateForm(),
                "searchForm":SearchForm()
            })

def edit(request, title):
    print(f'title is {title}')
    if request.method == 'POST':
        form = EditForm(request.POST)
        if form.is_valid():
            content=form.cleaned_data['content']
            # save
            util.save_entry(title,content)
            messages.success(request, 'The page updated successfully!')
            return redirect(reverse('encyclopedia:getEntry',args=[title]))
        else:
            messages.error(request,"Invalid inputs!, Try again")
            return render(request,"encyclopedia/edit.html",{
                "title":"EditPage",
                "editForm":form,
                "searchForm":SearchForm() 
            })
    if request.method == 'GET':
        # get default value to show
        entry=util.get_entry(title)
        if entry == None:
            messages.error(request, "The page doesn't exists!")
            return redirect(reverse('encyclopedia:getEntry',args=[title]))
        return render(request,"encyclopedia/edit.html",{
                "title":title,
                "editForm":EditForm(initial={'content':entry}),
                "searchForm":SearchForm()
            })

def random_entry(request):
    entries = util.list_entries()
    entry = random.choice(entries)
    return redirect(reverse('encyclopedia:getEntry',args=[entry]))