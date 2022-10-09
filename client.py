import socket
from cryptography.fernet import Fernet
import sys

#Host is the local IP address by default Port is 2000
HOST = socket.gethostbyname(socket.gethostname())
PORT = 2000
#Create the Key and Fernet Object
KEY_CREATE = Fernet.generate_key()
FERNET = Fernet(KEY_CREATE)


def encryptFern(message):
    #converts string to byte then encrypts
    message = bytes(message, 'utf-8')
    #returns byte form of encrpyed message
    return FERNET.encrypt(message)

def decrpytFern(message):
    return FERNET.decrypt(message)

#Valid parameter check for port and host
if len(sys.argv) !=3:
      print("Invalid amount of arguments: Please only use 2 arguments for host and port number")
      sys.exit()
#port number has to be >= 1024
elif (int(sys.argv[2]) <= 1023):
      print("Port needs to be 1024 or greater")
      sys.exit()
#port is a number
elif (sys.argv[2].isnumeric()):
   PORT = int(sys.argv[2])
   HOST = (sys.argv[1])
else:
    print("Enter valid parameters: startclient.sh HOST PORT")

#Start client socket and connect to server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #Connect to socket
    s.connect((HOST, PORT))
    #SEND KEY TO SERVER AS CLIENT STARTS
    s.send(KEY_CREATE)

    #client message receive/send loop
    while True:
        userInput = input("[Client]: ")
        #Check if used wants to quit
        if(userInput == "Bye" or userInput == "bye"):
            break
        #Encrypt the user input and send it to the server
        encrpyInput = encryptFern(userInput)
        s.send(encrpyInput)

        #Collect received message and decrypt it
        servMsg = decrpytFern(s.recv(1024)).decode('utf-8')
        print ("[Server]:", servMsg)


        if ("GAME OVER" in servMsg):
            break
    s.close()