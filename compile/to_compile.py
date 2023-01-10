import os
import json
import platform
import subprocess
from colorama import Fore
from colorama import init
import getpass
import base64
from cryptography.fernet import Fernet
import sys

# turns off tensorflow debugging output
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import logging
logging.getLogger('tensorflow').setLevel(logging.ERROR)

from compile_functions import detect_user
from compile_functions import decrypt
from compile_functions import encrypt
from compile_functions import resource_path
from compile_functions import verify
from compile_functions import get_key
from compile_functions import purge_file

def denied():
    # access denied output
    print(f'Access {Fore.RED}DENIED{Fore.GREEN}.')
    print(f'Goodbye.')
    sys.exit()

def art():
    # prints logo and commands
    print(f'{Fore.GREEN}', end='')

    print('███████╗░█████╗░░█████╗░███████╗░░░░░░░█████╗░██████╗░██╗░░░██╗██████╗░████████╗')
    print('██╔════╝██╔══██╗██╔══██╗██╔════╝░░░░░░██╔══██╗██╔══██╗╚██╗░██╔╝██╔══██╗╚══██╔══╝')
    print('█████╗░░███████║██║░░╚═╝█████╗░░█████╗██║░░╚═╝██████╔╝░╚████╔╝░██████╔╝░░░██║░░░')
    print('██╔══╝░░██╔══██║██║░░██╗██╔══╝░░╚════╝██║░░██╗██╔══██╗░░╚██╔╝░░██╔═══╝░░░░██║░░░')
    print('██║░░░░░██║░░██║╚█████╔╝███████╗░░░░░░╚█████╔╝██║░░██║░░░██║░░░██║░░░░░░░░██║░░░')
    print('╚═╝░░░░░╚═╝░░╚═╝░╚════╝░╚══════╝░░░░░░░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░░░░░░░╚═╝░░░')

    print(f'\n{Fore.RED}Decrypt{Fore.GREEN} - Decrypts users encrypted directory.')
    print(f'\n{Fore.RED}Change{Fore.GREEN} - Prompts the user to change the outpath of the encrypted directory.')
    print(f'\n{Fore.RED}Update{Fore.GREEN} - Updates encrypted directory with the current contents of the decrypted directory.')
    print(f'\n{Fore.RED}Purge{Fore.GREEN} - Purges decrypted directory from system.')
    print(f'\n{Fore.RED}Clear{Fore.GREEN} - Clears screen.')
    print(f'\n{Fore.RED}Exit{Fore.GREEN} - Exits Face-Crypt CLI.')

def clear(show_art: bool = False):
    # clearing screen and showing logo and commands depending on the show_art boolean
    commands = ['clear']
    system_name = platform.system()

    if system_name == 'Windows':
        commands.insert(0, 'powershell.exe')

    subprocess.call(commands)

    if show_art:
        art()

def get_user_input():
    # returns user input with prompt
    return input(f'\n{Fore.BLUE}fcry{Fore.GREEN} > ').strip().lower()

def change_outpath(key: bytes):
    # getting new outpath from user
    newpath = input('\nEnter new path: ').strip().encode('latin-1')

    print('\nAttemping to Encrypt ... ')

    # if path does not exist return 0
    if not os.path.isdir(newpath):
        return 0

    # base64 encoding the key
    b64_key = base64.b64encode(key)

    fernet = Fernet(b64_key)

    # encrypting the new outpath
    encrypted_path = fernet.encrypt(newpath)

    # loading data from info.json and changing the outpath
    with open(resource_path('info.json')) as file:
        content = json.load(file)
        content['outpath'] = encrypted_path.decode('latin-1')

    # writing the new encrypted outpath to info.json
    with open(resource_path('info.json'), 'w') as file:
        json.dump(content, file, indent=4)

    print(f'\nOutpath {Fore.RED}Sucessfully{Fore.GREEN} Changed.')

    # returning new path 
    return newpath.decode('latin-1')

