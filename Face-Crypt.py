print('Attempting to load Face-Crypt ...')

from colorama import Fore
from colorama import init
import platform
import subprocess
import os
import PyInstaller.__main__

from functions import create_dataset
from functions import train_model
from functions import encrypt
from functions import get_key

print('Success!')

def art(new_lines: int = 2):
    # prints logo
    print(f'{Fore.GREEN}', end='')

    print('███████╗░█████╗░░█████╗░███████╗░░░░░░░█████╗░██████╗░██╗░░░██╗██████╗░████████╗')
    print('██╔════╝██╔══██╗██╔══██╗██╔════╝░░░░░░██╔══██╗██╔══██╗╚██╗░██╔╝██╔══██╗╚══██╔══╝')
    print('█████╗░░███████║██║░░╚═╝█████╗░░█████╗██║░░╚═╝██████╔╝░╚████╔╝░██████╔╝░░░██║░░░')
    print('██╔══╝░░██╔══██║██║░░██╗██╔══╝░░╚════╝██║░░██╗██╔══██╗░░╚██╔╝░░██╔═══╝░░░░██║░░░')
    print('██║░░░░░██║░░██║╚█████╔╝███████╗░░░░░░╚█████╔╝██║░░██║░░░██║░░░██║░░░░░░░░██║░░░')
    print('╚═╝░░░░░╚═╝░░╚═╝░╚════╝░╚══════╝░░░░░░░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░░░░░░░╚═╝░░░')

    print(''.join(['\n'] * new_lines))

def clear(show_art: bool = False):
    # clears screen and shows art if shows logo if the show_art bool is True
    commands = ['clear']
    system_name = platform.system()

    if system_name == 'Windows':
        commands.insert(0, 'powershell.exe')

    subprocess.call(commands)

    if show_art:
        art()

def get_user_input(sub_dir: str):
    # gets user input and process it for decision making
    var = input(f'{Fore.BLUE}fcry{Fore.RED}{sub_dir}{Fore.GREEN} > ').strip()

    if 'set' in var.lower():
        var_list = var.split()

        if len(var_list) < 3:
            return 'set error error'

        var_list[0] = var_list[0].lower()
        var_list[1] = var_list[1].lower()
        new_var = ''

        for item in var_list:
            new_var += item + ' '

        new_var = new_var.strip()

        return new_var

    else:
        var = var.lower()
    
    return var

def help_options():
    # prints all commands
    print(f'\n{Fore.RED}Commands \n{Fore.GREEN}--------')
    print(f'{Fore.RED}Show options{Fore.GREEN} - Prints all available options.')
    print(f'\n{Fore.RED}Home{Fore.GREEN} - Breaks out of the selected option and returns home.')
    print(f'\n{Fore.RED}Use [option] {Fore.GREEN}- Selects the inputted option.')
    print(f'\n{Fore.RED}Show params {Fore.GREEN}- Prints all parameters and their selected values. (Can only be used when an option is selected)')
    print(f'\n{Fore.RED}Show info {Fore.GREEN}- Prints all parameters and their descriptions (Can only be used when an option is selected)')
    print(f'\n{Fore.RED}Set [parameter] [value]{Fore.GREEN} - Sets the selected paramater to the corresponding value.')
    print(f'\n{Fore.RED}Show profiles {Fore.GREEN} - Prints all availble profiles.')
    print(f'\n{Fore.RED}Run{Fore.GREEN} - Runs the selected option with the inputted parameters. (Can only be used when an option is selected)')
    print(f'\n{Fore.RED}Clear{Fore.GREEN} - Clears the screen.')
    print(f'\n{Fore.RED}Exit {Fore.GREEN}- Quits Face-Crypt.')

    print('\n--------\n')

def show_profiles():
    # shows existing profiles
    dir_files = os.listdir('data/')

    print(f'\n{Fore.RED}Profiles \n{Fore.GREEN}--------')


    if len(dir_files) == 1:
        print(f'\n{Fore.RED}No profiles found!{Fore.GREEN}')
        print('\n--------\n')
        return

    for item in dir_files:
        if item != 'other':
            print(f'\n-{Fore.RED} {item} {Fore.GREEN}')

    print('\n--------\n')

    return

def show_options():
    # shows options
    print(f'\n{Fore.RED}Options \n{Fore.GREEN}-------')

    print(f'\n{Fore.RED}Profiler{Fore.GREEN} - Creates a facial profile of the user and saves it for future use.')
    print(f'\n{Fore.RED}Compiler{Fore.GREEN} - Creates a directory containing an executable and an encrypted directory. When the executable is run, the users identity is confirmed via facial recognition and decrypts the directory.')

    print('\n-------\n')

