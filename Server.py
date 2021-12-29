import logging
import selectors
import select
import socket
import time
import threading
import struct
import Client

BROADCAST = '172.99.255.255'

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')


class SelectorServer:
    def __init__(self, port):

        # create udp socket
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.udp_socket.bind(('', port))
        logging.info('Server up, listening on IP address: {0}'.format(self.udp_socket.getsockname()))

        # Create the main socket that accepts incoming connections and start
        # listening. The socket is nonblocking.
        self.port = port
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.main_socket.bind(('', port))
        self.main_socket.listen(2)
        self.main_socket.setblocking(False)

        # Create the selector object that will dispatch events. Register
        # interest in read events, that include incoming connections.
        # The handler method is passed in data so we can fetch it in
        # serve_forever.
        self.selector = selectors.DefaultSelector()
        self.selector.register(fileobj=self.main_socket,
                               events=selectors.EVENT_READ,
                               data=self.on_accept)

        # waiting clients queue - contains sockets #
        self.queue = []
        self.p1_name = None
        self.riddles = [
                        ('What is the value of fib(2)+fib(3)? ***Assume fib(0) = 0***', 3),
                        ('Sum all digits of the number 74858 until getting one digit', 5),
                        ('What is the value of the following expression: 1<<3', 8),
                        ('What is the value of the following expression: 2<<2', 8),
                        ('What is the value of the following expression: 64>>5', 2),
                        ('What is the value of the following expression: 256>>7', 2),
                        ('What is the value of the following expression: 5 XOR 3', 6),
                        ('What is the value of the following expression: 2 XOR 8', 10),
                        ('What is the value of the following expression: 1 && 3', 1),
                        ('What is the value of the following expression: 5||4', 5),
                        ('What is the value of the following expression: 496351 XOR 496351', 8),
                        ('If one and half fish cost one and half dollar. How much costs five fish?', 5),
                        ('What is the value of the following expression: 496351 XOR 496351', 8),
                        ('What is sum first three digits AFTER DECIMAL DOT of √2?', 9),
                        ('How many occurrences of \'h\' in: \"Sarah Shara Shir Sameach\"', 3),
                        ('How many occurrences of \'s\' in: \"Sasha Samma Shum Ba Shuchi\"', 5),
                        ('What is sum of first two digits AFTER DECIMAL DOT of π?', 5),
                        ('What is the value of sin(90) ***Using Degree***', 1),
                        ('tan(45) equals to:  ***Using Degree***', 1),
                        ('arctan(0) equals to:  ***Using Degree***', 0),
                        ('2^33 bits equals to ____ Gigabytes?', 1),
                        ('2^30 bits equals to ____ Gigabits?', 1),
                        ('|-5| - 5 =____?', 0),
                        ('6÷2(1+2) =____?', 9),
                        ('3+3÷3 =____?', 4),
                        ('6÷2(1+2) =____?', 9),
                        ('Assume not using condom. How much 1+1 equals?', 3),
                        ('Assume f(x) = x^2. f(-3) = _____?', 9),
                        ]
        self.riddle_index = 0


    def on_accept(self, sock, mask):
        # This is a handler for the main_socket which is now listening, so we
        # know it's ready to accept a new connection.
        try:
            if len(self.queue) < 2:
                client_socket, address = self.main_socket.accept()
                logging.info('Accepted connection from {0}'.format(address))
                client_socket.setblocking(False)
                # Register interest in read events on the new socket, dispatching to self.on_read
                self.selector.register(fileobj=client_socket, events=selectors.EVENT_READ, data=self.on_read)
                                       
        except:
            logging.info('Server failed to connect to: {0}'.format(socket))

    def close_connection(self, socket):
        try:
            logging.info('Closing connection with: {0}'.format(socket))
            #self.selector.unregister(socket)
            socket.close()
        except:
            logging.info(
                'Error occurred during closing connection with: {0}'.format(socket))

    def run_offer(self, dest_port):
        if len(self.queue) < 2:
            logging.info('Server send offer message')
            packer = struct.Struct('IBH')
            data = packer.pack(0xabcddcba, 2, self.port)
            self.udp_socket.sendto(data, ('172.99.255.255', dest_port))


    def generate_winning_summary(self, winner, answer):
        return 'Game over!\nThe correct answer was: {0}.\n\nCongratulation to the winner: {1}\n\n'.format(answer,
                                                                                                          winner)

    def generate_draw_summary(self, answer):
        return 'Game over with a draw!\n The correct answer was: {0}.\n'.format(answer)

    def generate_welcome_message(self, p1, p2, riddle):
        return 'Welcome to Quasi Team\nPlayer1: {0}\nPlayer2: {1}\n=============\n{2}'.format(p1, p2, riddle)

    def generate_riddle(self):
        riddle = self.riddles[self.riddle_index]
        self.riddle_index = (self.riddle_index + 1) % (len(self.riddles))
        return riddle

    def run(self, p1_socket, p1_name, p2_socket, p2_name):
            (riddle, riddle_answer) = self.generate_riddle()
            welcome_msg = self.generate_welcome_message(p1_name, p2_name, riddle).encode()
            msg = None
            try:
                p1_socket.send(welcome_msg)
                p2_socket.send(welcome_msg)
                time.sleep(10)
                logging.info('Send welcome message to: {0}, {1}'.format(p1_name, p2_name))
                first_responder_socket = None
                fd1, fd2 = socket1.fileno(), socket2.fileno()
                rlist, wlist, xlist = select.select([fd1, fd2], [], [], 10)
                if len(rlist) != 0:
                    first_responder_fd = rlist[0]
                    first_responder_name = p1_name if first_responder_fd == fd1 else p2_name
                    first_responder_socket = p1_socket if first_responder_fd == fd1 else p2_socket
                    # get data from first responder, convert it to int.
                    answer = first_responder_socket.recv(1024)
                    answer = int(repr(answer)[2:-1])
                    is_correct_answer = answer == riddle_answer
                    logging.info('Recieve answer: {0} from: {1}.'.format(answer, first_responder_name))
                    msg = self.generate_winning_summary(p1_name,
                                                        riddle_answer) if is_correct_answer and first_responder_fd == fd1 else self.generate_winning_summary(
                        p2_name, riddle_answer)
                else:
                    msg = self.generate_draw_summary(riddle_answer)
            except:
                logging.info('Fail to receive data from: {0}, {1}'.format(p1_name, p2_name))
            finally:
                msg = self.generate_draw_summary(riddle_answer) if msg is None else msg
                msg = msg.encode()
                logging.info('Send summary to: {0}, {1}'.format(p1_name, p2_name))
                p1_socket.send(msg)
                p2_socket.send(msg)
                self.close_connection(p1_socket)
                self.close_connection(p2_socket)

    def on_read(self, socket, mask):
        # This is a handler for peer sockets - it's called when there's new data.
        try:
            data = socket.recv(1024)
            data = repr(data)[2:-1]
            fd = socket.fileno()
            address = socket.getpeername()
            logging.info('Got data from {0}: {1}'.format(address, data))
            if data is not None:
                self.queue.append((socket, data))
            if len(self.queue)>=2:
                # 1. pop first two rivals from queue
                p1_socket, p1_name = self.queue.pop()
                p2_socket, p2_name = self.queue.pop()
                # 2. Create thread to handle both rival
                pair_thread = threading.Thread(target=self.run, args=(p1_socket, p1_name, p2_socket, p2_name))
                pair_thread.start()
                self.selector.unregister(p1_socket)
                self.selector.unregister(p2_socket)
        except:
            logging.info('Fail to receive the following data:{0}'.format(data))
            self.close_connection(socket)

    def serve_forever(self):
        last_report_time = time.time()

        while True:
            # Wait until some registered socket becomes ready. This will block
            # for 200 ms.
            events = self.selector.select(timeout=1)
            threading.Thread(target=self.run_offer, args=(13117,)).start()

            # For each new event, dispatch to its handler
            for key, mask in events:
                handler = key.data
                handler(key.fileobj, mask)

            # This part happens roughly every second.
            cur_time = time.time()
            if cur_time - last_report_time > 1:
                logging.info('Running report...')
                logging.info('Number of active peers = {0}'.format(
                    len(self.queue)))
                last_report_time = cur_time


if __name__ == '__main__':
    logging.info('Create Server')
    """
    c1, c2 = Client.Client(13300), Client.Client(13300)
    threading.Thread(target=c1.run, args=()).start()
    threading.Thread(target=c2.run, args=()).start()
    """
    server = SelectorServer(port=2112)
    server.serve_forever()