def update(key: bytes, outpath: str, profile: str, name: str, slash: str):
    # concatanating path to directory
    path = outpath + slash + name

    # calling the encrypt function on the directory
    encrypt(path, key, profile, outpath)

if __name__ == '__main__':
    # initialize colorama
    init()

    print(f'{Fore.GREEN}', end='')

    # load contents of info.json
    with open(resource_path('info.json')) as file:
        json_content = json.load(file)
        profile = json_content['profile']
        encrypted_outpath = json_content['outpath'].encode('latin-1')
        name = json_content['name']

    # asking user for the password
    password = getpass.getpass('Password: ')

    print('Analyzing user identity ...')

    # calling detect user function
    val = detect_user(profile)

    # creating pepper from detect user output
    pepper = str(int(val)) * 8
    salt = 'aNdR3C3'

    # hashing key 
    key = get_key(salt, password, pepper)

    # if the detect_user is true then try and decrypt the file
    if val:
        # verifying the inputted password and identity of the user
        outpath = verify(key, encrypted_outpath)

        if not outpath:
            denied()
        else:
            print(f'Access Granted. Welcome {Fore.RED}{profile}{Fore.GREEN}.')

    else:
        denied()
    
    # retrieving slash type from outpath
    if '\\' in outpath:
        slash = '\\'
    else: 
        slash = '/'

    # If outpath does not exist then outpath is the path of the executable
    if not os.path.isdir(outpath):
        outpath = '.'

    clear(True)

    while True:
        # retrieving user input
        user_input = get_user_input()

        if user_input == 'decrypt':
            print('\nAttemping to Decrypt ... ')
            
            # send user a warning if directory already exists
            if os.path.isdir(outpath + slash + name):
                val = input(f'\nWarning {Fore.RED}{outpath + slash + name}{Fore.GREEN} already exists. Do you wish to overwrite it? (Y/N): ').strip().lower()

                if val != 'y': 
                    continue

            # calling the decrypt function
            decrypt(key, outpath)
            print(f'\nDecryption {Fore.RED}Sucessful{Fore.GREEN}. {Fore.RED}{name}{Fore.GREEN} has been written to {Fore.RED}{outpath}{Fore.GREEN}.')

        elif user_input == 'update':
            validation = input('\nAre you sure you want to update the encrypted directory? (Y/N): ').strip().lower()

            if validation != 'y':
                continue

            print('\nAttemping to Encrypt ... ')
            
            # if path does not exist throw an error and continue the loop
            if not os.path.isdir(outpath + slash + name):
                print(f'\n{Fore.RED}ERROR!{Fore.GREEN} Path does not exist!')
                continue

            # calling the update function
            update(key, outpath, profile, name, slash)

            print(f'\nEncryption {Fore.RED} Sucessful{Fore.GREEN}.')

        elif user_input == 'purge':
            validation = input('\nAre you sure you want to purge? (Y/N): ').strip().lower()

            if validation != 'y':
                continue
 
            # if path does not exist throw an error and continue the loop
            if not os.path.isdir(outpath + slash + name):
                print(f'\n{Fore.RED}ERROR!{Fore.GREEN} Path does not exist!')
                continue

            print(f'\nAttempting to Purge ...')

            # calling the purge file function
            purge_file(outpath + slash + name)

            print(f'\nPurge {Fore.RED}Sucessful{Fore.GREEN}.')

        elif user_input == 'change':
            # calling the change_outpath function
            new_path = change_outpath(key)
            
            if not new_path:
                # if change_outpath throw an error
                print(f'\n{Fore.RED}ERROR!{Fore.GREEN} Path does not exist!')
            else:
                # change current outpath to new outpath
                outpath = new_path

        elif user_input == 'clear':
            # call clear function
            clear(True)

        elif user_input == 'exit':
            # call sys.exit()
            sys.exit()