def profile():
    # returns profile params and descriptions
    params = {
        'name' : '',
        'delete': 'False',
        'pictures': '1500'

    }

    desc = {
        'Name': f'{Fore.RED}(str){Fore.GREEN} Name of profile to be created.',
        'Delete': f'{Fore.RED}(bool){Fore.GREEN} True if a profile of the same name exists and you would like to overwrite it. False otherwise. (If a profile of the same name exists and False is selected then profile will be improved.)',
        'Pictures': f'{Fore.RED}(int){Fore.GREEN} Number of pictures to use in dataset.'
    }

    return (params, desc)

def my_compile():
    # returns compiler params and descriptions
    params = {
        'profile': '',
        'password': '',
        'directory': '',
        'outpath' : 'Default',
        'name': 'Face-Crypt',
        'onefile': 'False',
        'purge': 'False'
    }

    desc = {
        'Profile': f'{Fore.RED}(str){Fore.GREEN} Name of profile to be used in encrypting the directory.',
        'Password': f'{Fore.RED}(str){Fore.GREEN} Password to be used alongside facial profile.',
        'Directory': f'{Fore.RED}(str){Fore.GREEN} Absolute path of directory that is to be encrypted.',
        'Outpath': f'{Fore.RED}(str){Fore.GREEN} Absolute path of folder to output decrypted directory. (Input [Default] if you would like to output the decrypted directory in the same folder as the executable)',
        'Name': f'{Fore.RED}(str){Fore.GREEN} Name of the compiled executable or directory.',
        'Onefile': f'{Fore.RED}(bool){Fore.GREEN} True: Output single executable. False: Output a directory containing the executable alongsige multiple binaries (Recomended option)',
        'Purge': f'{Fore.RED}(bool){Fore.GREEN} True: Purge original directory from system. False: Original directory remains untouched.'
    }

    return (params, desc)

def profiler_seq(params: dict):
    # creates facial profile for user
    for key in params:
        if params[key] == '':
            print('\nError! Profiler was run with invalid input')
            return
        if key == 'pictures':
            try:
                max_pics = int(params[key])
            except:
                print('\nError! Pictures has to be an integer.')
                return
        
    delete_val = 'true' in params['delete'].lower()

    camera_connected = input('Is a webcam connected to your machine? (Y/N): ')

    if camera_connected.lower() == 'y':

        input(f'\nIt is recommended to perform the following actions while the profiler is gathering data.\n\n{Fore.RED}- Move around the room\n- Consistently adjust your facial expression \n- Manipulate the lighting of your current space (if possible) \n\n{Fore.GREEN}Press enter to continue ...')

        create_dataset(params['name'], max_pics, delete_val)

        path = os.path.abspath(f'data/{params["name"]}/user')

        input(f'\nIt is reccomended that you navigate to {Fore.RED}{path}{Fore.GREEN} and lookover the dataset to confirm its validity to ensure the best possible profile can be created.\nPress enter to continue ...')
        print('')

        train_model(params['name'])

        print(f'\nSuccess! The {Fore.RED}{params["name"]}{Fore.GREEN} profile has been created and configured. Profiles can be listed by using the {Fore.RED}Show Profiles{Fore.GREEN} command.')

    else:
        print('\nPlease connect a webcam and try again.')
        return

