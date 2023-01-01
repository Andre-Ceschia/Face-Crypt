import cv2
import os
import platform
import subprocess
import hashlib
from Cryptodome.Cipher import AES
from cryptography.fernet import Fernet
import keyring
import base64
import random
import json

# hiding tensorflow debugging information
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from keras_preprocessing.image import ImageDataGenerator
from keras.layers import Conv2D
from keras.layers import MaxPool2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.optimizers import RMSprop
from keras.models import Sequential

def create_dataset(name: str, max_pics: int, delete: bool = False):

    # gets the platform of the user
    system_name = platform.system() 

    if delete:
        # initizalizes the command used to delete the folder
        delete_command = ['rm', '-r', f'data/{name}']

        # uses powershell if the user is on windows
        if system_name == 'Windows':
            delete_command.insert(0, 'powershell.exe')

        # executes the command
        subprocess.call(delete_command)

    # gets the contents of name 
    data_contents = os.listdir(f'data') 

    # if no folder exists in data create one
    if name not in data_contents:
        make_command = ['mkdir', f'data/{name}']
        copy_command = ['cp', '-R', 'data/other', f'data/{name}']

        if system_name == 'Windows':
            make_command.insert(0, 'powershell.exe')
            copy_command.insert(0, 'powershell.exe')
            
        subprocess.call(make_command, stdout=subprocess.DEVNULL)

        make_command[-1] = f'data/{name}/user'

        subprocess.call(make_command, stdout=subprocess.DEVNULL)
        subprocess.call(copy_command, stdout=subprocess.DEVNULL)

    name_contents = os.listdir(f'data/{name}')

    # if there exists a h5 profile for the user delete it
    if f'{name}.h5' in name_contents:
        delete_command = ['rm', f'data/{name}/{name}.h5'] 

        if system_name == 'Windows':
            delete_command.insert(0, 'powershell.exe')

        subprocess.call(delete_command)

    # initlizes the classifier being used
    facial_classifier_path = 'haarcascade_frontalface_default.xml'

    facial_classifier = cv2.CascadeClassifier(facial_classifier_path)

    # starts the camera
    camera = cv2.VideoCapture(0)

    # variable initialization
    PRINT_STEP = 100
    DELAY_MS = 30
    name_counter = 0 
    counter = 0

    for item in os.listdir(f'data/{name}/user'):
        num = int(item[:-4])
        if num > name_counter:
            name_counter = num

    if name_counter != 0:
        name_counter += 1

    while True:
        # reads camera fream
        _, frame = camera.read()

        # converts to grayscale
        grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # detects faces in frame
        faces = facial_classifier.detectMultiScale(grayscale_frame, scaleFactor=1.1, minNeighbors=5, flags=cv2.CASCADE_SCALE_IMAGE, minSize=(30, 30))

        for (x, y, width, height) in faces:
            # draws rectanle around all faces and moves that picture to its respective folder
            cropped = grayscale_frame[y:y+height, x:x+width]
            cropped = cv2.resize(cropped, (150, 150))

            cv2.imwrite(f'data/{name}/user/{name_counter}.png', cropped)

            counter += 1
            name_counter += 1

            cv2.rectangle(frame, (x, y), (x+width, y+height), (0, 0, 255), 2)

        if counter % PRINT_STEP == 0:
            print(f'Process is {round((counter / max_pics) * 100, 2)}% complete.')

        # shows window
        cv2.imshow('Facial Detecting', frame)
        
        # when to quit out of the loop
        if cv2.waitKey(DELAY_MS) == ord('q') or counter >= max_pics:
            break

    camera.release()
    cv2.destroyAllWindows()

def train_model(name: str):
    # initailizng ImageDataGenerator to rescale and split the dataset for training and validating
    train = ImageDataGenerator(rescale=1/255, validation_split=0.2)

    # initilzaes training set
    train_dataset = train.flow_from_directory(
        directory=f'data/{name}',
        target_size=(150, 150),
        color_mode='grayscale',
        class_mode='binary',
        batch_size=10,
        subset='training',
        shuffle=True,
        classes={
            'other': 0,
            'user': 1 
        }
    )

    # initizlizes validation set
    validation_dataset = train.flow_from_directory(
        directory=f'data/{name}',
        target_size=(150, 150),
        color_mode='grayscale',
        class_mode='binary',
        batch_size=10,
        shuffle=True,
        classes={
            'other': 0,
            'user': 1 
        },
        subset='validation'
    )

    # creating model architechture
    model = Sequential([
        Conv2D(16, (3, 3), activation='relu', input_shape=(150, 150, 1)),
        MaxPool2D(),

        Conv2D(32, (3, 3), activation='relu'),
        MaxPool2D(),

        Conv2D(64, (3, 3), activation='relu'),
        Flatten(),

        Dense(512, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    # compling model
    model.compile(optimizer=RMSprop(), metrics=['accuracy'], loss='binary_crossentropy')

    # training model
    model.fit(train_dataset, steps_per_epoch=5, epochs=30, validation_data=validation_dataset)

    # saving model
    model.save(f'data/{name}/{name}.h5')

def get_file_name(path: str):
    # returns title of file without extenstion
    if '.' not in path:
        return path
    else:
        return path[:path.index('.')]

def get_file_type(path: str):
    # returns file type
    if '.' not in path:
        return None
    else:
        return path[path.index('.') + 1:]

# for the setup file
def encrypt(path: str, password: str = None):
    if password is None:
        # if no password is inputted create random aes key
        key = ''.join([chr(random.randint(33, 126)) for i in range(32)]).encode('latin-1')
    else:
        # if a password is inputted hash the password with a sha256 hashing algorithim and use the output as the aes key
        salt = 'aNdR3C3'
        pepper = '1' * 8
        to_encode = (salt + password + pepper).encode('latin-1')
        key = hashlib.sha256(to_encode).digest()

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

    file_name = get_file_name(path)
    file_type = get_file_type(path)

    if '\\' in file_name:
        file_name = file_name.split('\\')[-1]
    elif '/' in file_name:
        file_name = file_name.split('/')[-1]

    if password is None:
        # if password is not used put the random aes key in keyring
        keyring.set_password(file_name, 'key', key.decode('latin-1'))

    # json info to write to encrypted.json
    json_dict = {
        'data': encrypted_data.decode('latin-1'),
        'tag': encrypted_tag.decode('latin-1'),
        'nonce': encrypted_nonce.decode('latin-1'),
        'file_name': file_name,
        'file_type': file_type 
    }

    # dumps the encrypted data to a json file
    with open(f'encrypted.json', 'w') as file:
        json.dump(json_dict, file)
