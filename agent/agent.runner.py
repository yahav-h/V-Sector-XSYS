import socket
import logging
import base64
from time import time
from pprint import pprint
from Crypto.Cipher import AES
from agent.modules.session import Session
from commons.agent_db import AgentDataBase

logging.basicConfig(filename='logs/agent.app-runtime.log',
                    filemode='w', format=logging.BASIC_FORMAT,
                    level=logging.DEBUG)
log = logging.getLogger('AgentApp')

global _sock
global _active_connections
global _agent_id
global _agent_db
_sock: socket.socket
_active_connections: dict
_agent_id: None
_agent_db: AgentDataBase

SERVER = '127.0.0.1'
PORT = 5443
MAX_BUFFER = 2048
BLOCK_SIZE = 16
ESCAPE_MARK = 'EOFEOFEOFEOFEOFX'
secret = b'YAHHU88il27a&4Na'
cipher = AES.new(secret, AES.MODE_ECB)

stamp = lambda: time().__str__()[:10]
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(s))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).decode()


def create_socket():
    global _sock
    try:
        _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        log.info(f'[+] Socket Server created adn allocated at {id(_sock)}')
    except (socket.error, Exception) as e:
        log.error(f'[Err] error occur at `create_socket`\n{e}')


def connect():
    global _sock
    try:
        _sock.connect((SERVER, PORT))
        log.info(f'[@] Socket connected to {SERVER, PORT}')
    except (socket.error, Exception) as e:
        log.error(f'[Err] error occur at `connect`\n{e}')


def make_handshake():
    global _sock
    global _agent_id
    try:
        _agent_id = recv_decrypt(_sock)
    except (socket.error, Exception) as e:
        log.error(f'[Err] error occur at `connect`\n{e}')


def send_encrypt(sock: socket.socket, data, end=ESCAPE_MARK):
    try:
        if len(data) > BLOCK_SIZE or len(data) % BLOCK_SIZE == 0:
            delta = len(data) - len(data) % BLOCK_SIZE
            exclusive = delta + len(data) - len(data) % BLOCK_SIZE
            data = data.zfill(exclusive)
        else:
            data = data.zfill(BLOCK_SIZE)
        encrypted_data = EncodeAES(cipher, data+end)
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


def start_agent():
    global _sock
    global _agent_id
    global _agent_db
    try:
        _agent_db = AgentDataBase()
        create_socket()
        connect()
        make_handshake()
        s = Session(_agent_id)
        _agent_db.add(s)
        while _agent_id is not None:
            try:
                response = str(s.to_json())
                send_encrypt(_sock, response)
                data = recv_decrypt(_sock)
                log.info(f'[!] data received : {data}')
                pprint(f'[>] Received : {data}')
            except socket.error as e:
                log.error(f'[Err] connection not allowed, trying again...\n{e}')
                socket.setdefaulttimeout(5000)
                continue
    except Exception as e:
        log.error(f'[ERR] Something went wrong!\n{e}')
        raise e


if __name__ == '__main__':
    start_agent()
