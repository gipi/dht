#!/usr/bin/env python
import sys
import bencode
import random
import socket
from utils import (
    hex2byte,
    byte2int,
    k,
    xor,
)
from models import (
    Node,
    bt_nodes_info_from_raw_data,
    bt_contact_peer,
)
import logging
from multiprocessing import Process, Pool


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

class Response(list):
    '''Base class for DHT network response'''
    def __repr__(self):
        return '[%s]' % ', '.join([unicode(x) for x in self])

class PeerResponse(Response):
    pass
class NodeResponse(Response):
    pass

# inspired from a nodejs implementation
#   https://github.com/feross/bittorrent-dht/blob/master/buckets.js
class BucketList(object):
    '''Contains the routing table of the DHT for a given node.
    
    It's the main point about DHT: allows to find a node in a
    net of size 2^N in N steps.

    The list contains entries ordered with respect to the XOR distance.
    '''
    BUCKET_SIZE = 20
    ID_SPACE_LENGTH = 160
    def __init__(self):
        '''node is the reference node.'''
        self.buckets = [
            {'min':0, 'max': 2**self.ID_SPACE_LENGTH, 'nodes': []}
        ]

    def _insert(self, bucket):
        index = 0
        for b in self.buckets:
            if b['min'] > bucket['min']:
                break
            index += 1

        self.buckets.insert(index, bucket)

    def _remove(self, bucket):
        self.buckets.remove(bucket)

    def _split(self, bucket):
        self._remove(bucket)

        _min = bucket['min']
        _max = bucket['max']
        _half = (_min + _max) / 2

        first_half = {
            'min': _min,
            'max': _half,
            'nodes': []
        }
        second_half = {
            'min': _half,
            'max': _max,
            'nodes': []
        }

        for node in bucket['nodes']:
            if byte2int(node.id) <= _half:
                first_half['nodes'].append(node)
            else:
                second_half['nodes'].append(node)

        self._insert(first_half)
        self._insert(second_half)

    def _join(self, bucket):
        self._remove(bucket)

        for b in self.buckets:
            if b['min'] > bucket['min']:
                b['min'] = bucket['min']
                break

    def insert_node(self, node):
        bucket = self.get(node)

        try:
            bucket['nodes'].remove(node)
            bucket['nodes'].append(node)
        except ValueError:
            self.__insert_node_not_present(bucket, node)

    def __insert_node_not_present(self, bucket, node):
        if len(bucket['nodes']) == 8:
            self._split(bucket)
            self.insert_node(node)
        else:
            bucket['nodes'].append(node)

    def remove_node(self, node):
        bucket = self.get(node)
        nodes = bucket['nodes']

        nodes.remove(node)

        if len(nodes) == 0:
            self._join(bucket)

    def get(self, node):
        '''Return the list of nodes closer to the given one.'''


        for bucket in self.buckets:
            if bucket['min'] <= node.id and bucket['max'] > node.id:
                break

        return bucket


# www.rueckstiess.net/research/snippets/show/ca1d7d90
def unwrap_self_f(arg, **kwarg):
    return DHT.get_peers(*arg, **kwarg)

class DHT(object):
    '''This represents the Distributed Hash Table with its own queries
    
    See <www.bittorrent.org/beps/bep_0003.html>
    '''

    def __init__(self, network, node):
        self.network = network
        self.core_node = node
        self.buckets_list = BucketList()

    def ping(self, node):
        ping_query = {'y': 'q',
                      't': '0f',
                      'q': 'ping',
                      'a': {'id': self.core_node.id}}

        return self.network.send_to_node(node, ping_query)

    def get_peers(self, node, info_hash):
        get_peers_query = {
            'y': 'q',
            't': '0f',
            'q': 'get_peers',
            'a': {
                'id': self.core_node.id,
                'info_hash': hex2byte(info_hash),
            }
        }
        logger.info('asking to \'%s\' for peers related to hash \'%s\'' % (node, info_hash))
        response = self.network.send_to_node(node, get_peers_query)

        if not response:
            return None

        nodes = None
        if response.has_key('nodes'):
            nodes = NodeResponse(bt_nodes_info_from_raw_data(response['nodes']))
        elif response.has_key('values'):
            nodes = PeerResponse([bt_contact_peer(x) for x in response['values']])
        else:
            raise ValueError('Unexpected response: ' + response)

        # update the routing table
        for n in nodes:
            self.buckets_list.insert_node(n)

        return nodes

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

    mynode = Node(id=my_id, hostname='localhost')

    dht = DHT(Network, mynode)

    info_hash = 'bbb6db69965af769f664b6636e7914f8735141b3' if len(sys.argv) == 1 else sys.argv[1]

    node_info_hash = Node(id=hex2byte(info_hash), ip='fake')

    bootstrap_node = Node.get_boostrap_node()
    ping_response = dht.ping(bootstrap_node)
    print('ping response: %s' % ping_response)

    # save the bootstrap node's id
    bootstrap_node.id = ping_response['id']

    dht.buckets_list.insert_node(bootstrap_node)
    node_to_query = dht.buckets_list.get(node_info_hash)['nodes'][0]
    print(dht.get_peers(node_to_query, info_hash))
