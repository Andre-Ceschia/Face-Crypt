# Face-Crypt

Face-Crypt is an open-source file encryption software that utilizes the Keras API in order to allow users to create their own distinct facial profiles. This profile is then used alongside a user inputted password for encryption. Face-Crypt is able to encrypt whole directories.

## How It Works?

Face-Crypt uses the SHA256 hashing algorithim in accordance with the AES256 encryption algorithim to ensure user privacy.

## Usage

1. The user should first create a facial profile. This can be done by using the *profiler* option within the Face-Crypt command line interface.

    * During this step Face-Crypt utilizes opencv to gather pictures of the user while simultaneously the preprocessing the gathered data.  
    * Next, Face-Crypt trains a neural network using the Keras API with the pictures aquired from the step above as well as a dataset obtained from the internet containing pictures of celebrities.
    * Finally, Face-Crypt outputs a *h5* file where the model architecture is stored alongside the connection weights.

2. The user should then use the *compiler* option to output an executable that houses the encrypted directory as well as a python script that is able to decrypt the encrypted directory. The user will be asked to specify the facial profile they wish to use, the path of the decrypted directory, a password of their choice, the path where they wish Face-Crypt outputs the decrypted directory, and other options regarding the compilation of the executable.

    * During this step Face-Crypt utilizes the inputted password as well as the profile created by the step above to encrypt the chosen directory.
    * Next, Face-Crypt then compiles to an executable that houses the encrypted directory, facial profile, and opencv classifier

3. When the user runs the executable they will be prompted for a password and then have thier identity analyzed by the neural network created earlier. If they have entered the correct password in addition to passing the identity verification then the user will be prompted with the Face-Crypt client side CLI where all options are shown. 

    * Within the client side CLI users will be able to decrypt their encrypted directory, work on the decrypted directory and then re-encrypt the updated directory, change the outpath of the decrypted directory and more.

<br>

### Note: Use the *help* command inside of the Face-Crypt CLI to list all commands and their funcitons 

<br>

## Installation
 ```sh
 git clone https://github.com/Andre-Ceschia/Face-Crypt

 cd Face-Crypt

 python3 -m pip install -r requirments.txt

 python3 Face-Crypt.py
 ```
