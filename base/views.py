from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from django.db.models import Q
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
# rooms = [
#     {"id": 1, "name":"music room"},
#      {"id": 2, "name":"science lab"},
#      {"id": 3, "name":"study room"}
# ]

rooms = Room.objects.all()

def loginPage(req):
    page = "login"
    if req.user.is_authenticated:
        return redirect("home")
    if req.method == "POST":
        username = req.POST.get("username").lower()
        password = req.POST.get("password")
        try: 
            user = User.objects.get(username=username)
        except:
            messages.error(req, "User does not exist")
        user = authenticate(request=req, username=username, password=password)
        if user != None:
            login(user=user, request=req)
            return redirect("home")
        else:
            messages.error(req, "Password is incorrect")
        
    context_table = {
        "req":req,
        "page": page
    }
    return render(req, "base/login_register.html", context_table)

def logoutUser(req):
    logout(req)
    return redirect('home')

def registerPage(req):
    page = "register"
    form = UserCreationForm()
    if req.method == "POST":
        form = UserCreationForm(req.POST)
        print("posting...")
        if form.is_valid():
            print("valid")
            user = form.save(False)
            user.username = user.username.lower()
            user.save()
            login(req, user)
            return redirect("home")
        else:
            messages.error(req, "An error has occured during registration")
    context_table = {
        "req":req,
        "page": page,
        "form":form
    }
    return render(req, "base/login_register.html", context_table)

# Create your views here.
def home(req: HttpRequest):
    q = req.GET.get("q")
    
    rooms = Room.objects.all() if q==None else Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
    topics = Topic.objects.all()[:5]
    room_messages = Message.objects.all() if q==None else Message.objects.filter(Q(room__name__icontains=q) | Q(room__description__icontains=q) | Q(room__topic__name__icontains=q))
    num = rooms.count()
    
    context_table  = {
        "rooms": rooms,
        "topics":topics,
        "num":num,
        "req":req,
        "room_messages": room_messages
    }
    return render(req, "base/home.html", context=context_table)

def userProfile(req, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    num = rooms.count()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context_table = {
        "user": user,
        "rooms": rooms,
        "room_messages": room_messages,
        "topics": topics,
        "num": num,
        "req":req
    }
    return render(req, "base/profile.html", context_table)

def room(req: HttpRequest, pk:str):
    room:dict = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by("-created")
    participants = room.participants.all()
    if req.method == "POST":
        message = Message.objects.create(
            user=req.user,
            room=room,
            body=req.POST.get("body")
        )
        room.participants.add(req.user)
        return redirect('room', pk=room.id)
    context_table = {
        "room":room,
        "messages":room_messages,
        "req": req,
        "participants": participants
    }
    return render(req, "base/room.html", context_table)

@login_required(login_url='login')
def createRoom(req):
    form = RoomForm()
    if req.method == "POST":
        topic_name = req.POST.get("room_topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        desc = req.POST.get("room_desc")            
        name = req.POST.get("room_name")  
        room = Room.objects.create(
            topic=topic,
            description=desc,
            name=name,
            host=req.user,
        )          
        room.participants.set([req.user])
        room.save()
        # form = RoomForm(req.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = req.user
        #     room.save()
        return redirect('home')
    topics = Topic.objects.all()
    context_table = {
        "form": form,
        "req": req,
        "topics": topics,
    }
    return render(req, "base/room_form.html", context_table)

@login_required(login_url='login')
def updateRoom(req, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if req.method == "POST":
        form = RoomForm(req.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")
            
    context_table = {
        "form": form,
        "req": req
    }
    return render(req, 'base/room_form.html', context_table)

@login_required(login_url='login')
def deleteRoom(req, pk):
    room = Room.objects.get(id=pk)
    if req.method == "POST":
        room.delete()
        return redirect('home')
    context_table = {
        "obj": room,
        "req": req
    }
    return render(req, 'base/delete.html',context_table)


@login_required(login_url='login')
def deleteMessage(req, pk):
    message = Message.objects.get(id=pk)
    if req.method == "POST":
        message.delete()
        return redirect('home')
    context_table = {
        "obj": message,
        "req": req
    }
    return render(req, 'base/delete.html',context_table)


@login_required(login_url='login')
def updateUser(req):
    user = req.user
    form = UserForm(instance=user)
    if req.method == "POST":
        form = UserForm(req.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', user.id)
    context_table = {
        "req":req,
        "form":form
    }
    return render(req, "base/update-user.html", context_table)


def topics(req):
    topics =  Topic.objects.all() if req.GET.get("q")==None else Topic.objects.filter(Q(name__icontains = req.GET.get("q")))
    count = Room.objects.all().count()
    context_table = {
        "req":req,
        "topics":topics,
        "num":count
    }
    return render(req, "base/topics.html", context_table)


def activity(req):
    messages =  Message.objects.all()
    context_table = {
        "req":req,
        "messages":messages,
    }
    return render(req, "base/activity.html", context_table)