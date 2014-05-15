import socket
from utils import byte2hex, chunks, s2ip


class Node(object):
    def __init__(self, id=None, hostname=None, ip=None, port=6881):
        if hostname is None and ip is None:
            raise AttributeError('You must indicate ip or hostname')

        if hostname is not None:
            ip = socket.gethostbyname(hostname)

        self.id = id
        self.ip = ip
        self.port = port

    @classmethod
    def get_boostrap_node(klass):
        return Node(hostname='router.bittorrent.com')

    def __unicode__(self):
        return u'%s %s %d' % (self.id, self.ip, self.port)

    def __str__(self):
        return self.__unicode__()

class Peer(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def __unicode__(self):
        return u'%s %d' % (self.ip, self.port)

    def __str__(self):
        return self.__unicode__()
def bt_contact_node(raw_data):
    '''Contact information for nodes is encoded as 26 bytes string.
    
     - 20 bytes node id
     - 4  bytes node ip
     - 2  bytes node port
    '''
    if len(raw_data) != 26:
        raise ValueError('data must be 26 bytes long')

    node_id = raw_data[:20].encode('hex')
    node_ip = s2ip(raw_data[20:24])
    node_port = int(raw_data[24:].encode('hex'), 16)

    return Node(id=node_id, ip=node_ip, port=node_port)

def bt_contact_peer(raw_data):
    if len(raw_data) != 6:
        raise ValueError('data must be 6 bytes long')

    node_ip = s2ip(raw_data[0:4])
    node_port = int(raw_data[4:].encode('hex'), 16)

    return Peer(node_ip, node_port)

def bt_nodes_info_from_raw_data(data):
    return [bt_contact_node(x) for x in chunks(data, 26)]

