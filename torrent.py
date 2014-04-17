#!/usr/bin/env python
import sys
import bencode
import hashlib


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: %s <torrent>' % sys.argv[0])
        sys.exit(1)

    filename = sys.argv[1]

    with open(filename) as torrent:
        content = torrent.read()
        content_debencoded = bencode.bdecode(content)

        m = hashlib.sha1(bencode.bencode(content_debencoded['info']))
        print(content_debencoded)
        print('info_hash: %s' % m.hexdigest())
