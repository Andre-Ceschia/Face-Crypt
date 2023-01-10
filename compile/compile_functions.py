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
import hashlib
import base64
from cryptography.fernet import Fernet
from Cryptodome.Cipher import AES
import platform
import subprocess

from keras_preprocessing import image
from keras.models import load_model

def resource_path(relative_path: str):
    # gets path of file 
    # used so when compiled data can still be accessed
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def make_dir(name: str, path: str, slash: str):
    # path name to use in command
    new_path = path + slash + name

    command = ['mkdir', new_path]

    if platform.system() == 'Windows':
        command.insert(0,'powershell.exe')

    # created directory
    subprocess.call(command, stdout=subprocess.DEVNULL)

def purge_file(path: str):
    # deletes file
    delete_command = ['rm', '-r' , path]

    if platform.system() == 'Windows':
        delete_command.insert(0, 'powershell.exe')

    subprocess.call(delete_command)

def get_key(salt: str, password: str, pepper: str) -> bytes:
    # concatinating the salt, password, and pepper
    to_encode = salt + password + pepper
    # encoding the string in latin-1 encoding
    to_encode = to_encode.encode('latin-1')

    # hash to_encode and return the bytes
    return hashlib.sha256(to_encode).digest()

def verify(key: bytes, encrypted_data: bytes):
    try:
        # base64 encode the key
        b64_key = base64.b64encode(key)

        fernet = Fernet(b64_key)

        # decrypt data if it throws an error return 0
        data = fernet.decrypt(encrypted_data).decode('latin-1')

        # return data
        return data
    except:
        return 0

def decrypt_file(key: bytes, data_in: tuple, path: str, slash: str):
    # unpacking encrypted data, tag, nonce, and file na me
    encrypted_data, encrypted_tag, encrypted_nonce, file_name = data_in

    # encoding with latin-1
    encrypted_data = encrypted_data.encode('latin-1')
    encrypted_tag = encrypted_tag.encode('latin-1')
    encrypted_nonce = encrypted_nonce.encode('latin-1')

    # encode the key to base64
    key_b64 = base64.b64encode(key) 

    # creates fernet instance
    fernet = Fernet(key_b64)

    # decrypting tag and nonce
    try:
        # attempt to decrypt the fiel wiht the aes key
        # an error is thrown if the password is incorrect
        tag = fernet.decrypt(encrypted_tag)
        nonce = fernet.decrypt(encrypted_nonce)
        cipher = AES.new(key, AES.MODE_GCM, nonce)
    except:
        raise Exception('Error incorrect password was inputted!')

    # decrypting file 
    data = cipher.decrypt_and_verify(encrypted_data, tag) 

    # path to write to
    file_path = path + slash + file_name

    # outputting decrypted file
    with open(file_path, 'wb') as file:
        file.write(data)

def decrypt_dir(key: bytes, path: str, dir_dict: dict, slash: str):
    # loops through every directory in dictionary
    for encrypted_dir in dir_dict:
        # created directory
        make_dir(encrypted_dir, path, slash)

        # initaizing new path to use below
        curr_path = path + slash + encrypted_dir

        # if files exist in this directory
        if 'files' in dir_dict[encrypted_dir]:

            # for encrypted file in files 
            for encrypted_file in dir_dict[encrypted_dir]['files']:
                
                # calling decrypt_file on file
                encrypted_file = tuple(encrypted_file)
                decrypt_file(key, encrypted_file, curr_path, slash)

        # if directories exist in this directory
        if 'dirs' in dir_dict[encrypted_dir]:

            # for every directory in dirs
            for my_dir in dir_dict[encrypted_dir]['dirs']:

                # recursivley called decrypt_dir
                decrypt_dir(key, curr_path, my_dir, slash)

