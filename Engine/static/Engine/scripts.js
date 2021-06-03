
document.addEventListener("DOMContentLoaded", function() {
    var csrftoken = getCookie('csrftoken');

    //set the speed at which text scrolls (shorter is better)
    headerspeed = 50
    entrancetextspeed = 20
    eventspeed = 20
    responsespeed = 20

    document.querySelector("#likebutton").onclick = function() {

        likedata = this.dataset.likestat
        fetch(`/updatelikes`, {
            headers: {
                'X-CSRFToken': csrftoken
            },
            method: "PUT",
            body:JSON.stringify({
                game: document.querySelector("#gamename").innerHTML,
                likedata: likedata,
            })
        })
        .then(response => response.json())
        .then(data => { 
            userlike = data[0]
            likenum = data[1]
            
            document.querySelector("#likebutton").innerHTML = userlike
            document.querySelector("#likebutton").setAttribute("data-likestat", userlike)
            document.querySelector("#likecount").innerHTML = `Liked by: ${likenum}`
            
        })
    }


    function getCookie(name) {

        //csrf cookie validation
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }



    document.querySelector("#NewGameButton").onclick = function() {
        //New game function
        fetch(`/newgame`, {
            headers: {
                'X-CSRFToken': csrftoken
            },
            method: "PUT",
            body:JSON.stringify({
                game: document.querySelector("#gamename").innerHTML
            })
        })
        .then(response => response.json())
        .then(data => {
            move(data)
        })
    }


    document.querySelector("#ContinueGameButton").onclick = function() {

        //Continue game function
        fetch(`/continuegame`, {
            headers: {
                'X-CSRFToken': csrftoken
            },
            method: "PUT",
            body:JSON.stringify({
                game: document.querySelector("#gamename").innerHTML
            })
    })
            .then(response => response.json())
            .then(data => {
                move(data)
            })
    }


    function updatebuttons(csrftoken) {

    //Updates buttons according to their functionality
    document.querySelectorAll(".optionbutton").forEach(button => {
        button.onclick = function() {

            //If this is a movement button, execute a movement command
            if (this.dataset.type == "move") {
            buttonval = this.dataset.move
            fetch(`/move`, {
                headers: {
                    'X-CSRFToken': csrftoken
                },
                method: "PUT",
                body:JSON.stringify({
                    room: buttonval,
                    game: document.querySelector("#gamename").innerHTML
                })
    
            })
            .then(response => response.json())
            .then(data => {
                console.log(data)
                move(data)
            })

            //If this is a response button, execute a response command
        } else if (this.dataset.type == "response") {
            buttonval=this.dataset.response
            fetch(`/respond`, {
                headers: {
                    'X-CSRFToken': csrftoken
                },
                method: "PUT",
                body:JSON.stringify({
                    response: buttonval,
                    noresponseevent:  false,
                    game: document.querySelector("#gamename").innerHTML
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log(data)
                updateview(data)
            })
        }
    }
            
    })
 }

    
function typeWrapper(cont, target, speed, wait) {

    //Asynchronus function that types text out instead of dumping it all at once
    return new Promise(function (resolve) {
        i = 0
        basespeed = speed
        function typeWriter(cont, target, speed) {

            //Option to speed up text
            document.addEventListener("keydown", event => {
                if (event.keyCode == 32) {
                    speed = 0.1
                }
            })

            document.addEventListener("keyup", event => {
                if (event.keyCode == 32) {
                    speed = basespeed
                }
            })

/***************************************************************************************
*    Below code adapted from:
*    Title: How TO - Typing Effect
*    Author: None given
*    Date: 5/4/2020
*    Code version: None given
*    Availability: https://www.w3schools.com/howto/howto_js_typewriter.asp
*    
***************************************************************************************/

            if (i < cont.length) {
                document.getElementById(target).innerHTML += cont.charAt(i)
                i++
                setTimeout(function() {typeWriter(cont, target, speed)}, speed)
            } else {setTimeout(function() {resolve("yes")}, wait
            )}
        }
        typeWriter(cont, target, speed)
    })
    } 


function loadobjectivestate(data) {

    //If the user has lost or won the game, this view is loaded
    const content = data[1][0]
    document.getElementById("windowView").innerHTML = ""
    const header = document.createElement("h1")
    header.style="text-align:center;margin:30px;"
    header.innerHTML = `You ${content.condition}!`
    const description = document.createElement("div")
    description.style="text-align:center;margin:30px"
    description.innerHTML = `Overview: ${content.description}`
    const tag = document.createElement("div")
    tag.style="text-align:center;margin:30px"
    tag.innerHTML = "Reload the page to start a new game"

    document.getElementById("windowView").append(header)
    document.getElementById("windowView").append(description)
    document.getElementById("windowView").append(tag)
}


function updateview(data) {

    //updates part of the view after responding to an event, instead of the entire view
    if (data[0] == "ObjectiveCompleted") {
        loadobjectivestate(data)
    }

    else {
        console.log(data)

    //set some variables for later, delete old info
    const responsedata = data[3]
    const eventdata = data[2]
    const exits = data[1]


    eventcont = ""
    if (eventdata.length > 0) {
        activeevent = eventdata[0]
        eventcont = activeevent.description
    }

    if (eventdata.length == 0) {
        document.querySelector("#optionHeader").innerHTML = "Move to:"}

        else {
        document.querySelector("#optionHeader").innerHTML = "Select one:"
        }  
    document.querySelector("#optionlist").innerHTML = ""


    const resulttext = document.createElement("div")
    resulttext.id="resulttext"
    resulttext.style=
    "text-align:left;font-size:14px;border-top:solid;margin-top:10px"
    document.querySelector("#gameView").append(resulttext)

    //show the result, then once the user has confirmed, move on
    if (responsedata == "null") {
        responsedesc = ""}
    else {responsedesc = responsedata.description}
    typeWrapper(responsedesc, "resulttext", responsespeed, 500)
    
    .then(data => {
        button = document.createElement("button")
        button.id="moveon"
        button.className = "Button1"
        button.innerHTML = "Got it!"

        document.querySelector("#gameView").append(button)
        
        document.querySelector("#moveon").onclick = function () {

            //delete the confirm, result, and event buttons/text
            document.querySelector("#moveon").remove()
            document.querySelector("#resulttext").remove()
            document.querySelector("#eventtext").innerHTML = ""
            eventcont = ""
                if (eventdata.length > 0) {

                    activeevent = eventdata[0]
                    eventcont = activeevent.description
            
                    typeWrapper(eventcont, "eventtext", eventspeed, 1000)
                    .then(data => 
                            respondupdate(activeevent, csrftoken)
                    )}
                else {
                load_move_view(exits)}
            }
            
        })
        
}}


//Updates the game view so that new content and buttons are displayed
function move(data){ 
    if (data[0] == "ObjectiveCompleted") {
        loadobjectivestate(data)
    }
    else {

    //Defines data, specifically the current room data and the exits, as well as useful variables
    const currentroom = data[0]
    const headercont = currentroom.name
    const entrancetextcont = currentroom.entrancetext

    const exits = data[1]

    //defines eventdata for events
    const eventdata = data[2]

    eventcont = ""
    if (eventdata.length > 0) {
        activeevent = eventdata[0]
        eventcont = activeevent.description
    }


    //Sets up the text view to be changed
    if (eventdata.length == 0) {
    document.querySelector("#optionHeader").innerHTML = "Move to:"}
    else {
    document.querySelector("#optionHeader").innerHTML = "Select one:"
    }
    document.querySelector("#optionlist").innerHTML = ""
    document.querySelector("#gameView").innerHTML = ""
    const headertext = document.createElement("h3")
    headertext.id = "roomheader"
    const contenttext = document.createElement("div")
    contenttext.id = "entrancetext"
    contenttext.style="text-align:left;font-size:14px"
    const eventtext = document.createElement("div")
    eventtext.id="eventtext"
    eventtext.style=
    "text-align:left;font-size:14px;border-top:solid;margin-top:10px"

    document.querySelector("#gameView").append(headertext)
    document.querySelector("#gameView").append(contenttext)
    document.querySelector("#gameView").append(eventtext)

    //Asynchronus string that first types out the header, then the content, then loads the buttons.
    if (eventdata.length > 0) {
        typeWrapper(headercont, "roomheader", headerspeed, 1000)
        .then(data =>
            typeWrapper(entrancetextcont, "entrancetext", entrancetextspeed, 500))
        .then(data => 
            typeWrapper(eventcont, "eventtext", eventspeed, 500))
        .then(data => 
            respondupdate(activeevent, csrftoken))
        
            }
        
    else {
        typeWrapper(headercont, "roomheader", headerspeed, 1000)
        .then(data =>
            typeWrapper(entrancetextcont, "entrancetext", entrancetextspeed, 500))
        .then(data => load_move_view(exits))
    }
        
    
 }}

    //loads movement buttons
    function load_move_view(exits) {
            for (item in exits) {
                add_move_button(exits[item])
            }
            updatebuttons(csrftoken)
    }


    function respondupdate(activeevent, csrftoken) {
        if (activeevent.responses.length > 0) {
            for (item in activeevent.responses) {
            add_option_button(activeevent.responses[item])}
        updatebuttons(csrftoken)}
        else {
                fetch(`/respond`, {
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    method: "PUT",
                    body:JSON.stringify({
                        response: activeevent.name,
                        noresponseevent:  "true",
                        game: document.querySelector("#gamename").innerHTML
                    })
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data)
                    updateview(data)
                })
            }
    }


    //adds individual move buttons
    function add_move_button(exit) {

        //only add if active or not hidden when inactive
        if (!(exit.openpath == "False" && exit.routehide == "True")) {
    const button = document.createElement('button');
    button.className="exitbutton Button1 optionbutton";
    button.id = `move_button${exit.exitway}}`
    button.setAttribute("data-move", exit.exitway)
    button.setAttribute("data-type", "move")
    button.innerHTML = exit.exitway
    if (exit.entrance == exit.exitway) {
        button.innerHTML = `Search around ${exit.exitway} more`
    }

    //If inactive and hidden when inactive, disable the button
    if (exit.openpath == "False" && exit.routehide == "False") {
        button.setAttribute("disabled", true)
    }

    document.querySelector("#optionlist").append(button);
    }}

    //adds individual option buttons
    function add_option_button(rez) {

        //Only add if active or not hidden when inactive
        if (!(rez.activeresponse == "False" && rez.rezhide == "True")) {
        const button = document.createElement('button');
        button.className="responsebutton Button1 optionbutton";
        button.id=`response_button${rez.name}`
        button.setAttribute("data-response", rez.name)
        button.setAttribute("data-type", "response")
        button.innerHTML = rez.name

        //If inactive and hidden when inactive, disable the button
        if (rez.activeresponse == "False" && rez.rezhide == "False") {
            button.setAttribute("disabled", true)
        }

        document.querySelector("#optionlist").append(button)

    }}
  })