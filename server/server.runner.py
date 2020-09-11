import socket
import logging
import base64
from time import time
from uuid import uuid1, uuid5, NAMESPACE_DNS
from pprint import pprint
from Crypto.Cipher import AES
from server.modules.agents import Agent
from commons.server_db import ServerDataBase

logging.basicConfig(filename='logs/server.app-runtime.log',
                    filemode='w', format=logging.BASIC_FORMAT,
                    level=logging.DEBUG)
log = logging.getLogger('ServerApp')

global _sock
global _active_connections
global _server_db
_sock: socket.socket
_active_connections: dict
_server_db: ServerDataBase

HOST = '0.0.0.0'
PORT = 5443
MAX_CONNECTIONS = 3
MAX_BUFFER = 2048
BLOCK_SIZE = 16
ESCAPE_MARK = 'EOFEOFEOFEOFEOFX'
secret = b'YAHHU88il27a&4Na'
cipher = AES.new(secret, AES.MODE_ECB)

stamp = lambda: time().__str__()[:10]
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(s))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).decode()

_server_db = ServerDataBase()


def create_socket():
    global _sock
    global _active_connections
    try:
        _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log.info(f'[+] TCP Socket Created and allocated at {id(_sock)}')
        _active_connections = {}
    except (socket.error, Exception) as e:
        log.error(f'[Err] error occur at `create_socket`\n{e}')
        raise e


def bind_and_listen():
    global _sock
    try:
        _sock.bind((HOST, PORT))
        log.info(f'[+] Socket Server bind connections on {HOST, PORT}')
        _sock.listen(MAX_CONNECTIONS)
        log.info(f'[+] Socket Server listen to {MAX_CONNECTIONS} connections')
    except (socket.error, Exception) as e:
        log.error(f'[Err] error occur at `bind_and_listen`\n{e}')
        raise e


def accept_connection():
    global _sock
    try:
        connection_info = _sock.accept()
        log.info(f'[+] Socket Server received connection from {connection_info[-1]}')
        return connection_info
    except (socket.error, Exception) as e:
        log.error(f'[Err] error occur at `accept_connection`\n{e}')
        raise e


def make_handshake(sock: socket.socket, agent_id: str):
    try:
        send_encrypt(sock, agent_id)
    except (socket.error, Exception) as e:
        log.error(f'[Err] error occur at `make_handshake`\n{e}')
        raise e


def send_encrypt(sock: socket.socket, data, end=ESCAPE_MARK):
    try:
        encrypted_data = None
        if len(data) > BLOCK_SIZE or len(data) % BLOCK_SIZE == 0:
            delta = len(data) - len(data) % BLOCK_SIZE
            exclusive = delta + len(data) - len(data) % BLOCK_SIZE
            data = data.zfill(exclusive)
        else:
            data = data.zfill(BLOCK_SIZE)
        encrypted_data = EncodeAES(cipher, data + end)
        sock.sendall(encrypted_data)
        log.info(f'[>] Socket sent data {encrypted_data}')
    except (socket.error, Exception) as e:
        log.error(f'[Err] error occur at `sent_encrypt`\n{e}')
        raise e


def recv_decrypt(sock: socket.socket, end=ESCAPE_MARK):
    try:
        data = ""
        packet = sock.recv(MAX_BUFFER)
        while packet:
            decrypted_data = DecodeAES(cipher, packet)
            data += decrypted_data
            if data.endswith(end):
                break
            else:
                data = sock.recv(MAX_BUFFER)
        log.info(f'[<] Socket received data {packet}')
        data = data.strip('0')
        return data[:-len(end)]
    except (socket.error, Exception) as e:
        log.error(f'[Err] error occur at `recv_decrypt`\n{e}')
        raise e


def start_server():
    global _active_connections
    global _server_db
    try:
        create_socket()
        bind_and_listen()
        log.info(f'[+] TCP Server is up and running...')
        while len(_active_connections.keys()) != MAX_CONNECTIONS:
            connection, address = accept_connection()
            timestamp = stamp()
            conn_id = uuid5(NAMESPACE_DNS, f'{address[0]}:{address[-1]}:{timestamp}').__str__()
            _active_connections.setdefault(conn_id, connection)
            log.debug(f'[@] Incoming Connection from {address} - {conn_id}')
            make_handshake(connection, conn_id)
            data = recv_decrypt(connection)
            optional_agent = Agent(peer_id=conn_id, json={'id': uuid1().__str__(), 'message': data})
            _server_db.add(optional_agent)

    except Exception as e:
        log.error(f'[ERR] Something went wrong!\n{e}')
        raise e


if __name__ == '__main__':
    start_server()
