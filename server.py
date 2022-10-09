import socket, random, sys
from cryptography.fernet import Fernet
from asyncio.windows_events import NULL

#Set the default Host being the IPV4 address of the machine running the code
HOST = socket.gethostbyname(socket.gethostname())
#Default port of 5000
PORT = 5000

#Variables for the key to be set in the future
key = NULL
fernetSet = NULL
keyNotifier = True

#state variables for the game to start and finish
startGame = False
gameEnd = False
#Default state of the player's guess and the counter for the amount of guesses
playerGuess = "_____"
guessCounter = 1

def encryptFern(message):
    #converts string to byte then encrypts
    message = bytes(message, 'utf-8')
    #returns byte form of encrpyed message
    return fernetSet.encrypt(message)

def decrpytFern(message):
    return fernetSet.decrypt(message)

def compareWords(guess):
   """ Compares the input word "guess" with the randomly chosen word
   :param guess: the user input guess word
   :type guess: string
   
   """
   global guessCounter
   global playerGuess
   guessCounter += 1
   # Iterate over index
   for index, letters in enumerate(guess):
      for jindex, characters in enumerate(chosenWord):
         # Right position right letter
         if (letters.upper() == characters and index == jindex):
            tempList = list(playerGuess)
            tempList[index] = guess[index].upper()
            playerGuess = ''.join(tempList)
         #Correct character wrong position
         elif(letters.upper() == characters):
            tempList = list(playerGuess)
            tempList[index] = guess[index].lower()
            playerGuess = ''.join(tempList)
   # game end state change
   if (playerGuess.casefold() == chosenWord.strip().casefold()):
      c.send(encryptFern(f"Word: {chosenWord} Score: {guessCounter} \n--GAME OVER--").encode())
      playerGuess = ""
   else:
      c.send(encryptFern(playerGuess))

def wordCheck(guess):
   """ Checks to see if the input word is appropriate for the prompt
   :param guess: the user input guess word
   :type guess: string
   
   """
   global playerGuess
   global gameEnd
   # if the guess and the chosen word are the same length
   if (len(guess) == len(chosenWord) - 1):
      #valid word
      if guess.upper() in finGuessList:
         if (guess.casefold() == chosenWord.strip().casefold()):
            print("end game")
            sendOutput = encryptFern((f"Word: {chosenWord}        Score: {guessCounter} \n      --GAME OVER--"))
            c.send(sendOutput)
            gameEnd = True
            
         else: #Working guess
            compareWords(guess)
      else:
         sendOutput = encryptFern("INVALID GUESS")
         c.send(sendOutput)
   else: #Wrong amount of characters
      sendOutput = encryptFern(f"Enter {len(chosenWord) - 1} characters")
      c.send(sendOutput)

def selectWord():
   """ 
      Select a word from the target.txt file at random
   :return: "chosenWord" randomly chosen word to be guessed by user
   
   """
   #Choose word from list
   my_file = open("target.txt", "r")
   content_list = my_file.readlines()
   randomListIndex = random.randrange(0, len(content_list))
   chosenWord = content_list[randomListIndex]
   return chosenWord


#Input parameter error handling
   #invalid amount of input parameteres
if len(sys.argv) !=2:
      print("Invalid amount of arguments: Please only use 1 argument for port number")
      sys.exit()
   #Port parameter too low (has to be high to avoid commonly used ports)
elif (int(sys.argv[1]) <= 1023):
      print("Port needs to be 1024 or greater")
      sys.exit()
   #Final check that the port parameter is a number
elif (sys.argv[1].isnumeric()):
   #change global port
   PORT = int(sys.argv[1])

   #connect socket to server "s"
   s = socket.socket()
   s.bind((HOST, PORT))
   print("Server is up!")
   s.listen(5)
   c, addr = s.accept()
   print ("Socket Up and running with a connection from",addr)

   #Read lines from text file and change the formatting to compare the words effectively
   guessFile = open("guess.txt", "r")
   guessList = guessFile.readlines()
   finGuessList = list(map(str.strip, guessList))

while True:
   if keyNotifier: # Key has not been sent
      key = c.recv(1024)
      print("Key has been received: ", key)
      fernetSet = Fernet(key)
      keyNotifier = False
      print("...Key complete...")
   else:
      # gamestate finish
      if gameEnd:
         break
      #receive message data from Client and decrypt it while outputting to the server
      rcvdData = c.recv(1024)
      decrpyedInput = decrpytFern(rcvdData).decode('utf-8')
      print(decrpyedInput)
      
      # Shut down server quickly
      if(decrpyedInput == "Bye" or decrpyedInput == "bye"):
         break
      # start game or prompt start game
      if startGame:
         wordCheck(decrpyedInput)
      elif(decrpyedInput.casefold() == "start game".casefold()):
         baseCase = "_____"
         c.send(encryptFern(baseCase))
         startGame = True
         chosenWord = selectWord()
         print(chosenWord)
      else:
         c.send(encryptFern("Messaged received. Type 'start game' to start"))

   
c.close()