import logging
import select
import socket
import struct
import sys

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')


class Client:

    def __init__(self, port):
        self.tcp_socket = None
        self.udp_socket = None
        self.server_port = None
        self.port = port
        self.team_name = 'Rak-Yossi!'
        self.server_address = None
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socketock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.udp_socket.bind(('', self.port))

    def connect_to_server(self, offer_buffer_size = 9):
        message, address = self.udp_socket.recvfrom(offer_buffer_size)
        self.server_port = struct.unpack('IBH', message)[2]
        self.server_address = address[0]
        logging.info('Received server details. IP: {0}, Port: {1}.'.format(self.server_address, self.server_port))
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((self.server_address, self.server_port))
        logging.info('Establish TCP connection with IP: {0}, Port: {1}.'.format(self.server_address, self.server_port))

    def run(self):
        try:
            self.tcp_socket.send(self.team_name.encode())
            welcome_msg = repr(self.tcp_socket.recv(1024))[2:-1].replace('\\n', '\n')
            logging.info('Received from server{0}:\n{1}'.format(self.server_address ,welcome_msg))
            fd1, fd2 = self.tcp_socket.fileno(), sys.stdin.fileno()
            try:
                rlist, wlist, xlist = select.select([fd1, fd2], [], [], 10)
                if len(rlist) > 0:
                    hd = rlist[0]
                    if hd == fd2:
                        user_input = input('')
                        logging.info('{0} answered: {1}'.format(self.team_name, user_input))
                        self.tcp_socket.send(user_input.encode())
            except:
                logging.info('Call to select function failed')
            finally:
                summary = repr(self.tcp_socket.recv(1024))[2:-1].replace('\\n', '\n')
                logging.info('Server contest summary:\n{0}\n'.format(summary))
        except:
            logging.info('Failed to send message to {0}'.format(self.server_address))


if __name__ == '__main__':
    PORT = 13117
    client = Client(PORT)
    client.connect_to_server()
    client.run()
