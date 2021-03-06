import socket, select
import sys
from thread import start_new_thread


class config:
    def __init__(self, host=None, port=None, s=socket.socket(socket.AF_INET, socket.SOCK_STREAM), CONNECTION_LIST=None):
        self.host = host
        self.port = port
        self.s = s
        self.CONNECTION_LIST=CONNECTION_LIST

    def create_socket(self):  # Create a socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error:
            print 'Failed to create socket'
            sys.exit()
        print 'Socket Created'
        return s

    def connect_host(self, host, port, s):  # Connect to remote server
        self.host = host
        self.port = port
        self.s = s
        try:
            remote_ip = socket.gethostbyname(host)
        except socket.gaierror:
            # could not resolve
            print 'Hostname could not be resolved. Exiting'
            sys.exit()
        # Connect to remote server
        s.connect((remote_ip, port))
        print 'Socket Connected to ' + host + ' on ip ' + remote_ip


class client(config):

    def send_message(self, s, message):  # Send some data
        self.s = s
        self.message = message
        try:
            # Set the whole string
            s.send(message)
        except socket.error:
            # Send failed
            print 'Send failed'
            sys.exit()
        print 'Message sent successfully'

    def receive_message(self, s):  # Receive a reply
        self.s = s
        # Now receive data
        reply = s.recv(4096)

        print reply


class server(config):

    def bind_socket(self, host, port):
        self.host = host
        self.port = port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((host, port))
        except socket.error, msg:
            print 'Bind failed. Error Code : ' + \
                str(msg[0]) + ' Message ' + msg[1]
            sys.exit()
        print 'Socket bind complete'

    def sckt_listen(self,s):
        s.listen(10)
        print 'Socket now listening'

    #Function for handling connections. This will be used to create threads
    def clientthread(self,conn):
        #Sending message to connected client
        conn.send('Welcome to the server. Type something and hit enter\n') #send only takes string
        
        #infinite loop so that function do not terminate and thread do not end.
        #while True:
            
        #Receiving from client
        data = conn.recv(1024)
        reply = 'OK...' + data    
        conn.sendall(reply)
    
        #came out of loop
        return data


    def sckt_accept(self,s):
        #now keep talking with the client
        while 1:
            #wait to accept a connection - blocking call
            conn, addr = s.accept()
            print 'Connected with ' + addr[0] + ':' + str(addr[1])
            
            #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
            start_new_thread(self.clientthread ,(conn,))
        
        s.close()
        
users = {}
CONNECTION_LIST = []
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
class chat_class(config):
    def broadcast_data(self, sock,message):
        #Do not send the message to master socket and the client who has send us the message
        for socket in CONNECTION_LIST:
            if socket != server_socket and socket != sock :
                try :
                    socket.send(message)
                except :
                    # broken socket connection may be, chat client pressed ctrl+c for example
                    socket.close()
                    CONNECTION_LIST.remove(socket)

    def broadcast_server(self):

        if __name__ == "__main__":
            
            # List to keep track of socket descriptors
            global CONNECTION_LIST
            RECV_BUFFER = 4096 # Advisable to keep it as an exponent of 2
            PORT = 5000
            
            # this has no effect, why ?
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(("0.0.0.0", PORT))
            server_socket.listen(10)
            live_server=server()
        
            # Add server socket to the list of readable connections
            CONNECTION_LIST.append(server_socket)
            print CONNECTION_LIST
            print "Chat server started on port " + str(PORT)
        
            while 1:
                # Get the list sockets which are ready to be read through select
                read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[])
        
                for sock in read_sockets:
                    #New connection
                    if sock == server_socket:
                        # Handle the case in which there is a new connection recieved through server_socket
                        sockfd, addr = server_socket.accept()
                        CONNECTION_LIST.append(sockfd)
                        name=live_server.clientthread(sockfd)
                        print CONNECTION_LIST
                        print type(addr)
                        client = list(addr)
                        print client
                        user= str(client[0])+"."+str(client[1])
                        print "user is: "+user
                        print name
                        users[user]=name
                        print name+" is connected as user " + user
                        print users
                        
                        self.broadcast_data(sockfd, "%s, is now online..." % name)
                    
                    #Some incoming message from a client
                    else:
                        # Data recieved from client, process it
                        try:
                            #In Windows, sometimes when a TCP program closes abruptly,
                            # a "Connection reset by peer" exception will be thrown
                            data = sock.recv(RECV_BUFFER)
                            ID=sock.getpeername()
                            new_ID=list(ID)
                            Disp_ID=str(new_ID[0])+"."+str(new_ID[1])
                            if data:
                                self.broadcast_data(sock, "\n\n" +users[Disp_ID] + ':-> ' + data)                
                        
                        except:
                            self.broadcast_data(sock, "Client (%s, %s) is offline" % users[Disp_ID])
                            print "Client (%s, %s) is offline" % users[Disp_ID]
                            sock.close()
                            CONNECTION_LIST.remove(sock)
                            continue
            
            server_socket.close()





server_class = chat_class()

server_class.broadcast_server()