def compiler_seq(params: dict):
    # encrypts directory and compiles executable
    if params['profile'] not in os.listdir('data') or params['profile'] == 'other':
        print(f'\nError! No profile exists with the name {Fore.RED}{params["profile"]}{Fore.GREEN}.')
        return

    for key in params:
        if params[key] == '':
            print(f'\nError! Compiler was run with invalid input.')
            return

    print(f'\nAttempting to encrypt {Fore.RED}{params["directory"]}{Fore.GREEN} ...')

    salt = 'aNdR3C3'
    pepper = '1'* 8

    # hashing key
    key = get_key(salt, params['password'], pepper)

    if params['outpath'].lower() == 'default':
        params['outpath'] = '.'
    elif params['outpath'][-1] == '/' or params['outpath'][-1] == '\\':

        params['outpath'] = params['outpath'][:len(params['outpath']) - 1]

    try:
        encrypt(params['directory'], key, params['profile'], params['outpath'])
    except:
        print(f'\n{Fore.RED}ERROR!{Fore.GREEN} Something went wrong!')

    print(f'\n{Fore.RED}{params["directory"]}{Fore.GREEN} has been sucessfully encrypted.')

    print(f'\nCompiling to {Fore.RED}executable{Fore.GREEN} ...\n')

    # use pyinstaller to compile

    if platform.system() == 'Windows':
        sys_name = 'Windows'
        c = ';'
    else:
        sys_name = 'other'
        c = ':'

    model_path = f'data/{params["profile"]}/{params["profile"]}.h5'

    if params['onefile'].lower() == 'true':
        comp_type = '--onefile'
    else:
        comp_type = '--onedir'

    PyInstaller.__main__.run([
        'compile/to_compile.py',
        comp_type,
        '-i', 'NONE',
        '-n', f'{params["name"]}',
        '--add-data', f'encrypted.json{c}.',
        '--add-data', f'info.json{c}.',
        '--add-data', f'{model_path}{c}.',
        '--add-data', f'haarcascade_frontalface_default.xml{c}.'
    ])

    delete_command = ['rm', f'{params["name"]}.spec']    
    move_command = ['mv', f'dist/{params["name"]}', '.']

    if 'file' in comp_type:
        move_command[1] += '.exe'

    if sys_name == 'Windows':
        delete_command.insert(0, 'powershell.exe')
        move_command.insert(0, 'powershell.exe')

    subprocess.call(move_command)
    subprocess.call(delete_command)

    for i in range(len(delete_command)):
        if '.spec' in delete_command[i]:
            file_index = i

    delete_command[file_index] = 'encrypted.json'
    subprocess.call(delete_command)

    delete_command[file_index] = 'info.json'
    subprocess.call(delete_command)

    delete_command.insert(file_index, '-r')

    if params['purge'].lower() == 'true':
        delete_command[file_index + 1] = params['directory']
        subprocess.call(delete_command)

    delete_command[file_index + 1] = 'build'

    subprocess.call(delete_command)

    delete_command[file_index + 1] = 'dist'

    subprocess.call(delete_command)

    print(f'\n{Fore.RED}{params["name"]}{Fore.GREEN} has been sucessfully compiled')

if __name__ == '__main__':
    valid_options = {
        'profiler' : profile,
        'compiler': my_compile 
    }

    functions = {
        'profiler': profiler_seq,
        'compiler': compiler_seq
    }

    params = {}
    desc = {}

    clear()
    init()
    art()
    sub_dir = ''
    selected_option = ''

    while True:
        var = get_user_input(sub_dir)

        if var == 'h' or var == 'help':
            help_options()

        elif var == 'home':
            params = {}
            desc = {}
            sub_dir = ''
            selected_option = ''

        elif var == 'exit' or var == 'quit':
            quit()
        
        elif var == 'clear' or var == 'cls':
            clear(True)

        elif var == 'show profiles':
            show_profiles()

        elif var == 'show options':
            show_options()

        elif 'use' in var:
            option = var.split()[1].lower()

            if option in valid_options:
                
                selected_option = option
                sub_dir = (f' ({option})')
                params, desc = valid_options[option]()

        elif var == 'show params':
            print(f'{Fore.RED}\nParameters\n{Fore.GREEN}----------')

            if selected_option == '':
                print(f'\n{Fore.RED}Error! no option has been selected.{Fore.GREEN}')
            else:
                for item in params:
                    print(f'\n{Fore.RED}{item.title()}{Fore.GREEN}: {params[item]}')

            print('\n----------\n')

        elif var == 'show info':
            print(f'{Fore.RED}\nParameter Info\n{Fore.GREEN}---------------')

            if selected_option == '':
                print(f'\n{Fore.RED}Error! no option has been selected.{Fore.GREEN}')
            else:
                for item in desc:
                    print(f'\n{Fore.RED}{item}{Fore.GREEN} - {desc[item]}')

            print('\n---------------\n')

        elif 'set' in var:
            var_list = var.split()
            option = var_list[1]
            val = ''
            
            for item in var_list[2:]:
                val += item + ' '

            val = val.strip()

            print(f'{Fore.RED}\nParameter\n{Fore.GREEN}---------')

            if selected_option == '':
                print(f'\n{Fore.RED}Error! no option has been selected.{Fore.GREEN}')
            elif option not in params:
                print(f'\n{Fore.RED}Error! Parameter does not exists.{Fore.GREEN}')
            else:
                params[option] = val

                print(f'\n{Fore.RED}{option.title()}{Fore.GREEN}: {val}')

            print('\n---------------\n')

        elif var == 'run':
            print(f'{Fore.RED}\nExecuting ...\n{Fore.GREEN}-------------')

            if selected_option == '':
                print(f'\n{Fore.RED}Error! no option has been selected.{Fore.GREEN}')
            else:
                clear(True)
                functions[selected_option](params)

            print(f'\n-------------\n')


