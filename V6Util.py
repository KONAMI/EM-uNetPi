import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, threading, time, datetime, subprocess

class V6Util:

    @staticmethod
    def IsLinklocal(addrStr):
        ret = False
        addr = addrStr.split(':')
        prefix = int(addr[0], 16)

        #print(addr[0])
        #print(hex(prefix))
        #print(hex((prefix >> 8)))
        #print(hex(prefix & 0xff))
    
        if ((prefix >> 8) == 0xfe) and (prefix & 0xc0 == 0x80):
            ret = True
    
        return ret

    @staticmethod
    def IsV6Enabled():
    
        cmd = "ip addr show dev eth0"
        v6Stat = -1

        try:
            cmdOut = subprocess.check_output(cmd.strip().split(" "))
            records = cmdOut.decode().strip().split('\n')
            #print(records)
        
            for record in records:
                if("inet6" in record):
                    elms = record.strip().split()                
                    #print(elms)
                    addr = elms[1]
                    isLinkLocal = V6Util.IsLinklocal(addr)
                    #print(addr + " >> Is Link Local >> " + str(isLinkLocal))
                    if isLinkLocal == False:
                        v6Stat = 1
                        break
                    else:
                        v6Stat = 0
        
        except subprocess.CalledProcessError:
            print(cmd + " >> Error")
            v6Stat = -1

            return True if v6Stat == 1 else False

    @staticmethod    
    def GetGua():
    
        cmd = "ip addr show dev eth0"
        ret = []

        try:
            cmdOut = subprocess.check_output(cmd.strip().split(" "))
            records = cmdOut.decode().strip().split('\n')
            #print(records)
        
            for record in records:
                if("inet6" in record):
                    elms = record.strip().split()                
                    #print(elms)
                    addr = elms[1]
                    isLinkLocal = V6Util.IsLinklocal(addr)
                    #print(addr + " >> Is Link Local >> " + str(isLinkLocal))
                    if isLinkLocal == False:
                        ret.append(addr)
        
        except subprocess.CalledProcessError:
            print(cmd + " >> Error")

        return ret

""" sample code

def main(argv):
    print("IsV6Enabled >> " + str(V6Util.IsV6Enabled()))
    
    addrList = V6Util.GetGua()
    print("GUA Nr " + str(len(addrList)))
    for addr in addrList:
        print("GUA >> " + addr)
    
if __name__ == '__main__':
    main(sys.argv[1:])
        
"""
