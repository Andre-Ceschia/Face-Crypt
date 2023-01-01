from cv2 import CascadeClassifier
from cv2 import VideoCapture
from cv2 import cvtColor
from cv2 import COLOR_BGR2GRAY
from cv2 import CASCADE_SCALE_IMAGE
from cv2 import resize
from cv2 import waitKey
import os
import sys
from time import time
import numpy as np
import json
import keyring
import hashlib
import base64
from cryptography.fernet import Fernet
from Cryptodome.Cipher import AES
import platform
import subprocess
from colorama import Fore
from colorama import init
import getpass

# turns off tensorflow debugging output
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)

from keras_preprocessing import image
from keras.models import load_model

def resource_path(relative_path: str):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def decrypt(password: str = None, pepper: str = None):
    # prob put outfoler in json somehwere
    # loading the content of encrypted.json
    with open(resource_path(f'encrypted.json')) as file:
        json_content = json.load(file)

        encrypted_data = json_content['data'].encode('latin-1')
        encrypted_tag = json_content['tag'].encode('latin-1')
        encrypted_nonce = json_content['nonce'].encode('latin-1')

        title = json_content['file_name']
        file_type = json_content['file_type']
        out_folder = json_content['out']

    if password is None:
        # retrives the aes key and b64 encodes it
        key = keyring.get_password(title, 'key').encode()
    else:
        # creastes aes encryption key from password and pepper
        salt = 'aNdR3C3'
        to_encode = (salt + password + pepper).encode('latin-1')
        key = hashlib.sha256(to_encode).digest()

    # encode the key to base64
    key_b64 = base64.b64encode(key) 

    # loads encrypted data
    fernet = Fernet(key_b64)

    # decrypting tag and nonce
    try:
        # attempt to decrypt the fiel wiht the aes key
        # an error is thrown if the password is incorrect, or no password was inputted
        tag = fernet.decrypt(encrypted_tag)
        nonce = fernet.decrypt(encrypted_nonce)
        cipher = AES.new(key, AES.MODE_GCM, nonce)
    except:
        raise Exception('Error incorrect password was inputted!')

    # decrypting file 
    data = cipher.decrypt_and_verify(encrypted_data, tag) 
    slash = ''

    # writing decrypted data to out file
    if '/' in out_folder:
        slash =  '/'
    elif '\\' in out_folder:
        slash = '\\'
    elif out_folder != '':
        slash = '/'

    file_name = f'{out_folder}{slash}{title}.{file_type}'

    # outputting decrypted file
    with open(file_name, 'wb') as file:
        file.write(data)

    return file_name

def detect_user(profile: str):
    # initializing classifier and camera
    facial_classifier_path = 'haarcascade_frontalface_default.xml'

    facial_classifier = CascadeClassifier(resource_path(facial_classifier_path))

    camera = VideoCapture(0)

    if camera is None or not camera.isOpened():
        raise Exception('Access Denied No Webcam Detected!')

    # loads model
    model = load_model(resource_path(f'{profile}.h5'))

    comparisons = 0
    user_on_screen = 0
    start = time() 

    while True:
        # gets frame
        _, frame = camera.read()

        # converts to grayscale
        grayscale = cvtColor(frame, COLOR_BGR2GRAY)

        # get all faces in frame
        faces = facial_classifier.detectMultiScale(grayscale, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=CASCADE_SCALE_IMAGE)

        if len(faces) != 0:
            # for face in frame if the model predicts its the user increment the user_on_screen variable
            for (x, y, width, height) in faces:
                img = grayscale[y:y+height, x:x+width]
                img = resize(img, (150, 150))

                img = image.img_to_array(img)
                img = np.expand_dims(img, 0)

                val = model.predict(img, verbose=0)

                if val == 1:
                    user_on_screen += 1

        comparisons += 1

        waitKey(1)

        if time() - start > 1:
            camera.release()

            # get the amount of time that the user is on screen
            user_percentage = ( user_on_screen / comparisons ) * 100 

            # return whether the user has been on screen for atleast 70% of the time
            return (user_percentage > 70) 


def purge_file(path: str):
    # deletes file
    delete_command = ['rm', '\'' + path + '\'']

    if platform.system() == 'Windows':
        delete_command.insert(0, 'powershell.exe')

    subprocess.call(delete_command)

def denied():
    # access denied output
    print(f'Access {Fore.RED}DENIED{Fore.GREEN}.')
    print(f'Goodbye.')

if __name__ == '__main__':
    # initialize colorama
    init()

    print(f'{Fore.GREEN}', end='')

    # load contents of encrypted.json
    with open(resource_path('encrypted.json')) as file:
        json_content = json.load(file)
        profile = json_content['profile']
        use_pass = json_content['password']

    # if a password was used then ask for password 
    if use_pass:
        password = getpass.getpass(f'Password: ')
    else:
        password = None

    print(f'Analyzing user identity ...')

    # calling detect user function
    val = detect_user(profile)

    # creating pepper from detect user output
    if use_pass:
        pepper = str(int(val)) * 8
    else:
        pepper = None

    # if the detect_user is true then try and decrypt the file
    if val:
        try:
            decrypted_file_path = decrypt(password, pepper)
            print(f'Access Granted. Welcome {Fore.RED}{profile}{Fore.GREEN}.')
            input('Press enter when finished to purge the decrypted file from your system ...')
            purge_file(decrypted_file_path)
        except:
            denied()
    else:
        denied()


