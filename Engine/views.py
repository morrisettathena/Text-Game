from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from datetime import datetime
from .models import *
import time
import json


def detectuser(request):

    # detects who and if the user exists
    try:
        return User.objects.get(username=request.user.get_username())
    except:
        return None


def get_save(request, user, game):

    # gets the save data for the user from the current game
    data = SaveData.objects.get(user=user, game=game)
    return data


def index(request):

    # displays the index of games on the home page
    if detectuser(request):
        return render(request, "Engine/index.html", {
            "games": GameData.objects.all(),
            "user": detectuser(request),
        })
    else:
        return HttpResponseRedirect(reverse("loginerror"))


def updatelikes(request):

    # Updates the like functionality
    data = json.loads(request.body)
    game = GameData.objects.get(name=data.get("game"))
    user = detectuser(request)
    if data.get("likedata") == "Like?":
        user.likes.add(game)
        game.likes.add(user)
        likedata = "Unlike?"
    else:
        user.likes.remove(game)
        game.likes.remove(user)
        likedata = "Like?"
    user.save()
    game.save()

    likes = len(game.likes.all())
    info = [likedata, likes]

    return JsonResponse(info, safe=False)


def packetdata(request, game):

    # Given a game's information
    # return a packet containing all the information
    # that javascript needs to load the page
    user = detectuser(request)
    savedata = get_save(request, user, game)
    current = savedata.currentroom
    events = game.Events.filter(location=current).order_by("-priority")
    eventdata = []

    # quickly runs through any active responses and checks if they are active
    for event in events:
        for rez in event.responses.all():
            if len(rez.ReqEvents.all()) == 0:
                i = 1
            else:
                i = 1
                for item in rez.ReqEvents.all():
                    if item not in savedata.Responses.all():
                        i = 0
            if len(rez.Disqualifier.all()) == 0 and i != 0:
                i = 1
            elif len(rez.Disqualifier.all()) > 0 and i != 0:
                i = 1
                for item in rez.Disqualifier.all():
                    if item in savedata.Responses.all():
                        i = 0
            if i == 1:
                rez.activeresponse = True
            else:
                rez.activeresponse = False
            rez.save()

    # Loads any events that have met their requirements
    for event in events:
        if event not in savedata.alreadyasked.all():
            if len(event.ReqEvents.all()) == 0:
                i = 1
            else:
                i = 1
                for item in event.ReqEvents.all():
                    if item not in savedata.Responses.all():
                        i = 0
            if len(event.Disqualifier.all()) == 0 and i != 0:
                i = 1
            elif len(event.Disqualifier.all()) > 0 and i != 0:
                i = 1
                for item in event.Disqualifier.all():
                    if item in savedata.Responses.all():
                        i = 0
            if i == 1:
                eventdata.append(event)

    # Loads any routes that have met their requirements
    rooms = game.Routes.filter(entrance=current).order_by("-priority")
    routes = []
    for route in rooms:
        if len(route.reqresponse.all()) == 0:
            i = 1
        else:
            i = 1
            for item in route.reqresponse.all():
                if item not in savedata.Responses.all():
                    i = 0
        if i == 1:
            if len(route.disqualifier.all()) == 0:
                i = 1
            else:
                i = 1
                for item in route.disqualifier.all():
                    if item in savedata.Responses.all():
                        i = 0

        if i == 1:
            route.openpath = True
        else:
            route.openpath = False
        route.save()
        routes.append(route.serialize())

    # Serialize and package all of the information
    eventdata1 = [event.serialize() for event in eventdata]
    routes = [route.serialize() for route in rooms]
    current = current.serialize()
    packet = [current, routes, eventdata1]
    return packet


def maintenance(request, rooms, game, events, responses):

    # fixes some fields and objects in case they were missed.
    for item in rooms:
        if len(Routes.objects.filter(entrance=item, exitway=item)) == 0:
            Selfroute = Routes(entrance=item, exitway=item, priority=-1)
            Selfroute.save()
            game.Routes.add(Selfroute)
    for item in events:
        for rez in item.responses.all():
            if rez.event != item:
                rez.event = item
                rez.save()
    for item in events:
        for rez in item.responses.all():
            if rez not in game.responses.all():
                game.responses.add(rez)
                rez.save()


def newgame(request):

    # Get objects, load a new save
    data = json.loads(request.body)
    game = GameData.objects.get(name=data.get("game"))

    rooms = game.rooms.all()
    events = game.Events.all()

    responses = game.responses.all()
    maintkey = 0

    if maintkey == 0:
        maintenance(request, rooms, game, events, responses)
    old_data = SaveData.objects.filter(user=detectuser(request), game=game)
    for obj in old_data:
        obj.delete()

    # The data for a new game
    new_data = SaveData(
        user=detectuser(request), currentroom=game.startroom, game=game)
    new_data.save()
    new_data.Responses.set([])
    new_data.save()

    updateresponse(data, new_data)
    packet = packetdata(request, game)

    return JsonResponse(packet, safe=False)


