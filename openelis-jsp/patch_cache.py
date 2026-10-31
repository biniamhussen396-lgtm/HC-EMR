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

print "Found %d tableswitch opcodes" % len(switches)

# The target tableswitch is at file offset 0x2059
# It has: default=188, low=1, high=22
# Case 5 (ordinal for Dxc_700) is at offset 0x2059 + 8 + 4 + 4 + 4*4 = 0x2059+8+4+4+16 = 0x2059+32 = 0x2079
# Case 5 offset bytes: 0x2079 through 0x207c
# Currently: 00 00 00 bc (188) -> need to change to 00 00 00 74 (116)
# Default offset bytes: 0x205d through 0x2060
# Currently: 00 00 00 bc (188) -> need to change to 00 00 00 74 (116)

# Verify by checking the tableswitch at 0x2059
s = 0x2059
print "Tableswitch at 0x%04x:" % s
print "  Byte: 0x%02x" % data[s]
print "  Padding: %02x %02x %02x" % (data[s+1], data[s+2], data[s+3])
default_offset = struct.unpack('>i', str(data[s+4:s+8]))[0]
low = struct.unpack('>i', str(data[s+8:s+12]))[0]
high = struct.unpack('>i', str(data[s+12:s+16]))[0]
print "  Default offset: %d" % default_offset
print "  Low: %d, High: %d" % (low, high)

# Case offsets start at s+16, each 4 bytes
for case_num in range(low, high+1):
    case_offset_pos = s + 16 + (case_num - low) * 4
    case_offset = struct.unpack('>i', str(data[case_offset_pos:case_offset_pos+4]))[0]
    marker = " <-- DXC_700 (case 5), NEEDS PATCH" if case_num == 5 else ""
    print "  Case %d at 0x%04x: offset %d (0x%04x)%s" % (case_num, case_offset_pos, case_offset, case_offset, marker)

# Now patch: case 5 at 0x2079 from 188 to 116
case5_pos = 0x2079
current_val = struct.unpack('>i', str(data[case5_pos:case5_pos+4]))[0]
print "\nPatching case 5 at 0x%04x: %d -> 116" % (case5_pos, current_val)
data[case5_pos:case5_pos+4] = struct.pack('>i', 116)

# Also patch default from 188 to 116
default_pos = 0x205d
current_default = struct.unpack('>i', str(data[default_pos:default_pos+4]))[0]
print "Patching default at 0x%04x: %d -> 116" % (default_pos, current_default)
data[default_pos:default_pos+4] = struct.pack('>i', 116)

# Write back
open(filepath, "wb").write(data)
print "\nDone! File patched."

# Verify
data2 = open(filepath, "rb").read()
v1 = struct.unpack('>i', str(data2[case5_pos:case5_pos+4]))[0]
v2 = struct.unpack('>i', str(data2[default_pos:default_pos+4]))[0]
print "Verification: case5=%d, default=%d" % (v1, v2)
