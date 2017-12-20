import time
from socket import *

def parse(recv):
	str_recv = recv[0:-1] #get the file content
	ACK = recv[-1:] #get ACK number
	return str_recv, int.from_bytes(ACK,byteorder='big')

def waitForOK(seq, filename, clientSocket, serverAddress):
	clientSocket.settimeout(3)
	try:
		while True:
			data, address = clientSocket.recvfrom(1024)
			recvStr, ACK = parse(data)
			print('Received from server: ', recvStr, '  ACK: ', ACK, '  Sequence: ', seq)

			if recvStr == b'OK':
				print('Server is ready to start transmitting!')	
				clientSocket.sendto(seq.encode(),serverAddress)
				return
			else:
				clientSocket.sendto((filename + seq).encode('utf-8'), serverAddress)
	except timeout:
		print("Timed Out! Resending last segment. . .")
		clientSocket.sendto(seq.encode(),serverAddress)


#Waits for new segments of the file from the server, and sends an ACK if a segment is correctly received
def waitForData(seq, file, clientSocket, serverAddress):
	clientSocket.settimeout(3)
	closingMessage = 'close'

	try:
		while True:
			#Receiving data from server
			data, address = clientSocket.recvfrom(1024)
			recvStr, ACK = parse(data)
			print('Received from server: ', recvStr, '  ACK: ', ACK, '  Sequence: ', seq)

			#Here is the Alternating Bits implementation; if ACK is 0, seq is 1, and vice versa
			if int(seq) == ACK:
				if ACK == 0:
					seq = '1'
				else:
					seq = '0'
				clientSocket.sendto(seq.encode(), serverAddress)

			if recvStr == b'close':
				print('Closing connection upon server request. . .')	
				clientSocket.sendto((closingMessage + seq).encode(), serverAddress)
				clientSocket.close()
				return

			#Write the received data to the necessary file
			file.write(recvStr.decode('utf-8'))
	except timeout:
		print("timed out!")
		clientSocket.sendto(seq.encode(), serverAddress)



def main():
	#Initiating client socket
	clientSocket = socket(AF_INET, SOCK_DGRAM)
	clientSocket.settimeout(3)

	#Asking user for filename
	filename = input("Input the name of the file: ")

	#Setting sequence number
	seq = '0'

	#IP and port of server
	serverName = "localhost"
	serverPort = 13000
	serverAddress = (serverName, serverPort)

	#Let's also create a new file with the given filename, so we have somewhere to store the received data
	file = open(filename, 'w')

	#Sending the requested filename to the server
	clientSocket.sendto((filename + seq).encode('utf-8'), serverAddress)
	print ('Requesting ', filename, ' from ', serverName)

	waitForOK(seq, filename, clientSocket, serverAddress)
	waitForData(seq, file, clientSocket, serverAddress)

	print('The file is completely transferred!')

	clientSocket.close();


if __name__ == '__main__':
	main()