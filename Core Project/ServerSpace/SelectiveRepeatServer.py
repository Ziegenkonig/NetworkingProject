# UDPPingerServer.py
# We will need the following module to generate randomized lost packets
import random
import os
import os.path
import math
from socket import *

#Globals
clientAddress = '';
numberData = 0;
windowSize = 0;
totalPackets = 0;
totalFrames = 0;
currentFrame = 0;
currentPacket = 0;
packets = [];
frame = {};
SEQ = 0;

def parseLazy(recv):
	parsed = recv.split('|'.encode())
	ACK = parsed[1]
	return int(ACK)
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
			global numberData
			print ('Sending READY flag to client. . .')
			file = open(recvStr, 'r')
			
			#Sends the OK to begin transfer
			serverSocket.sendto(str.encode('READY')+bytes([ACK]),clientAddress)
			
			#Doing some quick calcs to find out how 
			fSize = os.stat(recvStr).st_size #get the file size
			print('File Size: ', fSize)
			file = open(recvStr, 'rb')
			numberData = math.ceil(fSize/1024)
			print('numberData=',numberData)
			if mACK == ACK:
				mACK = (mACK+1)%2
			return file

#Wait for windowSize from client
def waitForWindowSize(file, serverSocket):
	serverSocket.settimeout(10) #Setting timeout
	try:
		while True:
			global totalPackets
			global totalFrames
			global SEQ
			global windowSize
			#Waiting for windowSize request
			data, clientAddress = serverSocket.recvfrom(1024)
			recvStr, ACK = parse(data)
			print ('WindowSize received from client: ', recvStr, '  ACK: ', ACK)
			#Calculating totalPackets and totalFrames based on values for numberData and windowSize
			print('numberData=',numberData)
			windowSize = int(recvStr)
			totalPackets = numberData
			totalFrames = math.ceil(numberData/windowSize)

			#Chopping up dat file into the necessary pieces
			for x in range(numberData):

				packets.append(file.read(1000))
				SEQ += 1
				file.seek(1000,1)

			#After server receives the windowSize and prepares packets, its time to send the client the buffer information
			print('Client ready for buffering data:  totalPackets=', totalPackets, '  totalFrames=', totalFrames, '  ACK=', ACK)	
			tempStr = str(totalPackets) + '|' + str(totalFrames) + '|' + 'BUFFERDETAILS'
			serverSocket.sendto(str.encode(tempStr)+bytes([ACK]),clientAddress)
			return

	except timeout:
		print("Timed Out! Resending ready acknowledgement. . .")
		serverSocket.sendto(str.encode('READY')+bytes([ACK]),clientAddress)

#Wait for ACK of buffer details from client
def waitForAckOfBuffer(serverSocket):
	global clientAddress

	serverSocket.settimeout(10) #Setting timeout
	try:
		while True:
			#Waiting for windowSize request
			data, clientAddress = serverSocket.recvfrom(1024)
			recvStr, ACK = parse(data)
			print ('ACK received from client: ', recvStr, '  ACK: ', ACK)

			if recvStr == 'DETAILSRECEIVED':
				return

	except timeout:
		print("Timed Out!")
		tempStr = str(totalPackets) + '|' + str(totalFrames) + '|' + 'BUFFERDETAILS'
		serverSocket.sendto((tempStr).encode('utf-8'), serverAddress)

#Sends the five packets that make up a single frame
def sendFrame(serverSocket):

	for x in range(windowSize):
		print ('Sending segment ', x+1, '/', windowSize, ' of frame ', currentFrame, ' ACK: ', currentPacket+x, '\n Data: ', packets[currentPacket+x])
		serverSocket.sendto((packets[currentPacket+x]) + bytes([currentPacket+x]),clientAddress)
	
	print ('Finished sending frame')

#Receives all 5 ACKs that are associated with the current frame
def receiveAck(serverSocket):

	global currentPacket
	global currentFrame

	for x in range(windowSize):
		frame[currentPacket+x] = False

	#Receiving ACKs
	for x in range(windowSize):
		serverSocket.settimeout(3) #Setting timeout
		try:
			while True:
				#Waiting for windowSize request
				data, clientAddress = serverSocket.recvfrom(1024)
				ACK = parseLazy(data)
				print ('ACK received from client:  ACK: ', ACK)

				if ACK == currentPacket+x:
					frame[ACK] = True
					break

		except timeout:
			print("Timed Out!")

	#Resending any packets that did not take
	for x in range(windowSize):
		if frame[currentPacket+x] == False:
			print('Resending Packet that was lost. . .')
			serverSocket.sendto(packets[currentPacket+x]+bytes([currentPacket+x]),clientAddress)

	currentPacket += 5;
	currentFrame += 1;

def main():

	# Create a UDP socket
	# Notice the use of SOCK_DGRAM for UDP packets
	serverSocket = socket(AF_INET, SOCK_DGRAM)

	# Assign IP address and port number to socket
	serverSocket.bind(('', 13000))

	mACK = 0

	print('Waiting for filename request. . .')

	file = waitForFilename(serverSocket, mACK)

	waitForWindowSize(file, serverSocket)
	waitForAckOfBuffer(serverSocket)

	i=0
	while currentFrame <= totalFrames:
		sendFrame(serverSocket)
		receiveAck(serverSocket)
		i += 1
	print(i)



	x = input('Press any key to exit. . .')

	serverSocket.close();

if __name__ == '__main__':
	main()