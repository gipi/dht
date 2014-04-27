#!/usr/bin/env python
import sys
import json
import bencode
import random
import socket
from utils import bt_nodes_info_from_raw_data, bt_contact_peer, hex2byte
import logging
from multiprocessing import Process, Pool

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

# www.rueckstiess.net/research/snippets/show/ca1d7d90
def unwrap_self_f(arg, **kwarg):
    return DHT.get_peers(*arg, **kwarg)

class DHT(object):
    '''This represents the Distributed Hash Table with its own queries
    
    See <www.bittorrent.org/beps/bep_0003.html>
    '''

    def __init__(self, network):
        self.network = network

    def ping(self, _id):
        ping_query = {'y': 'q',
                      't': '0f',
                      'q': 'ping',
                      'a': {'id': _id}}

        return self.network.send_to_node(Node.get_boostrap_node(), ping_query)

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
        response = self.network.send_to_node(node, get_peers_query)

        if not response:
            return None

        if response.has_key('nodes'):
            return bt_nodes_info_from_raw_data(response['nodes'])
        elif response.has_key('values'):
            return [bt_contact_peer(x) for x in response['values']]
        else:
            raise ValueError('Unexpected response: ' + response)

    def find_node(self, _id, target):
        raise NotImplementedError('find_node is not implemented')

    def announce_peer(self, _id, target):
        raise NotImplementedError('announce_peer is not implemented')

    def get_recursively_peers(self, _id, nodes, info_hash):
        logger.debug('asking for peers to nodes ' + str(nodes))
        pool = Pool()
        args = [(self, _id, x, info_hash) for x in nodes if x is not None]

        # this returns a list of list
        results = pool.map(unwrap_self_f, args)
        results = [x for x in results if x is not None]
        logger.info([str(x) for x in results])
        for result in results:
            self.get_recursively_peers(_id, result, info_hash)

    def find_peers_for_infohash(self, _id, info_hash):
        result = self.get_recursively_peers(_id, [Node.get_boostrap_node()], info_hash)


if __name__ == "__main__":
    my_id = generate_random_id()
    print('id: ' + my_id.encode('hex'))

    dht = DHT(Network)

    info_hash = 'bbb6db69965af769f664b6636e7914f8735141b3' if len(sys.argv) == 1 else sys.argv[1]


    dht.find_peers_for_infohash(my_id, info_hash)
