#!/usr/bin/python2

try:
  from lxml import etree
  print("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    print("running with cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      print("running with ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        print("running with cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          print("running with ElementTree")
        except ImportError:
          print("Failed to import ElementTree from any known place")


import math

num_status=int(input("Please input the number of status register: "))
num_control=int(input("Please input the number of control register: "))
num_wfifo=int(input("Please input the number of read FIFO: "))
num_rfifo=int(input("Please input the number of write FIFO: "))

print("Generating...")

def calc_width(x):
    for i in range(32):
        if math.pow(2,i) >= x:
            return (i)

def max(a,b):
    return a if a>=b else b

def reg_slave_num(control,status):
    return 1 if (control>0 or status>0) else 0

def max_port_addr_width(ctl_reg_num,sta_reg_num,wfifo_num,rfifo_num):
    reg_address_width = calc_width(max(ctl_reg_num,sta_reg_num))+1;
    fifo_address_width = calc_width(wfifo_num+rfifo_num)+2;
    return fifo_address_width if (ctl_reg_num==0 and sta_reg_num==0) else (max(reg_address_width,fifo_address_width)+1)

ADDR_WIDTH = max(calc_width(num_status),calc_width(num_control))

REG_SLV_NUM = reg_slave_num(num_control,num_status)
NSLV = REG_SLV_NUM + num_wfifo + num_rfifo
MAX_ADDR_NUM = max_port_addr_width(num_control,num_status,num_wfifo,num_wfifo)

## generate connection xml file
root = etree.Element('connections')
doc = etree.SubElement(root,'connection',id="dummy.udp.0",uri="ipbusudp-2.0://192.168.0.1:50001",address_table="file://ipbus_slave_reg_fifo.xml")

content = etree.tostring(root, pretty_print=True, xml_declaration=True,encoding="UTF-8")
f=open('./connection.xml','w+')
f.write(content)
f.close()
####################################
#generate fifo and register address#
####################################
write="w"
read="r"
read_write="rw"

top = etree.Element('node',id="ipbus_slave_reg_fifo")

addr=0;
##  register address ##
if(REG_SLV_NUM==1):
    for i in range(num_status):
        reg_addr = int(addr + i)
        node_stat = etree.SubElement(top,'node',id="STAT"+str(i),address=hex(reg_addr),perimission=read)
    tmp_addr = int(addr+math.pow(2,ADDR_WIDTH))
    for i in range(num_control):
        stat_addr = int(tmp_addr + i)
        node_cntl = etree.SubElement(top,'node',id="CNTL"+str(i),address=hex(stat_addr),perimission=read_write)

## fifo address ##
wfifo_id=("WFIFO_DATA","WFIFO_LEN","WVALID_LEN")
rfifo_id=("RFIFO_DATA","RFIFO_LEN","RVALID_LEN")
fifo_wr_mode="non-incremental"

# when number of refister is zero #
if(REG_SLV_NUM==0):
    for i in range(num_wfifo):
        tmp_wfifo_addr = int(addr+i*math.pow(2,2))
        for j in range(3):
            wid=wfifo_id[j]
            tmp_wfifo_cntl_addr = int(tmp_wfifo_addr+j)
            if(j==0):
                node_wfifo = etree.SubElement(top,'node',id="WFIFO"+str(i)+'.'+wid,address=hex(tmp_wfifo_cntl_addr),mode=fifo_wr_mode,perimission=read)
            else:
                node_wfifo = etree.SubElement(top,'node',id="WFIFO"+str(i)+'.'+wid,address=hex(tmp_wfifo_cntl_addr),perimission=read)

    for i in range(num_rfifo):
        tmp_rfifo_addr = int(addr+num_wfifo*math.pow(2,2)+i)
        for j in range(3):
            rid=rfifo_id[j]
            tmp_rfifo_cntl_addr = int(tmp_rfifo_addr+j)
            if(j==0):
                node_rfifo = etree.SubElement(top,'node',id="RFIFO"+str(i)+'.'+rid,address=hex(tmp_rfifo_cntl_addr),mode=fifo_wr_mode,perimission=write)
            else:
                node_rfifo = etree.SubElement(top,'node',id="RFIFO"+str(i)+'.'+wid,address=hex(tmp_rfifo_cntl_addr),perimission=read)

# when the number of register is not zero #
if(REG_SLV_NUM==1):
    for i in range(num_wfifo):
        tmp_wfifo_addr = int(addr+i*math.pow(2,2)+math.pow(2,MAX_ADDR_NUM-1))
        for j in range(3):
            wid=wfifo_id[j]
            tmp_wfifo_cntl_addr = int(tmp_wfifo_addr+j)
            if(j==0):
                node_wfifo = etree.SubElement(top,'node',id="WFIFO"+str(i)+'.'+wid,address=hex(tmp_wfifo_cntl_addr),mode=fifo_wr_mode,perimission=read)
            else:
                node_wfifo = etree.SubElement(top,'node',id="WFIFO"+str(i)+'.'+wid,address=hex(tmp_wfifo_cntl_addr),perimission=read)

    for i in range(num_rfifo):
        tmp_rfifo_addr = int(addr+num_wfifo*math.pow(2,2)+i+math.pow(2,MAX_ADDR_NUM-1))
        for j in range(3):
            rid=rfifo_id[j]
            tmp_rfifo_cntl_addr = int(tmp_rfifo_addr+j)
            if(j==0):
                node_rfifo = etree.SubElement(top,'node',id="RFIFO"+str(i)+'.'+rid,address=hex(tmp_rfifo_cntl_addr),mode=fifo_wr_mode,perimission=write)
            else:
                node_rfifo = etree.SubElement(top,'node',id="RFIFO"+str(i)+'.'+wid,address=hex(tmp_rfifo_cntl_addr),perimission=read)

## write to file ##
content = etree.tostring(top, pretty_print=True,encoding="ISO-8859-1")
f=open('./ipbus_slave_reg_fifo.xml','w+')
f.write(content)
f.close()
print("Finished!")
