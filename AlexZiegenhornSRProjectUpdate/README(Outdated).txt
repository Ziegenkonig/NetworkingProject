NOTES

- The screenshot labeled 'Input-Output' has the server print
messages on the left, and the client print messages on the right.

- Programs are separated into different folders to enable easier file access.

- ClientClient is the client program, and is located inside of the ClientSpace folder.

- ServerClient is the server program, and is located inside of the ServerSpace folder.

- The implementation for the Alternating Bit Protocol is located inside of
ClientClient.py and starts at line 40.

BUILD/INSTALL/RUN INSTRUCTIONS

- I tested this locally, using gitbash on Windows 10. I believe I also have
Python27 installed on this machine.

- Command for gitbash, once inside of the correct directory:
	for server: python ServerClient.py
	for client: python ClientClient.py
  Then just follow the prompts from there.

- If the file is large, like the mobydick.txt I have inside of the ServerSpace
folder, gitbash works just fine. 

- If the file is small, like the alice.txt I have inside of the ServerSpace folder,
then gitbash does not work; this is because of a bug in which my server program does
not read anything that is not greater than 1000 bytes, which is why the end of 
mobydick.txt is cut off (when transferred), and why it cannot read alice.txt. HOWEVER,
running the python file directly from windows using the python executable works for
the alice.txt, and does not work for mobydick.txt. So if you want to test it that way,
by all means.