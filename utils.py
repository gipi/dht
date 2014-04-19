from models import Node

def chunks(l, n):
    if n < 1:
        n = 1
    for i in range(0, len(l), n):
        yield l[i:i+n]

def s2ip(data):
    return '.'.join([str(int(x.encode('hex'), 16)) for x in data])

def hex2byte(data):
    '''Returns the raw bytes from an hex encoded string
    
        >>> hex2byte('0001414243ba')
        '\\x00\\x01ABC\\xba'
    '''
    return ''.join([chr(int(x, 16)) for x in chunks(data, 2)])

def bt_contact_node(raw_data):
    '''Contact information for nodes is encoded as 26 bytes string.
    
     - 20 bytes node id
     - 4  bytes node ip
     - 2  bytes node port
    '''
    node_id = raw_data[:20].encode('hex')
    node_ip = s2ip(raw_data[20:24])
    node_port = int(raw_data[24:].encode('hex'), 16)

    return Node(id=node_id, ip=node_ip, port=node_port)
