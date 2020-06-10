import pyrebase
from os.path import dirname, abspath
from pathlib import Path
class Firebase():
    def __init__(self, token):
        parent = dirname(dirname(abspath(__file__)))
        firebase_config = {
        'apiKey': token,
        'authDomain': "wishlist-project-77ef4.firebaseapp.com",
        'databaseURL': "https://wishlist-project-77ef4.firebaseio.com",
        'projectId': "wishlist-project-77ef4",
        'storageBucket': "wishlist-project-77ef4.appspot.com",
        'messagingSenderId': "547319689136",
        'appId': "1:547319689136:web:5c84b34bfadcc43c7ab075",
        'serviceAccount': parent + "/wishlist-project-77ef4-firebase-adminsdk-27u38-d55ef4d3f0.json"
        }  
        firebase = pyrebase.initialize_app(firebase_config)
        self.firebasedb = firebase.database()