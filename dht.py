#!/usr/bin/env python
import json
import bencode
import random
import socket
from utils import hex2byte
import logging

stream = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(filename)s:%(lineno)d - %(message)s')

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
logger.addHandler(stream)
stream.setFormatter(formatter)

def generate_random_id():
    # Generate a 160-bit (20-byte) random node ID.
    return ''.join([chr(random.randint(0, 255)) for _ in range(20)])

def send_to_bootstrap_node(data):
    data_bencoded = bencode.bencode(data)

    # Send a datagram to a server and recieve a response.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(data_bencoded,
             (socket.gethostbyname('router.bittorrent.com'), 6881))

    r = s.recvfrom(1024)

    return bencode.bdecode(r[0])

def bootstrap(_id):

# Create ping query and bencode it.
# "'y': 'q'" is for "query".
# "'t': '0f'" is a transaction ID which will be echoed in the response.
# "'q': 'ping'" is a query type.
# "'a': {'id': my_id}" is arguments. In this case there is only one argument -
# our node ID.
    ping_query = {'y': 'q',
                  't': '0f',
                  'q': 'ping',
                  'a': {'id': _id}}

    get_peers_query = {
        'y': 'q',
        't': '0f',
        'q': 'get_peers',
        'a': {
            'id': _id,
            'info_hash': hex2byte(info_hash),
        }
    }

    send_to_bootstrap_node(ping_query)

    response = send_to_bootstrap_node(get_peers_query)



if __name__ == "__main__":
    my_id = generate_random_id()
    print('id: ' + my_id.encode('hex'))
    bootstrap(my_id)
