Project by John Morrisett

This project contains software designed to make it easy to make text-based adventure games, and to
mock-up a website where users could like and comment on games.  The software is easy enough to use
that users would be able to create their own games without any javascript or python knowledge.

Overview of files:
scripts.js:  The javascript that makes the application run.  Mostly handles front-end updating of
information
styles.css:  The css styling for the application.
models.py:  Django functionality.  Defines the models necessary for games to run.
urls.py:  Urls for pages
views.py:  The backend python code for handling interaction between javascript and the SQL database.

templates-
layout.html:  The basic layout for a page.
game.html:  The basic view for a game.  This is heavily changed once the game starts, however
index.html:  The index of games available for play.
login.html:  The login page.
loginerror.html:  Occurs whenever someone tries to do anything without logging in.
register.html:  Registering page

The project heavily uses SQL in order to keep track of data.  Under Engine/models.py, there are many models.
This is a quick run-through of what each model does.  Reading these will help you use the functionality
of many of the models, but its not strictly necessary.


(can be skipped for now)
User -
    Inherits from the user class, see their documentation.
    Also adds two new fields - comments and likes.

        Likes - ManyToManyField which shows which games the user has liked.
        Comments - ManyToManyField for the comments model.

Comment -
    Model which contains comments that users made about games
    
        content - the content of the comment
        user - displays which user owns the comment
        game - displays which game the comment belongs to
        timestamp - displays what time the comment was made

Room -
    Standard space which a game uses to center events, routes etc.
        name - name of the room
        entrancetext - text that displays when a player enters the room

Routes -
    The routes between rooms.  Can be activated or deactivated based on events.

        entrance - where the route begins
        exitway = where the route ends

            note - entrance and exits basically just define routes

        reqresponse - required responses for the route to open.  No reqs mean always open.
            All responses are required.
        disqualifier = responses that close the route.  Any disqualifier closes the route
        openpath - based on the two fields above, returns boolean expression of open or not.
        hidden_when_inactive - If this route is inactive, decide whether to show inactive button
            or hide it altogether.
        priority - Decides if this route will be displayed first.  Visual only.

Response -
    Items that decide whether routes, events, or even other responses should be active or not.

        name - name of response
        description - description of response, displays when activated.
        event - event which this is attached to (not necessary, but helpful)
        ReqEvents = required events for this response to be active in an event situation
            AND logic - all must be active
        Disqualifier = events that stop this event from being active in an event situation
            OR logic - only one has to be active
        priority - Decides how soon this response will be displayed in an event situation
        activeresponse - boolean function displaying 
            if this event is active or inactive based on the requirements
        hidden_when_inactive - decides if this response will be hidden, or simply shown but not
            accessible in an event situation
        auto_activate - automatically added to response list once conditions are met.
        activate_on_entry - automatically added to response list once one of the rooms is visited

SaveData - 
    Data that the game uses to decide where the player is located, which responses they have
    chosen etc.  Updates every time a decision is made in the game.

        user - user owning this data
        currentroom - room which the player is currently in
        Responses - list of responses that have been activated.
        game - game which this savedata belongs to
        alreadyasked - list of events which have already occurred per room.
            Basically used to make sure that events don't activate twice per room visit
        visited - list of rooms that the player has visited

ObjectiveState -
    Model that contains information about win and loss states of the game.

        name - name of win/loss condition
        description - description of win/loss state.
            Displayed upon activation of win/loss state.
        winstate - If true, this is a winning result.  Otherwise, it's a losing result.
        rooms - rooms where the game can be won.
            OR logic
        responses - list of responses that need to be achieved in order to win
        room_and_response_condition - if this is true, both the room and the responses need
            to be met in order for the state to be achieved.  (AND logic)
            otherwise, either one can be met.  (OR logic)

Event -
    Object that has two main functionaities
    1.  Display a list of responses
    2.  Display some text (like flavor text)
    Option 1 is achieved by setting a list of responses.  This option is more of a function.
    Option 2 is achieved by NOT setting a list of responses.  Then, just the flavor text is
        displayed.

        name - name of event
        description - description of event.  Displays when event is activated
        location - room that can activate the event
        ReqEvents - Required responses for the event to activate
            AND logic (all need to activate)
        Disqualifier - Responses that disqualify the event from activating
            OR logic (only one response)
        responses - list of responses that the event can log into the save data.
        priority - The higher the priority, the sooner the event will be displayed.
            If you have event A and event B, if event B has a higher priority, the game
            will activate event B, and then once that response is logged, it will activate event A
        auto_responses - responses that are automatically logged into the save data, no matter what.
            Useful for flavor text events, by setting an auto-response to be logged after the
            event is activated, and then disqualifying the event using that same response.

GameData-
    List of models that the game uses.  Not strictly necessary, but useful for
    organization.

        name = name of game.
        rooms - list of rooms in the game
        Events - list of events in the game
        descript - description of the game
        Routes - list of routes in the game
        startroom - room that the game starts in.
        endroom - unused
        objectives - list of win/loss conditions

        likes - list of players that like the game
        comments - list of comments made about the game

OVERVIEW OF PROJECT - 
The main feature of this project is not the games themselves - both of them are fun, but the real
power in this project is the editor.

The software uses four main interlooping models in order to provide functionality:  
-Events
-Responses
-Rooms
-Routes

Rooms are the basic building block of any game.  They trigger events, responses etc.
Routes are the ways that you get to rooms, from other rooms.  They can be activated using responses
Responses are a list of objects that are activated by the player, and then logged into their save data.
Events are the main way responses are triggered.  They can have requirements, such as having certain
responses triggered before activating.

Again, the real power is in the editor here.  I would encourage you to try and make your own game
using the admin function - just define routes between rooms, events etc.  No javascript or python
is required to make a game - just a little knowledge of how the events work.