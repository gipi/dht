'''
Utilities to encode/decode raw data.
'''

def xor(a, b):
    '''Calculates the XOR between two strings.
    
        >>> xor('\\x00', '\\x01')
        '\\x01'
    '''
    return ''.join([chr(ord(x)^ord(y)) for (x,y) in zip(a, b)])

def k(value):
    '''Returns the zero-index of the bucket entry where this id should go.

    For each 0 <= i < 160, every node keeps a list of info for nodes
    of distance between 2^i and 2^i+1 (excluded) from itself.
    
        >>> k(16)
        4
        >>> k(0)
        0
        >>> k(1)
        0
        >>> k(2)
        1
        >>> k(2**159)
        159
    '''
    if isinstance(value, basestring):
        value = int(value.encode('hex'), 16)
    # bits necessary to describe the value minus the '0b' prefix
    b = bin(value)[2:]
    # since is 0-indexed adjust the value correctly
    return len(b) - 1

def chunks(l, n):
    if n < 1:
        n = 1
    for i in range(0, len(l), n):
        yield l[i:i+n]

def s2ip(data):
    return '.'.join([str(int(x.encode('hex'), 16)) for x in data])

def byte2hex(data):
    '''Returns the hex representation of raw string.

        >>> byte2hex('\\x01\\x02\\x03\\x04')
        '01020304'
    '''
    return ''.join(['%02x' % ord(x) for x in data])

def hex2byte(data):
    '''Returns the raw bytes from an hex encoded string
    
        >>> hex2byte('0001414243ba')
        '\\x00\\x01ABC\\xba'
    '''
    return ''.join([chr(int(x, 16)) for x in chunks(data, 2)])

def byte2int(data):
    return int(byte2hex(data), 16)

