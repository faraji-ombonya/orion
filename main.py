from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore, storage
import starlette.status as status
import local_constants
import uuid
from pathlib import Path
import mimetypes

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
    user_ref = firestore_db.collection("users").document(user_token['user_id'])
    if not user_ref.get().exists:
        user_data = {
            'email':user_token['email'], 
            'galleries': [],
        }
        firestore_db.collection("users").document(user_token['user_id']).set(user_data)
    return user_ref


def create_gallery(gallery_name: str, user_ref):
    """Create a gallery.
    
    Create a gallery and return the gallery reference. Raise a value
    error if a gallery with the same name exists.
    """
    # check if the gallery name exists
    for gallery in user_ref.get().get('galleries'):
        if gallery.get().get("name") == gallery_name:
            raise ValueError("A gallery with a similar name exists")

    gallery_ref = firestore_db.collection("galleries").document()
    gallery_ref.set({
        "name": gallery_name,
        "images": []
    })
    return gallery_ref


def add_gallery_to_user(gallery_ref, user_ref):
    """Add a gallery to a user."""
    galleries = user_ref.get().get('galleries')
    galleries.append(gallery_ref)
    user_ref.update({'galleries': galleries})
    return user_ref


def get_galleries(user_ref):
    """Get user galleries"""
    galleries = []
    for gallery in user_ref.get().get('galleries'):
        galleries.append(gallery.get())
    return galleries


def get_gallery_refs(user_ref):
    """Get user gallery refs"""
    gallery_refs = []
    for gallery in user_ref.get().get('galleries'):
        gallery_refs.append(gallery)
    return gallery_refs


def validate_gallery_name(gallery_name, gallery_refs, index):
    for i in range(len(gallery_refs)):
        if i == index:
            continue

        gallery = gallery_refs[i].get()

        if gallery.get("name") == gallery_name:
            raise ValueError("A gallery with the same name exists")


def validate_image(file):
    """Validate an image."""
    allowed_extensions = [".jpg", ".jpeg", ".png"]
    extension = Path(file.filename).suffix
    if file.filename == "":
        return False
    if extension not in allowed_extensions:
        return False
    return True


def upload_image(file):
    """Upload image to the storage bucket."""
    storage_client = storage.Client(project=local_constants.PROJECT_NAME)
    bucket = storage_client.bucket(local_constants.PROJECT_STORAGE_BUCKET)

    # generate random file names
    extension = Path(file.filename).suffix
    file_name = f"{str(uuid.uuid4())}{extension}"
    blob = storage.Blob(file_name, bucket)
    
    blob.upload_from_file(file.file)
    blob.make_public()
    return blob.public_url
    

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


def get_image_refs(gallery_ref):
    """Get image refs"""
    return gallery_ref.get().get('images')


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
    dummy_gallery_ref = create_gallery("dummy_gallery", dummy_user)

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
    user_ref = get_user(user_token)
    user = user_ref.get()

    # get user galleries
    galleries = get_galleries(user_ref)
    
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


@app.post('/gallery', response_class=RedirectResponse)
async def handle_create_gallery(request: Request):
    # get and validate token
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/")
    
    user_ref = get_user(user_token)

    # get gallery name from the form
    form = await request.form()
    gallery_name = form['gallery_name']

    try:
        gallery_ref = create_gallery(gallery_name, user_ref)
        user_ref = add_gallery_to_user(gallery_ref, user_ref)
    except ValueError as e:
        print(str(e))

    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.get('/gallery/{index}', response_class=HTMLResponse)
async def handle_get_gallery(request: Request, index: int):
    # get and validate token
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/")
    
    user_ref = get_user(user_token)
    gallery_refs = get_gallery_refs(user_ref)
    gallery_ref = gallery_refs[index]

    image_refs = gallery_ref.get().get("images")

    images = []
    for ref in image_refs:
        images.append(ref.get())

    return templates.TemplateResponse(
        "gallery.html", 
        {
            "request": request, 
            "user_token": user_token, 
            "user_info": user_ref.get(),
            "gallery": gallery_ref.get(),
            "gallery_index": index,
            "error_message": None,
            "images": images,
        },
    )


@app.post('/update-gallery-name', response_class=RedirectResponse)
async def handle_update_gallery_name(request: Request):
    # get and validate token
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/")
    
    # get new gallery name and index from the form
    form =  await request.form()
    gallery_name = form['gallery_name']
    index = int(form['index'])

    user_ref = get_user(user_token)
    gallery_refs = get_gallery_refs(user_ref)

    try:
        validate_gallery_name(gallery_name, gallery_refs, index)
    except ValueError as e:
        print(str(e))
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    gallery_ref = gallery_refs[index]
    gallery_ref.update({"name": gallery_name})
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.post('/delete-gallery', response_class=RedirectResponse)
async def handle_delete_gallery(request: Request):
    # get and validate token
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/")
    
    # get gallery index from the form
    form =  await request.form()
    index = int(form['index'])

    user_ref = get_user(user_token)
    gallery_refs = get_gallery_refs(user_ref)
    gallery_ref = gallery_refs[index]
    gallery_ref.delete()
    del gallery_refs[index]

    user_ref.update({"galleries": gallery_refs})
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)


@app.post("/gallery/{index}/image", response_class=RedirectResponse)
async def handle_upload_image(request: Request, index: int):
    # get and validate token
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/")
    
    form = await request.form()
    file = form['file_name']
    
    if not validate_image(file):
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)

    image_url = upload_image(form['file_name'])
    image_ref = create_image(image_url)
    
    user_ref = get_user(user_token)
    gallery_refs = get_gallery_refs(user_ref)
    gallery_ref = gallery_refs[index]
    gallery_ref = add_image_to_gallery(image_ref, gallery_ref)
    
    return RedirectResponse(f"/gallery/{index}", status_code=status.HTTP_302_FOUND)


@app.post("/gallery/{gallery_index}/image/{image_index}/delete", response_class=RedirectResponse)
async def handle_delete_image(request: Request, gallery_index: int, image_index: int):
    # get and validate token
    id_token = request.cookies.get("token")
    user_token = validate_firebase_token(id_token)
    if not user_token:
        return RedirectResponse("/")   

    user_ref = get_user(user_token)
    gallery_refs = get_gallery_refs(user_ref)
    gallery_ref = gallery_refs[gallery_index]
    image_refs = get_image_refs(gallery_ref) 
    image_refs[image_index].delete()
    del image_refs[image_index]

    gallery_ref.update({"images": image_refs})
    return RedirectResponse(f"/gallery/{gallery_index}", status_code=status.HTTP_302_FOUND)
