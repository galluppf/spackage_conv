"""
Script to instantiate a viewer integrating the Nengo workbench with SpiNNaker with a single 1D input and a single 1D output.

./nengo-cl scripts/viewers/2dviewer_args.py -n 2d_view -b big-robospinn-local -d 1 -s 2
 - -n : sets the network_name (identifier for layouts)
 - -b : identifies the SpiNNaker board to use
 - -d : sets the target core in chip (0,0) of the SpiNNaker board receiving UDP packets sent by the UDPValueSender
 - -s : sets the source core in chip (0,0) of the SpiNNaker board sending UDP packets received by the UDPValueReceiver
"""


import nef
import java
import jarray
import struct
import numeric
import nengo_spinnaker_interface.packet as packet

import getopt
opts, args = getopt.getopt(sys.argv[1:], 'b:n:d:s:')

board_name = ""
network_name = ""
source_core_id = dest_core_id = 0

for o, a in opts:
    if o == "-b":
        board_name = a
    elif o == "-n":
        network_name = a
    elif o == "-s":
        source_core_id = eval(a)
    elif o == "-d":
        dest_core_id = eval(a)



class NullOutputStream(java.io.OutputStream):
    def write(*args):
        pass
real_out=java.lang.System.out
java.lang.System.setOut(java.io.PrintStream(NullOutputStream()))

from org.apache.log4j import Logger,Level
logger=Logger.getLogger(ca.nengo.util.Memory)
logger.setLevel(Level.FATAL)



class SpikeSender(nef.SimpleNode):
    def __init__(self,name,ensemble):
        nef.SimpleNode.__init__(self,name)
        self.ensemble=ensemble
        self.datastream=java.io.DataOutputStream(real_out)
    def tick(self):
        data=self.ensemble.getOrigin('AXON').getValues().getValues()
        for i,spike in enumerate(data):
            if spike:
                self.datastream.writeBytes(struct.pack('<I',i+2048))        
        self.datastream.writeInt(0xFFFFFFFF)

class UDPValueSender(nef.SimpleNode):
    pstc=0
    def __init__(self,name,address,port):
        nef.SimpleNode.__init__(self,name)
        self.socket=java.net.DatagramSocket()
        self.address=java.net.InetAddress.getByName(address)
        self.port=port
        self.header=packet.Packet()
        self.last_value=None
        self.header.tx_sdp_header=dict(flags=7,ip_tag=255,dst_port=(4<<5)+dest_core_id,src_port=255,dst_chip=0,src_chip=0,cmd=257,arg0=1,arg1=0,arg2=0)
       
    def termination_input(self,x):
        self.data=x
       
    def tick(self):
        data=int(self.data[0] * 256)
#        print self.t_start,data
        if data!=self.last_value:
            self.header.tx_sdp_header['arg0']=1
            start=struct.pack('BB',0x01,00)
            msg=start+self.header.pack_sdp_header()
            msg+=struct.pack('<I',data)
            packet=java.net.DatagramPacket(msg,len(msg),self.address,self.port)
            self.socket.send(packet)
            self.last_value=data
        
        


class UDPValueReceiver(nef.SimpleNode):
    def __init__(self,name,dimensions=2,port=54321):
       self.socket=java.net.DatagramSocket(port)
       maxLength=65535
       self.buffer=jarray.zeros(maxLength,'b')
       self.packet=java.net.DatagramPacket(self.buffer,maxLength)
       self.dimensions=dimensions
       self.value=[0]*dimensions
       nef.SimpleNode.__init__(self,name)
    def tick(self):
        if self.t_start>0:
            self.socket.receive(self.packet)
            d=java.io.DataInputStream(java.io.ByteArrayInputStream(self.packet.getData()))
            d.readByte()
            d.readByte()
            d.readByte()
            d.readByte()
            d.readByte()
            code=d.readByte()
            d.readShort()
            d.readShort()
            cmd_rc=struct.unpack('<I',struct.pack('>I',d.readInt()))[0]
            int1=struct.unpack('<I',struct.pack('>I',d.readInt()))[0]       # arg1?
            d.readInt()                                                     # arg2?
            d.readInt()                                                     # arg3?
            int4=struct.unpack('<i',struct.pack('>i',d.readInt()))[0]       # payload (1 int)
#            print code, cmd_rc, int4
#            if code&0xE0==0x80 and cmd_rc==257 and int1==1:
#            if code==0x83 and cmd_rc==257 and int1==1:
#            if (code & 0x1F) == 2 and cmd_rc==257 and int1==1:
            if (code & 0x1F) == source_core_id and cmd_rc==258 and int1==1:    
                self.value[0]=int4/256.0
#                print "received", self.value[0],self.value, "from core:", code & 0x1F
            if (code & 0x1F) == 3 and cmd_rc==258 and int1==1:    
                self.value[1]=int4/256.0
##                print "received", self.value[0],self.value, "from core:", code & 0x1F

            
    def origin_value(self):
        return self.value
        
            
net=nef.Network('Test SpiNNaker',quick=True)
input=net.make_input('input',[0])
A=net.make('A',100,1,max_rate=[10,10])
B=net.make('B',100,1,max_rate=[10,10])
net.connect(input,A)
net.connect(A,B)

#ss=SpikeSender('ss',A)
#net.add(ss)
uvs=UDPValueSender('uss',board_name,17893)
net.add(uvs)

net.connect(input,uvs.getTermination("input"))

uvr=UDPValueReceiver('uvr')
net.add(uvr)


net.view()

                
                
