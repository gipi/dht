#!/usr/bin/env python
import bencode
import random
import socket


def generate_random_id():
    # Generate a 160-bit (20-byte) random node ID.
    return ''.join([chr(random.randint(0, 255)) for _ in range(20)])

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
    ping_query_bencoded = bencode.bencode(ping_query)

    # Send a datagram to a server and recieve a response.
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(ping_query_bencoded,
             (socket.gethostbyname('router.bittorrent.com'), 6881))

    import ipdb;ipdb.set_trace()
    r = s.recvfrom(1024)

    '''
    The ping response contains in the 'ip' field the 4 bytes with the ip
    value followed by the port indicated with 2 bytes.
    '''
    ping_response = bencode.bdecode(r[0])

    print(ping_response)
    print r[1]

if __name__ == "__main__":
    my_id = generate_random_id()
    print('id: ' + my_id.encode('hex'))
    bootstrap(my_id)
