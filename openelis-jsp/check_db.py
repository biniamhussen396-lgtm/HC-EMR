import socket
try:
    ip = socket.gethostbyname('openelisdb')
    print 'openelisdb resolves to: ' + ip
except:
    print 'openelisdb does not resolve'
