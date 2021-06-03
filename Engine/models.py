from django.contrib.auth.models import AbstractUser
from django.db import models, migrations
from datetime import datetime

class Migration(migrations.Migration):
    atomic = False # <<<< THIS LINE


#Userdata and other things
class User(AbstractUser):
    likes = models.ManyToManyField("GameData", blank=True, related_name="userlikes")
    comments = models.ManyToManyField("Comment", blank=True, related_name="usercomments")
    pass


#Comments from users for games
class Comment(models.Model):
    content = models.CharField(max_length=1000, default="")
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="commentuser")
    game = models.ForeignKey("GameData", on_delete=models.CASCADE, related_name="commentgame")
    timestamp = models.CharField(max_length=100, default="")

    def __str__(self):
        return f"{self.content}"

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "game": self.game.name,
            "timestamp": self.timestamp,
        }


#the spaces with which the game can access
class Room(models.Model):
    name = models.CharField(max_length=100, default="")
    entrancetext = models.CharField(max_length = 1000, default="")


    def __str__(self):
        return f"{self.name}"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "entrancetext": self.entrancetext,
        }


#The routes between rooms
class Routes(models.Model):
    entrance = models.ForeignKey("Room", default="", on_delete=models.CASCADE, related_name="entrance")
    exitway = models.ForeignKey("Room", on_delete=models.CASCADE, default="", related_name="exit")
    reqresponse = models.ManyToManyField("Response", default="", blank=True, related_name="requirements")
    disqualifier = models.ManyToManyField("Response", default="", blank=True, related_name="disqual")
    openpath = models.BooleanField(blank = True, default=True)
    hidden_when_inactive = models.BooleanField(blank = True, default=False)
    priority = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.entrance}:{self.exitway}"

    def serialize(self):
        return {
            "id": self.id,
            "entrance": self.entrance.name,
            "exitway": self.exitway.name,
            "reqresponse": [req.name for req in self.reqresponse.all()],
            "disqualifier": [req.name for req in self.disqualifier.all()],
            "openpath": str(self.openpath),
            "routehide": str(self.hidden_when_inactive),
            "priority": str(self.priority),
        }


#responses to events
class Response(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True)
    event = models.ForeignKey("Event", on_delete=models.CASCADE, default = "", null=True, blank=True)
    ReqEvents = models.ManyToManyField("Response", blank=True, related_name="Prereq")
    Disqualifier = models.ManyToManyField("Response", blank = True, related_name="Noes")
    priority = models.IntegerField(blank=True, default=0)
    activeresponse = models.BooleanField(blank = True, default=True)
    hidden_when_inactive = models.BooleanField(blank = True, default=False)
    auto_activate = models.ManyToManyField("Response", blank=True, related_name="autoactive")
    activate_on_entry = models.ManyToManyField("Room", blank=True, related_name="visitactive")


    def __str__(self):
        return f"{self.name}"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "event": self.event.name,
            "ReqEvents": [event.name for event in self.ReqEvents.all()],
            "Disqualifier": [event.name for event in self.Disqualifier.all()],
            "priority": str(self.priority),
            "activeresponse": str(self.activeresponse),
            "rezhide": str(self.hidden_when_inactive),
            "auto_activate": [req.name for req in self.auto_activate.all()],
            "activate_on_entry": [room.name for room in self.activate_on_entry.all()]
        }

    def auto_activate_notnull(self):
        if len(self.auto_activate.all()) > 0:
            return True
        else:
            return False
        
    def activate_on_entry_notnull(self):
        if len(self.activate_on_entry.all()) > 0:
            return True
        else:
            return False


#A users save data.  Saved every time they take an action.
class SaveData(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=False, default="")
    currentroom = models.ForeignKey("Room", on_delete = models.CASCADE, default="")
    Responses = models.ManyToManyField("Response", blank=True)
    game = models.ForeignKey("GameData", on_delete=models.CASCADE, default="")
    alreadyasked = models.ManyToManyField("Event", blank=True, default="")
    visited = models.ManyToManyField("Room", blank=True, default="", related_name="visits")

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "currentroom": self.currentroom.name,
            "Responses": [response.name for response in self.Responses.all()],
            "game": self.game.name,
            "alreadyasked": [event.name for event in self.alreadyasked.all()],
            "visited": [room.serialize() for room in self.visited.all()],
        }




class ObjectiveState(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    winstate = models.BooleanField(default=True, blank=True)
    rooms = models.ManyToManyField("Room", blank=True)
    responses = models.ManyToManyField("Response", blank=True)
    room_and_response_condition = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "winstate": str(self.winstate),
            "rooms": [room.serialize() for room in self.rooms],
            "responses": [response.serialize() for response in self.responses],
            "room_and_response_condition": str(self.room_and_response_condition)
        }



#Events which make up the bulk of interaction in the game
class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, default="")
    location = models.ForeignKey("Room", on_delete=models.CASCADE, related_name="EventLocation", default="")
    ReqEvents = models.ManyToManyField("Response", blank=True, related_name="Prerequisites")
    Disqualifier = models.ManyToManyField("Response", blank = True, related_name="NoGoes")
    responses = models.ManyToManyField("Response", blank=True, related_name="EventResponse")
    priority = models.IntegerField(blank=True, default=0)
    auto_responses = models.ManyToManyField("Response", blank=True, related_name="AutoResponses")


    def __str__(self):
        return f"{self.name}"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "location": self.location.name,
            "ReqEvents": [event.name for event in self.ReqEvents.all()],
            "Disqualifier": [event.name for event in self.Disqualifier.all()],
            "responses": [event.serialize() for event in self.responses.all().order_by("-priority")],
            "priority": str(self.priority),
        }


#Data loaded for a single game.  Useful for organization
class GameData(models.Model):
    name = models.CharField(max_length=100)
    rooms = models.ManyToManyField("Room", blank=True, related_name="rooms")
    Events = models.ManyToManyField("Event", blank=True)
    descript = models.CharField(max_length=1000, default="")
    Routes = models.ManyToManyField("Routes", blank=True)
    startroom = models.ForeignKey(
    "Room", on_delete=models.CASCADE, blank=True, related_name="start", null=True)
    endroom = models.ForeignKey(
    "Room", on_delete=models.CASCADE, blank=True, related_name="end", null=True)
    responses = models.ManyToManyField("Response", blank=True)
    objectives = models.ManyToManyField("ObjectiveState", blank=True)

    likes = models.ManyToManyField("User", blank=True, related_name="gamelikes")
    comments = models.ManyToManyField("Comment", blank=True, related_name="gamecomments")
    

    def __str__(self):
        return f"{self.name}"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "descript": self.descript,
            "Events": [event.name for event in self.Events.all()],
            "Routes": [route.name for route in self.Routes.all()],
            "rooms": [room.name for room in self.rooms.all()],
            "startroom": self.startroom.name,
            "endroom": self.endroom.name,
            "responses": [rez.name for rez in self.responses.all()],
            "objectives": [objective.serialize() for objective in self.objectives.all()]
        }

    def get_comments(self):
        return {
            "comments": [comment.serialize() for comment in self.comments.all()]
        }