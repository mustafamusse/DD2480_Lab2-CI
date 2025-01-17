##### IMPORTS #####

from flask import Flask, request, json
import os
import sys

from modules.compilation import compile
from modules.notification import notify
from modules.test import test

##### SETTINGS #####

STATUS_DEBUG = True
HOST = "127.0.0.1"
PORT = 8080

PATH_REPO = str(os.getcwd()) # Folder within CWD to run the code.

##### PROGRAM #####

app = Flask(__name__) # Variable for flask server application, to be called upon.

# Create an endpoint which receives requests from the GitHub API.
@app.route('/', methods=['POST']) # Triggered by URL localhost:5000/
def handler_Push():

    TOKEN = sys.stdin.readline()
    data = request.json # Request the data from the event.

    message, code = notify(data, "pending", TOKEN)
    
    if code > 0 or code < 0: # Error occured!
        # Set github status.
        notify(data, "failure", TOKEN)
        return message + ' ' + str(code)

    print("Received PUSH event from webhook!") # Debug print.

    # Step 1: Clone the repository.
    repo = data["repository"]["clone_url"] # Fetches the clone URL from the payload.
    name = data["repository"]["name"]
    branch = data["ref"].split('/')[2]

    os.chdir(PATH_REPO)
    os.system("git clone " + '-b ' + branch + ' ' + repo) # Runs command to clone the repository.

    # Run module that compiles.

    print(str(os.getcwd()) + '/' + name)

    message, code = compile(PATH_REPO + '/' + name)

    if code > 0 or code < 0: # Error occured!
        # Set github status.
        notify(data, "failure", TOKEN)
        return message + ' ' + str(code)

    # Run module that tests.

    message, code = test(PATH_REPO + '/' + name)

    if code > 0 or code < 0: # Error occured!
        # Set github status.
        notify(data, "failure", TOKEN)
        return message + ' ' + str(code)

    notify(data, "success", TOKEN)

    return "OK " + message + ' ' + str(code)


# Start the Flask web server.
if __name__ == '__main__':
    app.run(debug=STATUS_DEBUG, host=HOST, port=PORT)
    
