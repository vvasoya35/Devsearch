from multiprocessing import context
import profile
from pydoc import describe
from turtle import title
from unicodedata import name
from django.shortcuts import redirect, render
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import ProjectForm, ReviewForm
from .utils import *

def projects(request):
    projects, search_query = searchProjects(request)
    custom_range, projects = paginateProjects(request, projects, 3)

    context = {'projects': projects,
               'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'projects/projects.html', context)


def project(request,pk):
    projectObj = Project.objects.get(id=pk)
    form = ReviewForm()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        review = form.save(commit=False)
        review.project = projectObj
        review.owner = request.user.profile
        review.save()
        
        
        # update object vote count
        projectObj.getVoteCount
        
        messages.success(request, 'Your Review was successfully submitted')
        
        return redirect('project', pk = projectObj.id )
    # tags = projectObj.tags.all()
    return render(request,'projects/single-project.html',{'project':projectObj,
                                                        #   'tags':tags.
                                                        'form':form
                                                          }) 

@login_required(login_url="login")
def createProject(request):
    profile = request.user.profile
    form = ProjectForm()
    
    if request.method == 'POST':
        # print(request.POST)
        newtags = request.POST.get('newtags').replace(','," ").split()
        
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = profile
            project.save()
            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
            return redirect ('account')
            
            
    context = {'form':form}
    return render(request,'projects/project_form.html', context)


@login_required(login_url="login")
def updateProject(request,pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    form = ProjectForm(instance=project)
    
    if request.method == 'POST':
        newtags = request.POST.get('newtags').replace(','," ").split()
        print(newtags)
        # print(request.POST)
        
        form = ProjectForm(request.POST, request.FILES, instance=project)
        # print(form)
        if form.is_valid():
            project = form.save()
            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                project.tags.add(tag)
            return redirect ('account')
            
    # print(ProjectForm(request.POST, instance=project))        
    context = {'form':form,'project':project}
    return render(request,'projects/project_form.html', context)

@login_required(login_url="login")
def deleteProject(request,pk):
    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    if request.method == 'POST':
        print(project)
        project.delete()
        return redirect('projects')
    else:
        context = {'object':project}
        return render(request, 'delete_template.html',context)