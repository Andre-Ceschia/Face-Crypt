import cv2
import os
import platform
import subprocess
import hashlib
from Cryptodome.Cipher import AES
from cryptography.fernet import Fernet
import base64
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
    PRINT_STEP = max_pics // 12
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

def get_key(salt: str, password: str, pepper: str) -> bytes:
    to_encode = salt + password + pepper
    to_encode = to_encode.encode('latin-1')

    return hashlib.sha256(to_encode).digest()

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
    if not os.path.isdir(path) or not os.path.isdir(outpath):
        raise Exception('Error path does not exists')

    # encrypt the directory and everyting in it and return a heriachal dictionary
    encrypted_hierarchy = encrypt_dir(path, key, slash)

    # write output of the encrypt dir function to a json file 
    with open('encrypted.json', 'w') as file:
        json.dump(encrypted_hierarchy, file, indent=4)

    # base 64 encodes key and encrypts the name of the directory
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
    with open('info.json', 'w') as file:
        json.dump(info_out, file, indent=4)

