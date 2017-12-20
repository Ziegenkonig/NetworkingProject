# UDPPingerServer.py
# We will need the following module to generate randomized lost packets
import random
import os
import os.path
import math
from socket import *

def parse(recv):
	filename = recv[0:-1].decode() #get the file name
	ACK = recv[-1:] #get ACK number
	return filename, int(ACK)

#Simply waits upon program start for the client to send the filename request
def waitForFilename(serverSocket, mACK):
	
	while True:
		#Waiting for filename request
		data, clientAddress = serverSocket.recvfrom(1024)
		recvStr, ACK = parse(data)
		print ('Filename request received from client: ', recvStr, '  ACK: ', ACK)

		#Checking if file exists
		if (os.path.isfile(recvStr)):
			print ('Sending OK to client. . .')
			file = open(recvStr, 'r')
			
			#Sends the OK to begin transfer
			serverSocket.sendto(str.encode('OK')+bytes([ACK]),clientAddress)
			
			#Doing some quick calcs to find out how 
			fSize = os.stat(recvStr).st_size #get the file size
			print('File Size: ', fSize)
			file = open(recvStr, 'rb')
			numberData = math.ceil(fSize/1024)
			if mACK == ACK:
				mACK = (mACK+1)%2
			return file, numberData

	
def sendTheFile(serverSocket, mACK, file, numberData):
		
	closingMessage = 'close'
	i = 0

	while True:
		data, clientAddress = serverSocket.recvfrom(1024)
		recvStr, ACK = parse(data)
		print ('ACK received: ', ACK)

		if recvStr != '':
			if recvStr == 'close':
				print('file is sent completely!')
				file.close()
				return
		else:
			if mACK == ACK:
				i = i+1
			else:
				file.seek(1000,1)
			resp_data = file.read(1000)

			if i == numberData:
				print (i, '    ', numberData)
				serverSocket.sendto(str.encode(closingMessage)+bytes([ACK]),clientAddress)
			else:
				print ('Sending next data segment: ', resp_data, ' ACK: ', ACK)
				serverSocket.sendto(resp_data+bytes([ACK]),clientAddress)


def main():

	# Create a UDP socket
	# Notice the use of SOCK_DGRAM for UDP packets
	serverSocket = socket(AF_INET, SOCK_DGRAM)

	# Assign IP address and port number to socket
	serverSocket.bind(('', 13000))

	mACK = 0

	print('Waiting for filename request. . .')

	file, numberData = waitForFilename(serverSocket, mACK)

	sendTheFile(serverSocket, mACK, file, numberData)

	x = input('Press any key to exit. . .')

	serverSocket.close();

if __name__ == '__main__':
	main()