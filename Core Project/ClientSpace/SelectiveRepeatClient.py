import time
from socket import *

#Globals
windowSize = '5';
frameCount = 0;
totalPackets = 0;
totalFrames = 0;
framesReceived = 0;
packetsReceived = 0;

#Specifically parses the information received from server regarding buffers (totalPackets, totalFrames)
#Stores the updated totalPackets and totalFrames inside of their respective global variables
def parseBufferData(recv):
	global totalPackets
	global totalFrames

	parsed = recv.split('|'.encode())
	#Allow the first 4 slots of the string to represent the totalPackets
	totalPackets = int(parsed[0])
	#Allow next 4 slots of string to represent the totalFrames
	totalFrames =  int(parsed[1])
	#The rest of the data is the main data as well as the ACK number
	recv = parsed[2]
	str_recv = recv[0:-1] #get the file content
	ACK = recv[-1:] #get ACK number
	return str_recv, int.from_bytes(ACK,byteorder='big')

def parse(recv):
	str_recv = recv[0:-1] #get the file content
	ACK = recv[-1:] #get ACK number
	return str_recv, int.from_bytes(ACK,byteorder='big')

#Aside from the function above and the main function, all of the functions here are laid out in order of execution

#Called from main, and then loops (with timeout) until a windowSize request has been sent from the server.
def waitForServerWindowSizeRequest(filename, clientSocket, serverAddress):
	clientSocket.settimeout(3) #Setting timeout
	try:
		while True:
			data, address = clientSocket.recvfrom(1024)
			recvStr, ACK = parse(data)
			print('Received request from server:', recvStr, '  ACK: ', ACK)

			#NOTE -- We will be using the 'READY' as a flag to make sure that the server is ready to receive windowSize
			#Sending windowSize to server
			if recvStr == b'READY':
				print('Server is ready to receive window size! windowSize=', windowSize, '  Sending to server. . .')	
				clientSocket.sendto((windowSize + '0').encode(), serverAddress)
				return
			else:
				clientSocket.sendto((filename + '0').encode('utf-8'), serverAddress)
	except timeout:
		print("Timed Out! Resending filename request. . .")
		clientSocket.sendto((filename + '0').encode('utf-8'), serverAddress)

#Called from main, and then loops (with timeout) until a segment containing the necessary buffer details arrives from server
def waitForServerBufferDetails(clientSocket, serverAddress):
	clientSocket.settimeout(6) #Setting timeout
	try:
		while True:
			data, address = clientSocket.recvfrom(1024)
			recvStr, ACK = parseBufferData(data) #Parsing received buffer data
			print('Received buffer information:', recvStr, '  totalPackets= ', totalPackets, '   totalFrames=', totalFrames, '  ACK: ', ACK)

			#NOTE -- We will be using the 'BUFFERDETAILS' as a flag to make sure that this message contains the nexessary buffer details
			#Send acknowledgement of receipt
			if recvStr == b'BUFFERDETAILS':
				print('Server has sent buffer details! totalPackets=', windowSize, '  totalFrames=', totalFrames, '  Sending acknowledgement. . .')	
				clientSocket.sendto(('DETAILSRECEIVED' + '0').encode(), serverAddress)
				return
			else:
				clientSocket.sendto((windowSize + '0').encode('utf-8'), serverAddress)
	except timeout:
		print("Timed Out! Resending windowSize notification. . .")
		clientSocket.sendto((windowSize + '0').encode('utf-8'), serverAddress)

#Waits for new segments of the file from the server, and sends an ACK if a segment is correctly received
#Also regulates some of the variables needed for Selective Repeat
def waitForData(file, clientSocket, serverAddress):
	global packetsReceived
	global framesReceived

	clientSocket.settimeout(10)
	closingMessage = 'close'

	try:
		while True:
			#Receiving data from server
			data, address = clientSocket.recvfrom(1024)
			recvStr, ACK = parse(data)
			print('Received packet from server: ', recvStr, '  totalFrames=', totalFrames, '  framesReceived=', framesReceived, 'packetsReceived=', packetsReceived,' ACK=', ACK)

			#This is where the bulk of the Selective Repeat is implemented
			#Here we check to make sure that the ACK matches the framesReceived, to ensure validity
			if packetsReceived == ACK:
				print('Sending ACK ', ACK)
				tempStr = '|' + str(ACK)
				clientSocket.sendto(tempStr.encode(), serverAddress)
				packetsReceived += 1
			#Checks whether or not we have advanced a full frame yet
			if packetsReceived%int(windowSize) == 0:
				framesReceived += 1

			#Closes connection from clients side if closing request is received from server
			if recvStr == b'close':
				print('Closing connection upon server request. . .')	
				clientSocket.sendto((closingMessage + ACK).encode(), serverAddress)
				clientSocket.close()
				return

			#Write the received data to the necessary file
			file.write(recvStr.decode('utf-8'))
	except timeout:
		print("Timed Out! Resending last acknowledgement. . .")
		print('Sending ACK ', packetsReceived)
		tempStr = '|' + str(packetsReceived)
		clientSocket.sendto(tempStr.encode(), serverAddress)



def main():
	#Initiating client socket
	clientSocket = socket(AF_INET, SOCK_DGRAM)
	clientSocket.settimeout(3)

	#Asking user for filename
	filename = input("Input the name of the file: ")

	#IP and port of server
	serverName = "localhost"
	serverPort = 13000
	serverAddress = (serverName, serverPort)

	#Let's also create a new file with the given filename, so we have somewhere to store the received data
	file = open(filename, 'w')

	#Sending the requested filename to the server
	clientSocket.sendto((filename + '0').encode('utf-8'), serverAddress)
	print ('Requesting ', filename, ' from ', serverName)

	waitForServerWindowSizeRequest(filename, clientSocket, serverAddress)
	waitForServerBufferDetails(clientSocket, serverAddress)
	waitForData(file, clientSocket, serverAddress)


	print('The file is completely transferred!')

	clientSocket.close();


if __name__ == '__main__':
	main()