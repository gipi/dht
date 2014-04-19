import socket


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

