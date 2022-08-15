import profile
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Profile, Skill, Message
from .forms import CustomUserCreationForm, ProfileForm, SkillForm,MessageForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .utils import searchProfiles

# Create your views here.
def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('profiles')
    
    if request.method=='POST':
        username = request.POST['username'].lower()
        password = request.POST['password']
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,'User dose not exist')
            
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect(request.GET['next'] if 'next' in request.GET else 'account')
        else:
            messages.error(request,'Username or password is incorrect')
    return render(request, 'users/login_register.html')


def logoutUser(request):
    logout(request)
    messages.error(request,'Username was Logged out')
    return redirect('login')


def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            
            messages.success(request,'Register successfully')
            
            login(request, user)
            return redirect('edit-account')
        
        else:
            messages.success(request,'An error has occurred during registration')
        
    context = {'page':page,'form':form}
    return render(request,'users/login_register.html',context)


def profiles(request):
    profiles, search_query = searchProfiles(request)
    page = request.GET.get('page')
    result = 6
    paginator = Paginator(profiles, result)
    try:
        profiles = paginator.page(page)
    except PageNotAnInteger:
      
        page = 1
        profiles = paginator.page(page)
        
    except EmptyPage:
        page = paginator.num_pages
        profiles = paginator.page(page)
        
         
    leftIndex= (int(page)-4)
    if leftIndex <1:
        leftIndex = 1
        
        
    rightIndex = (int(page)+5)
    if rightIndex > paginator.num_pages:
        rightIndex = paginator.num_pages +1
    
    custom_range = range(leftIndex,rightIndex)
        
    context = {'profiles':profiles,'search_query':search_query,'paginator':paginator,'custom_range':custom_range}
    return render(request,'users/profiles.html',context)

def userProfile(request, pk):
    profile = Profile.objects.get(id=pk)
    
    topSkills = profile.skill_set.exclude(description__exact="")
    otherSkills = profile.skill_set.filter(description="")
    
    context = {'profile':profile,
               'topSkills':topSkills,
               'otherSkills':otherSkills,
               
               }
    return render(request,'users/user-profile.html',context)

@login_required(login_url='login')
def userAccount(request):
    profile = request.user.profile
    
    skills = profile.skill_set.all()
    projects = profile.project_set.all()
    
    context ={'profile':profile,
               'skills':skills,
               'projects':projects
               }
    return render(request, 'users/account.html',context)

@login_required(login_url='login')
def editAccount(request):
    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

            return redirect('account')

    context = {'form': form}
    return render(request, 'users/profile_form.html',context)

@login_required(login_url='login')
def createSkill(request):
    profile = request.user.profile
    form = SkillForm()
    
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request,'Skill added successfully')
            return redirect('account')
    
    context = {'form':form}
    return render(request, 'users/skill_form.html',context)


@login_required(login_url='login')
def updateSkill(request,pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = SkillForm(instance=skill)
    
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            
            skill.save()
            messages.success(request,'Skill updated successfully')

            return redirect('account')
    
    context = {'form':form}
    return render(request, 'users/skill_form.html',context)


@login_required(login_url="login")
def deleteSkill(request,pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    if request.method == 'POST':
        skill.delete()
        messages.success(request,'Skill deleted successfully')
        return redirect('account')
    context = {'object':skill}
    return render(request,'delete_template.html',context)

@login_required(login_url="login")
def inbox(request):
    profile = request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()
    context = {'messageRequests':messageRequests,'unreadCount':unreadCount}
    return render(request,'users/inbox.html',context)

@login_required(login_url="login")
def viewMessage(request,pk):
    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read==False:
        message.is_read = True
        message.save()
    context = {'message':message}
    return render(request, 'users/message.html',context)

@login_required(login_url="login")
def createMessage(request,pk):
    recipient = Profile.objects.get(id=pk)
    form = MessageForm()
    
    try :
        sender = request.user.profile
    except:
        sender = None
        
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient
            
            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()
            
            messages.success(request,'Your message was successfully sent!')
            return redirect('user-profile', pk=recipient.id)
    context = {'recipient':recipient,'form':form}
    return render(request,'users/message_form.html',context)