import sys
import struct

filepath = sys.argv[1]
data = bytearray(open(filepath, "rb").read())

# Find all tableswitch opcodes (0xaa)
switches = []
idx = 0
while idx < len(data):
    if data[idx] == 0xaa:
        switches.append(idx)
    idx += 1

print "Found %d tableswitch opcodes:" % len(switches)
for s in switches:
    print "  0x%04x (dec %d)" % (s, s)

# The tableswitch we want is at file offset 0x002059
# But let's find it by looking for the pattern near each switch
for s in switches:
    # Print 16 bytes before and 80 bytes after
    start = max(0, s - 8)
    end = min(len(data), s + 80)
    print "\nSwitch at 0x%04x:" % s
    for i in range(s, end, 16):
        hexline = ""
        for j in range(i, min(i+16, end)):
            hexline += "%02x " % data[j]
        print "  0x%04x: %s" % (i, hexline)
