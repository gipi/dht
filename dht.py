#!/usr/bin/env python
import sys
import json
import bencode
import random
import socket
from utils import hex2byte
import logging
from models import Node


stream = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(filename)s:%(lineno)d - %(message)s')

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
logger.addHandler(stream)
stream.setFormatter(formatter)

def generate_random_id():
    # Generate a 160-bit (20-byte) random node ID.
    return ''.join([chr(random.randint(0, 255)) for _ in range(20)])

class Network(object):
    @classmethod
    def send_to_node(klass, node, data):
        data_bencoded = bencode.bencode(data)

        # Send a datagram to a server and recieve a response.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(10)
        s.sendto(data_bencoded, (node.ip, node.port))

        r = None
        try:
            r = s.recvfrom(4096)
        except socket.timeout:
            logger.debug('timeout for %s' % node)
            return r

        try:
            # de-bencode
            r = bencode.bdecode(r[0])
        except bencode.BTL.BTFailure:
            logger.error('response not bencoded: \'%s\'' % r[0])
            return None

        if r.has_key('r'):
            return r['r']
        else:
            logger.error('error for query \'%s\'' % data)
            return r

class Response(object):
    '''Base class for DHT network response'''
    pass

class PeerResponse(Response):
    def __init__(self, peers):
        '''peers is a list of peers'''
        self.peers = peers

class NodeResponse(Response):
    def __init__(self, nodes):
        self.nodes = nodes

class DHT(object):
    '''This represents the Distributed Hash Table with its own queries'''

    def __init__(self, bootstrap=None):
        pass

    def ping(self, _id):
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

        return Network.send_to_node(Node.get_boostrap_node(), ping_query)

    def get_peers(self, _id, node, info_hash):
        get_peers_query = {
            'y': 'q',
            't': '0f',
            'q': 'get_peers',
            'a': {
                'id': _id,
                'info_hash': hex2byte(info_hash),
            }
        }
        logger.info('asking to \'%s\' for peers related to hash \'%s\'' % (node, info_hash))
        return Network.send_to_node(node, get_peers_query)

    def find_node(self, _id, target):
        raise NotImplementedError('find_node is not implemented')

    def announce_peer(self, _id, target):
        raise NotImplementedError('announce_peer is not implemented')

if __name__ == "__main__":
    my_id = generate_random_id()
    print('id: ' + my_id.encode('hex'))

    dht = DHT()

    info_hash = 'bbb6db69965af769f664b6636e7914f8735141b3' if len(sys.argv) == 1 else sys.argv[1]

    peers_result = dht.get_peers(my_id, Node.get_boostrap_node(), info_hash)
    logger.debug('results from bootstrap node: ' + str(peers_result))