def decrypt(key: bytes, outpath: str):
    # loading data in encrypted.json
    with open(resource_path('encrypted.json')) as file:
        encrypted_dict = json.load(file)

    # initializing slash to be used in paths
    if '\\' in outpath:
        slash = '\\'
    else: 
        slash = '/'

    # full path used for return value
    full_path = outpath + slash + list(encrypted_dict.keys())[0]

    try:
        # calling decrypt dir on the main directory 
        decrypt_dir(key, outpath, encrypted_dict, slash)
    except:
        # if an error is thrown delete directory and return 0
        purge_file(full_path)

        return 0 

    # return 1 name if decrypt exits with no error
    return full_path

# for the setup file
def encrypt_file(path: str, key: bytes, slash: str):
    # encodes the key to base64
    key_b64 = base64.b64encode(key)

    # reads byte data from specified path
    with open(path, 'rb') as file:
        data = file.read()
    
    # initializes encrypts the contents of the inputted file 
    cipher = AES.new(key, AES.MODE_GCM)
    encrypted_data, tag = cipher.encrypt_and_digest(data)
    nonce = cipher.nonce

    # encrypting aes nonce and tag
    fernet = Fernet(key_b64)

    encrypted_tag = fernet.encrypt(tag)
    encrypted_nonce = fernet.encrypt(nonce)

    # getting name of file from path
    if slash in path:
        file_name = path.split(slash)[-1]
    else:
        file_name = path.split

    # returning a tuple contating the encrypteted data, tag, nonce, and file name
    return encrypted_data.decode('latin-1'), encrypted_tag.decode('latin-1'), encrypted_nonce.decode('latin-1'), file_name

def encrypt_dir(path: str, key: bytes, slash: str):
    # gets directory name
    if slash in path:
        dir_name = path.split(slash)[-1]
    else:
        dir_name = path

    # initailziing return dictionary
    json_info = {
        dir_name: {}
    }

    # for every item in the inputted path
    for item in os.listdir(path):
        # formatting file path
        item_path = path + slash + item

        # if item is a file encrypt the file and append the tuple to the files list in the json info dictionary
        if os.path.isfile(item_path):
            if 'files' not in json_info[dir_name]:
                json_info[dir_name]['files'] = []

            json_info[dir_name]['files'].append(encrypt_file(item_path, key, slash))

        # if item is a direcotry recursivley call encrypt_dir and append the return value to the dirs list in the json info dictionary
        elif os.path.isdir(item_path):
            if 'dirs' not in json_info[dir_name]:
                json_info[dir_name]['dirs'] = []

            json_info[dir_name]['dirs'].append(encrypt_dir(item_path, key, slash))

    return json_info

def encrypt(path: str, key: bytes, profile: str, outpath: str = '.'):
    # determining what slash to use when dealing with paths
    if '\\' in path:
        slash = '\\'
    else:
        slash = '/'

    # if path does not exist raise exception
    if not os.path.isdir(path):
        raise Exception('Error path does not exists')

    # encrypt the directory and everyting in it and return a heriachal dictionary
    encrypted_hierarchy = encrypt_dir(path, key, slash)

    # write output of the encrypt dir function to a json file 
    with open(resource_path('encrypted.json'), 'w') as file:
        json.dump(encrypted_hierarchy, file, indent=4)

    # base64 encode teh key encrypt the name of the directory
    b64_key = base64.b64encode(key)
    fernet = Fernet(b64_key)

    encrypted_outpath = fernet.encrypt(outpath.encode('latin-1'))

    name = path.split(slash)[-1]

    info_out = {
        'outpath': encrypted_outpath.decode('latin-1'),
        'profile': profile,
        'name': name
    }

    # write info_out to info.json
    with open(resource_path('info.json'), 'w') as file:
        json.dump(info_out, file, indent=4)

def detect_user(profile: str):
    # initializing classifier and camera
    facial_classifier_path = resource_path('haarcascade_frontalface_default.xml')

    facial_classifier = CascadeClassifier(facial_classifier_path)

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

