import json
from datetime import datetime
from typing import Callable, Any, Awaitable

import requests
from h2o_wave import Q, ui, on, handle_on

import os


# load .env file
def load_env_file(env_path: str = '.env'):
    if os.path.exists(env_path):

        with open(env_path) as f:
            for line in f:
                if line.startswith('#') or line == '\n':
                    continue
                key, value = line.strip().split('=', 1)
                os.environ[key] = value
    else:
        print(f"File does not exist: {env_path}")
        raise FileNotFoundError(f"File does not exist: {env_path}")


load_env_file("/home/ruben/PycharmProjects/LeaguesManager/.env")
# At the top of your file after other imports
FIREBASE_CONFIG = {
    "apiKey": os.environ.get("FIREBASE_API_KEY"),
    "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.environ.get("FIREBASE_DATABASE_URL"),
    "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
    "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.environ.get("FIREBASE_APP_ID"),
    "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID"),

}


def authenticate_with_firebase(email, password):
    endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_CONFIG['apiKey']}"
    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    response = requests.post(endpoint, data=json.dumps(data))
    response_data = response.json()
    if 'idToken' in response_data:
        return response_data['idToken']
    else:
        # Handle error
        return None


def check_token_validity(idToken):
    endpoint = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_CONFIG['apiKey']}"
    data = {"idToken": idToken}
    response = requests.post(endpoint, data=json.dumps(data))
    return (response.status_code == 200)



# var_firebaseConfig = f'''var firebaseConfig = {FIREBASE_CONFIG};'''
# scripts = [
#     # Add Firebase scripts
#     ui.script(path='https://www.gstatic.com/firebasejs/8.0.0/firebase-app.js'),
#     ui.script(path='https://www.gstatic.com/firebasejs/8.0.0/firebase-auth.js'),
#     # Add inline script for your authentication function
#     ui.script(var_firebaseConfig +
#               '''
#               console.log("Script is running");
#               firebase.initializeApp(firebaseConfig);
#               console.log("Firebase initialized");
#               function loginWithFirebase() {
#                       var email = document.getElementById("email").value;
#                       var password = document.getElementById("password").value;
#
#                       if (isLogin) {
#                           firebase.auth().signInWithEmailAndPassword(email, password)
#                               .then((userCredential) => {
#                                   var user = userCredential.user;
#                                   user.getIdToken().then((token) => {
#                                       Wave.emit('token_received', {token: token});
#                                   });
#                               })
#                               .catch((error) => {
#                                   alert("Error signing in: " + error.message);
#                               });
#                       } else {
#                           firebase.auth().createUserWithEmailAndPassword(email, password)
#                               .then((userCredential) => {
#                                   // Signed up successfully
#                                   var user = userCredential.user;
#                                   user.getIdToken().then((token) => {
#                                       Wave.emit('token_received', {token: token});
#                                   });
#                               })
#                               .catch((error) => {
#                                   alert("Error signing up: " + error.message);
#                               });
#                       }
#                   }
#           '''
#               ),
# ]