def continuegame(request):

    data = json.loads(request.body)
    game = GameData.objects.get(name=data.get("game"))
    savedata = SaveData.objects.get(user=detectuser(request), game=game)
    packet = packetdata(request, game)

    return JsonResponse(packet, safe=False)


def move(request):

    # Save any new data, and then load information from that data.
    data = json.loads(request.body)
    room = Room.objects.get(name=data.get("room"))
    game = GameData.objects.get(name=data.get("game"))
    user = detectuser(request)

    old_data = get_save(request, user, game)
    old_data.currentroom = room
    old_data.alreadyasked.set([])
    old_data.visited.add(room)
    old_data.save()
    updateresponse(request, old_data)

    packet = packetdata(request, game)

    placeholder = checkobjectivestate(request, old_data)

    if placeholder:
        packet = placeholder
    return JsonResponse(packet, safe=False)


def updateresponse(request, savedata):

    # Updates the responses in the game, in case a new item is triggered
    responses = savedata.game.responses.all()

    for item in responses:
        if item.auto_activate_notnull() is True:
            i = 1
            for itemautoreqs in item.auto_activate.all():
                if itemautoreqs not in savedata.Responses.all():
                    i = 0
            if i == 1:
                savedata.Responses.add(item)
                savedata.save()
        elif item.activate_on_entry_notnull() is True:
            i = 1
            for itemlocreqs in item.activate_on_entry.all():
                if itemlocreqs not in savedata.visited.all():
                    i = 0
            if i == 1:
                savedata.Responses.add(item)
                savedata.save()


def objectiveinfo(request, state):

    # Supplies win/lose state information
    if state.winstate is True:
        condition = "Won"
    else:
        condition = "Lost"
    return ["ObjectiveCompleted", [{
        "name": state.name,
        "description": state.description,
        "condition": condition
    }]]


def checkobjectivestate(request, savedata):

    # Checks if conditions have been met for a win/lose state
    objectives = savedata.game.objectives.all()
    for item in objectives:
        roomlen = len(item.rooms.all())
        responselen = len(item.responses.all())
        state = 0
        if savedata.currentroom in item.rooms.all() and len(item.rooms.all()) > 0:
            state += 1
        if len(item.responses.all()) > 0:
            i = 1
            for obj in item.responses.all():
                if obj not in savedata.Responses.all():
                    i = 0
            if i == 1:
                state += 1
        if state == 2:
            savedata.delete()
            return objectiveinfo(request, item)
        elif state == 1 and ((item.room_and_response_condition == False) or
        (responselen == 0 or roomlen == 0)):
            savedata.delete()
            return objectiveinfo(request, item)
        

def respond(request):

    # Update the user data when making a response to an event
    data=json.loads(request.body)
    game = GameData.objects.get(name=data.get("game"))

    user = detectuser(request)
    old_data=get_save(request, user, game)

    print(old_data.Responses.all())

    # If this is a no-response event, update the event.  Otherwise update with the response.
    if data.get("noresponseevent") == "true":
        event = Event.objects.get(name=data.get("response"))
        serialize_response = "null"
    else:
        response = Response.objects.get(name=data.get("response"))
        old_data.Responses.add(response)
        event = response.event
        serialize_response = response.serialize()
    old_data.alreadyasked.add(event)
    for item in event.auto_responses.all():

        old_data.Responses.add(item)
    old_data.save()
    updateresponse(request, old_data)

    packet = packetdata(request, game)
    packet.append(serialize_response)
    placeholder = checkobjectivestate(request, old_data)
    if placeholder:
        packet = placeholder

    return JsonResponse(packet, safe=False)


def game(request, game_name):

    # Loads the start menu for a game
    if detectuser(request):

        game = GameData.objects.get(name=game_name)
        current_data = SaveData.objects.filter(
        user=detectuser(request), game=game)

        if request.method == "POST":
            content = request.POST["newPostInput"]
            time = str(datetime.now())
            formattime = f"{time[:4]}{time[5:7]}{time[8:10]}{time[11:19]}"
            user = detectuser(request)
            f = Comment(content=content,
                user=user, game=game, timestamp=formattime)
            f.save()
            game.comments.add(f)
            game.save()

        if game in detectuser(request).likes.all():
            userlikes = True
        else:
            userlikes = False

        if not current_data:
            current_data = None
        else:
            current_data = SaveData.objects.get(
                user=detectuser(request), game=game)
        comments = game.comments.all().order_by("-timestamp")

    else:
        return HttpResponseRedirect(reverse("loginerror"))
    return render(request, "Engine/game.html", {
        "game": game,
        "current_data": current_data,
        "likes": len(game.likes.all()),
        "userlikes": userlikes,
        "comments": comments,

    })


def loginerror(request):
    return render(request, "Engine/loginerror.html")


"""
*    All code below taken directly from previous projects
*    Title: None given
*    Author: TAs of CSCI E-33a from Spring 2020 semester
*    Date: 5/4/2020
*    Code version: None given
*    Availability: Not publicly available
"""


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "Engine/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "Engine/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "Engine/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "Engine/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "Engine/register.html")