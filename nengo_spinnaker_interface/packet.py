"""
Facilities for network communication between the Nengo workbench and SpiNNaker:
 - **class Packet**: defines an SDP packet, to be sent/received to/from SpiNNaker
 - **class UDPValueReceiver**: used to receive SDP packets from SpiNNaker and plotting values
 - **class UDPValueSender**: used to send SDP commands to SpiNNaker as input values
"""

import struct
import nef
import java
import jarray
import struct
import numeric
import ca

class Packet:

  def __init__(self):
    self.SPINN_HEADER = 'HIIII'
    self.SDP_HEADER = '<BBBBHHIIII'
    self.SPINN_HEADER_SIZE = struct.calcsize(self.SPINN_HEADER)
    self.SDP_HEADER_SIZE = struct.calcsize(self.SDP_HEADER)

    self.tx_spinn_header = {
      'prot' : 0,
      'cmd' : 0,
      'arg0' : 0,
      'arg1' : 0,
      'arg2' : 0
    }

    self.tx_sdp_header = {
      'flags' : 0,
      'ip_tag' : 0,
      'dst_port' : 0,
      'src_port' : 0,
      'dst_chip' : 0,
      'src_chip' : 0,
      'cmd' : 0,
      'arg0' : 0,
      'arg1' : 0,
      'arg2' : 0
    }

    self.rx_spinn_header = {
      'prot' : 0,
      'cmd' : 0,
      'arg0' : 0,
      'arg1' : 0,
      'arg2' : 0
    }

    self.rx_sdp_header = {
      'flags' : 0,
      'ip_tag' : 0,
      'dst_port' : 0,
      'src_port' : 0,
      'dst_chip' : 0,
      'src_chip' : 0,
      'cmd' : 0,
      'arg0' : 0,
      'arg1' : 0,
      'arg2' : 0
    }



  def pack_spinn_header(self, endianness=False):
    '''Return headers of SpiNNaker packet packed into a string for
       transmission over Ethernet. The endianness argument determines whether
       the data is packed in host or network order. It must be set to True for
       system software loading (the boot ROM code performs hardware ntoh).'''
    format = endianness and ('>' + self.SPINN_HEADER) or ('=' + self.SPINN_HEADER)
    return struct.pack(format,
                       self.tx_spinn_header['prot'],
                       self.tx_spinn_header['cmd'],
                       self.tx_spinn_header['arg0'],
                       self.tx_spinn_header['arg1'],
                       self.tx_spinn_header['arg2'])



  def pack_sdp_header(self):
    '''Return headers of an SDP message packet into a string for transmission
       over Ethernet. No endianness option is given: SDP messages are processed
       by system software (not bootROM) which receives all network comms in
       little endian order.'''
    return struct.pack(self.SDP_HEADER,
                        self.tx_sdp_header['flags'],
                        self.tx_sdp_header['ip_tag'],
                        self.tx_sdp_header['dst_port'],
                        self.tx_sdp_header['src_port'],
                        self.tx_sdp_header['dst_chip'],
                        self.tx_sdp_header['src_chip'],
                        self.tx_sdp_header['cmd'],
                        self.tx_sdp_header['arg0'],
                        self.tx_sdp_header['arg1'],
                        self.tx_sdp_header['arg2'])



  def unpack_spinn_header(self, data):
    unpack = struct.unpack('IIII', data[:self.SPINN_HEADER_SIZE])
    self.rx_spinn_header['prot'] = unpack[0]
    self.rx_spinn_header['cmd'] = unpack[1]
    self.rx_spinn_header['arg0'] = unpack[2]
    self.rx_spinn_header['arg1'] = unpack[3]
    self.rx_spinn_header['arg2'] = unpack[4]



  def unpack_sdp_header(self, data):
    struct.unpack('BBBBHHIIII', data[:self.SPINN_HEADER_SIZE][:self.SDP_HEADER_SIZE])
    self.rx_sdp_header['flags'] = unpack[0]
    self.rx_sdp_header['ip_tag'] = unpack[1]
    self.rx_sdp_header['dst_port'] = unpack[2]
    self.rx_sdp_header['src_port'] = unpack[3]
    self.rx_sdp_header['dst_chip'] = unpack[4]
    self.rx_sdp_header['src_chip'] = unpack[5]
    self.rx_sdp_header['cmd'] = unpack[6]
    self.rx_sdp_header['arg0'] = unpack[8]
    self.rx_sdp_header['arg1'] = unpack[9]
    self.rx_sdp_header['arg2'] = unpack[10]


class UDPValueSender(nef.SimpleNode):
    """
    UDPValueSender
    
    SYNTAX: UDPValueSender(name, address, port, dest_core_id)
     - *name* is a network identifier (used to save layout info)
     - *dest_core_id* is a SpiNNaker input core in (0,0) equipped with a lif_nef_multidimensional population
     
    At every tick (set in Nengo) a packet is sent to address:port:(0, 0, dest_core_id)
    """

    pstc=0
    def __init__(self, name, address, port, dest_core_id):
        nef.SimpleNode.__init__(self,name)
        self.socket=java.net.DatagramSocket()
        self.address=java.net.InetAddress.getByName(address)
        self.port=port
        self.header=Packet()
        self.last_value=None
        self.header.tx_sdp_header=dict(flags=7, ip_tag=255, dst_port=(4<<5)+dest_core_id, src_port=255, dst_chip=0, src_chip=0, cmd=257, arg0=1, arg1=0, arg2=0)
       
    def termination_input(self,x,dimensions=2):
        self.data=x
       
    def tick(self):
        data=[int(x*256) for x in self.data]
#        print self.t_start,data
        if data!=self.last_value:
            self.header.tx_sdp_header['arg0']=1
            start=struct.pack('BB',0x01,00)
            msg=start+self.header.pack_sdp_header()
            for d in data:
                msg+=struct.pack('<I',d)
            packet=java.net.DatagramPacket(msg,len(msg),self.address,self.port)
            self.socket.send(packet)
            self.last_value=data
        
        


class UDPValueReceiver(nef.SimpleNode):
    """
    UDPValueReceiver
    
    SYNTAX: UDPValueReceiver(name, source_core_id)
     - *name* is a network identifier (used to save layout info)
     - *source_core_id* is a SpiNNaker core in (0,0) equipped with a nef_out_multidimensional population
     
    At every tick (set in Nengo) a packet is received, unpacked and elaborated if it corresponds to the source_core_id
    """
    def __init__(self,name, dimensions=2,port=54321, source_core_id=1):
       self.socket=java.net.DatagramSocket(port)
       self.source_core_id = source_core_id
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
            int0=struct.unpack('<I',struct.pack('>I',d.readInt()))[0]
            int1=struct.unpack('<I',struct.pack('>I',d.readInt()))[0]
            d.readInt()
            d.readInt()
            int4=struct.unpack('<i',struct.pack('>i',d.readInt()))[0]
            int5=struct.unpack('<i',struct.pack('>i',d.readInt()))[0]

            if (code & 31) == self.source_core_id and int0==258 and int1==1:    
                self.value[0]=int4/256.0
                self.value[1]=int5/256.0

            
    def origin_value(self):
        return self.value

class NullOutputStream(java.io.OutputStream):
    def write(*args):
        pass
        
real_out=java.lang.System.out
java.lang.System.setOut(java.io.PrintStream(NullOutputStream()))

from org.apache.log4j import Logger,Level

logger=Logger.getLogger(ca.nengo.util.Memory)
logger.setLevel(Level.FATAL)

