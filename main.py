from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore
import starlette.status as status


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


def get_user(user_token):
    """Get or create user document.
    
    Gets a document that represents a user. Creates one if it does not exist.
    """
    user = firestore_db.collection("users").document(user_token['user_id'])
    if not user.get().exists():
        user_data = {
            'email':user_token['email'], 
            'galleries': [],
        }
        firestore_db.collection("users").document(user_token['user_id']).set(user_data)
    return user


def create_gallery(gallery_name: str, user_document):
    """Create a gallery.
    
    Create a gallery and return the gallery reference.
    """
    gallery_ref = firestore_db.collection("galleries").document()
    gallery_ref.set({
        "name": gallery_name,
        "images": []
    })
    return gallery_ref


def add_gallery_to_user(gallery_ref, user_document):
    """Add a gallery to a user."""
    galleries = user_document.get().get('galleries')
    galleries.append(gallery_ref)
    user_document.update({'galleries': galleries})
    return user_document


def get_galleries(user_document):
    """Get user galleries"""
    galleries = []
    for gallery in user_document.get('galleries'):
        galleries.append(gallery.get())
    return galleries


def create_image(image_url):
    """Create an image document.
    
    Creates an image document and returns the image reference.
    """
    image_ref = firestore_db.collection("images").document()
    image_ref.set({
        "url": image_url
    })
    return image_ref


def add_image_to_gallery(image_ref, gallery_ref):
    """Add an image to a gallery.
    
    Add an image to a gallery and return the gallery reference.
    """
    images = gallery_ref.get().get('images')
    images.append(image_ref)
    gallery_ref.update({'images': images})
    return gallery_ref


# I don't really understand task number 2 in the first group of tasks
# where I'm supposed to generate firestore document collections to represent
# users, galleries and images. This is because firestore will implicitly create
# the collections when we create the first document in each category.
# For example, the users collection will be created when we create the first
# user, the same will happen for gallery and image document collections.
# But for the sake of completeness and to avoid risking my work not being
# corrected, I've included an initialize route that will create dummy documents
# of each kind, effectively creating document collections to represent users,
# galleries and images
@app.get("/initialize", response_class=RedirectResponse)
async def initialize(request: Request):
    dummy_user_token = {
        "user_id":"dummyuserid",
        "email":"dummy@dummy.com"
    }
    # create a dummy user, image and gallery
    dummy_user = get_user(dummy_user_token)
    dummy_image_ref = create_image("https://picsum.photos/200/300")
    dummy_gallery_ref = create_gallery("dummy_gallery")

    # add image to gallery then attach the gallery to the user
    dummy_gallery_ref = add_image_to_gallery(dummy_image_ref, dummy_gallery_ref)
    dummy_user = add_gallery_to_user(dummy_gallery_ref, dummy_user)

    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


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
    
    # get user document
    user = get_user(user_token).get()

    # get user galleries
    galleries = get_galleries(user)
    
    # render template with user_token after successful validation
    return templates.TemplateResponse(
        "main.html", 
        {
            "request": request, 
            "user_token": user_token, 
            "user_info": user,
            "galleries": galleries,
            "error_message": None,
        },
    )
