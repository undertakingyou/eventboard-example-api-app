# EventBoard Example API Application

## Overview
This example application is meant to provide a working example of how to use the EventBoard API to automatically book a space, or free a space, with the use of a sensor. This is done by making simple get calls to this application running on a webserver.

## Installation
This application uses sqlite3 for stateful storage and flask as a webframework. Thank you very much to these teams and for details on those projects please see them. These instructions assume that you have a certain working knowledge of your systems and how to deploy web applications. If not, a dev ops team member will be a handy resource.

Once you have cloned this repository to where you want, you will need to change a couple of things in the code. 
 1. In schema.sql you will need to change the initial data to actual EventBoard client id, access token, refresh token, etc. that you have gotten using a tool like Postman's OAUTH2.0 flow.
 2. In eb_sensor_app.py you should change the top environmental variables to match what you need your actual application to say and have locations match actual deployed locations.

Now that you changed those things you will need to install the items found in the requirements.txt file using pip. You are welcome to use virtualenvs if needed, just know that when you actually go to run the server.

Next we need to load the initial data that you have already set. You can do this with sqlite3 directily (e.g. `sqlite3 desired/db/location/path/eb_sensor_app.db < schema.sql`) or using the create db commands that are included (thank you Flask example team) by doing `flask initdb`.

Last step is to have the webserver actually point to it. The built in Flask server is for testing only, and not meant for something that might get more than one request at a time. Using something like gunicorn with an nginx proxy can work well.

## Usage
Once up and running on a webserver you should be able to call the app with a simple GET call. All of these calls still follow the calendar edit permissions, and that should be kept in mind.

### Room is occupied so book it:
Calling http://mydomain/occupied?room_id=00000 will check if there is a current room reservation that EventBoard is aware of. If there is a current reservation it will do nothing, if there is not then it will book the room using the Environment variables provided.

### Room is now empty, so end any events:
Calling http://mydomain/empty?room_id=00000 will grab the current event, and edit the endtime to now. 

## Comments
Please send any comments over that you may see fit, and thanks for checking out the little example application.

## Source Projects
Much of the flask specific items are borrowed from the example flaskr app. This application contains its own Licensing, and is provided with no warranty. In addition, its authors do not endorse this project in any way. But thanks you guys for providing a cool little example to work well with my little example.