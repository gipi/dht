from models import Node, Peer

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
