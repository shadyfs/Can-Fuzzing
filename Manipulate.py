import os
import time
import binascii
for i in range(10000):

    #a = binascii.b2a_hex(os.urandom(8))
    #s = "cansend vcan0 0CF00400#" + a.decode("utf-8")
    #os.system(s)
    #time.sleep(0.02)
    os.system("cansend vcan0 0CF00400#0000000000000000")