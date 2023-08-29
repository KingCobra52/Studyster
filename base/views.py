from django.shortcuts import render, redirect 
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.forms import UserCreationForm 
from django.http import HttpResponse 
from .models import Room, Topic, Message 
from .forms import RoomForm 

# Create your views here.

# rooms = [
#     {'id':1, 'name':'Lets learn python!'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'front end devolpers'},
# ]

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST": #user gave info 
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username) #if this works then keep going 
            ######
            user = authenticate(request, username=username, password=password)
        
            if user is not None:
                login(request, user) #adds session inside db and browser 
                return redirect('home')
            else:
                messages.error(request, 'Username OR password does not exist')
                ##########
        except:
            messages.error(request, 'User does not exist')
        ######## -> was here  
    context = {'page':page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) #able to access user right away 
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
            
    return render(request, 'base/login_register.html', {'form': form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else '' #read like sentence, gets data after q in url if there is data present 
    
    rooms = Room.objects.filter(  #if q == None, room.objects.all 
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    
    topics = Topic.objects.all()
    room_count = rooms.count() #gives length of querySet 
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    
    
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context) #app/html file if template folder located within app

def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all() #gives set of messages (child) related to specific room
    participants = room.participants.all()
    
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk = room.id)
        
        
    context = {'room':room, 'room_messages': room_messages, 'participants': participants} #all room requests contain room object 
    return render(request, 'base/room.html', context) #pk is added to the end of the request

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST': 
        form = RoomForm(request.POST) # pass in all data to form object
        if form.is_valid():
            room = form.save() 
            room.host = request.user 
            room.save()
            return redirect('home')
    context = {'form': form} 
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    
    if request.user != room.host:
        return HttpResponse('You do not own this room')
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room) #sepcify instance or new room will be created 
        if form.is_valid():
            form.save()
            return redirect('home')
    
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You do not own this room')
    
    if request.method == 'POST':
        room.delete() #deletes from database 
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You did not create this message')
    
    if request.method == 'POST':
        message.delete() #deletes from database 
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})