from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore


#  app that will contain routing for fast API
app = FastAPI()


# firestore client to interact with firestore database
firestore_db = firestore.Client()


# request object to talk to firebase for verifying user logins
firebase_request_adapter = requests.Request()


# static and template directories
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory="templates")


def validate_firebase_token(id_token):
    """Validate firebase token.

    Validate firebase token and return user_token if valid, None otherwise.
    """
    if not id_token:
        return None
    
    user_token = None
    try:
        user_token = google.oauth2.id_token.verify_firebase_token(
            id_token, firebase_request_adapter)
    except ValueError as err:
        print("An error occured while validating firebase token: ", str(err))

    return user_token


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    user_token = None

    # get and validate id_token
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return templates.TemplateResponse(
            'main.html', 
            {
                'request': request, 
                'user_token': None, 
                'error_message': None, 
                'user': None,
            },
        )
    
    # render template with user_token after successful validation
    return templates.TemplateResponse(
        "main.html", 
        {
            "request": request, 
            "user_token": user_token, 
            "error_message": None,
        },
    )
