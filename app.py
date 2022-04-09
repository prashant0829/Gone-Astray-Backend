# app.py
import json
import os
import cv2
import face_recognition
import pymongo
from bson import json_util
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
userTable = mydb["user"]
imageTable = mydb["images"]
# dblist = myclient.list_database_names()
# mydict = {"name": "John", "address": "Highway 37"}
x = userTable.find_one({"name": "John"})
print(bool(x))

# x = userTable.insert_one(mydict)

# print(myclient.list_database_names())

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'
# UPLOAD_FOLDER = 'test'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_image():
    print("you are here", request.files["file"].filename)
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')
        print(filename)
        return {"filename": filename}, 200
    else:
        flash('Allowed image types are - png, jpg, jpeg')
        return redirect(request.url)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    existing_user = userTable.find_one({"email": data["email"], "password": data["password"]})
    if existing_user:
        return {"email": existing_user["email"]}, 200
    else:
        return {"message": "Invalid Email or Password"}, 401


@app.route('/saveImageData', methods=['POST'])
def saveimagedata():
    data = request.get_json()

    image_data = imageTable.insert_one(data)
    print(image_data)
    return "Success", 200


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    existing_user = userTable.find_one({"email": data["email"]})
    if existing_user:
        return {"message": "User already exists"}, 401
    else:
        mydict = {"email": data["email"], "password": data["password"]}
        x = userTable.insert_one(mydict)
        return request.data, 200


@app.route('/getresultimages/<images>', methods=['GET'])
def getImages(images):
    fetched_images = imageTable.find({})
    json_docs = []
    for doc in fetched_images:

        image1 = face_recognition.load_image_file("static/uploads/" + doc["imageName"])
        image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
        image1encoding = face_recognition.face_encodings(image1)
        image1encoding = image1encoding[0]
        image2 = face_recognition.load_image_file("static/uploads/Prashant1.jpg")
        image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
        image2encoding = face_recognition.face_encodings(image2)[0]
        result = face_recognition.compare_faces([image1encoding], image2encoding)
        if result[0]:
            json_doc = json.dumps(doc, default=json_util.default)
            json_docs.append(json_doc)

    return {"images": json_docs}, 200


@app.route('/display/<filename>')
def display_image(filename):
    # print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == "__main__":
    app.run()
