def chunks(l, n):
    if n < 1:
        n = 1
    for i in range(0, len(l), n):
        yield l[i:i+n]

def s2ip(data):
    return '.'.join([str(int(x.encode('hex'), 16)) for x in data])

def bt_contact_node(raw_data):
    '''Contact information for nodes is encoded as 26 bits string.
    
     - 20 bytes node id
     - 4  bytes node ip
     - 2  bytes node port
    '''
    node_id = raw_data[:20].encode('hex')
    node_ip = s2ip(raw_data[20:24])
    node_port = int(raw_data[24:].encode('hex'), 16)

    return node_id, node_ip, node_port
