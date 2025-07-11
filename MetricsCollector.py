import socket 
import errno
import time
import json

class MetricsNode():
    def __init__(self):
        self.rttList = [] # PPSによる
        self.send    = 0
        self.recv    = 0
        self.drop    = 0
        self.sid     = ''
        self.sendSum = 0
        self.recvSum = 0
        self.dropSum = 0

    def LoadJson(self, metricsMsg):
        try:
            jsonObj = json.loads(metricsMsg);
            self.sid     = jsonObj['sid']
            self.rttList = jsonObj['rtt']
            self.send    = jsonObj['s']
            self.recv    = jsonObj['r']
            self.drop    = jsonObj['d']
            self.sendSum = jsonObj['ts']
            self.recvSum = jsonObj['tr']
            self.dropSum = jsonObj['td']
            return True
            
        except Exception as e:
            print(f"JsonParse Error:{e}")
            return False

    def ImportNode(self, src):
        self.sid     = src.sid
        self.rttList = list(src.rttList) 
        self.send    = src.send
        self.recv    = src.recv
        self.drop    = src.drop
        self.sendSum = src.sendSum
        self.recvSum = src.recvSum
        self.dropSum = src.dropSum
        
    def RttMax(self):
        rtt = -1
        if len(self.rttList) == 0:
            return rtt
        for idx in range(0, len(self.rttList)):
            if (rtt == -1) or (self.rttList[idx] > rtt):
                rtt = self.rttList[idx]
        return rtt

    def RttMin(self):
        rtt = -1
        if len(self.rttList) == 0:
            return rtt
        for idx in range(0, len(self.rttList)):
            if (rtt == -1) or (self.rttList[idx] < rtt):
                rtt = self.rttList[idx]
        return rtt 

    def RttAvg(self):
        sum = 0
        if len(self.rttList) == 0:
            return 0
        for idx in range(0, len(self.rttList)):
            sum = sum + self.rttList[idx]
        rtt = int(sum / len(self.rttList))
        return rtt 

    def RttMdn(self):
        rtt = -1
        if len(self.rttList) == 0:
            return rtt
        seek = int(len(self.rttList) / 2)
        rtt = self.rttList[seek] 
        return rtt

    def LossRate(self):
        rate = 0.000
        if (self.send == 0) or (self.drop == 0):
            return rate
        rate = round((self.drop / (self.recv + self.drop)) * 100, 3)
        return rate

    def Dump(self):
        print("Rtt MAX > " + str(self.RttMax()))
        print("Rtt MIN > " + str(self.RttMin()))
        print("Rtt AVG > " + str(self.RttAvg()))
        print("Rtt MDN > " + str(self.RttMdn()))
        print("Loss    > " + str(self.LossRate()))
        print("Send Nr > " + str(self.send) + " / " + str(self.sendSum))
        print("Recv Nr > " + str(self.recv) + " / " + str(self.recvSum))
        print("Drop Nr > " + str(self.drop) + " / " + str(self.dropSum))
    
class MetricsCollector():
    def __init__(self, sid4 = '', sid6 = '', listenIp = '127.0.0.1', listenPort = 10394, nodeMax = 300):

        self.metricsList4 = []
        self.metricsList6 = []
        self.metricsCount4 = 0
        self.metricsCount6 = 0
        self.metricsSid4   = sid4
        self.metricsSid6   = sid6
        self.metricsNodeNr = nodeMax
        for idx in range(0, self.metricsNodeNr):
            self.metricsList4.append(MetricsNode())
            self.metricsList6.append(MetricsNode())
        
        self.listenAddr = (listenIp, listenPort)
        self.BUFSIZE = 1024 * 8
        self.udpServSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpServSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udpServSock.bind(self.listenAddr)
        self.udpServSock.setblocking(False)
        self.jsonBuf = MetricsNode()
        
    def GetMetricsCount4(self):
        return self.metricsCount4

    def GetMetricsCount6(self):
        return self.metricsCount6
    
    def GetLastMetrics4(self):
        if self.metricsCount4 == 0:
            return None        
        seek = (self.metricsCount4 - 1) % self.metricsNodeNr
        return self.metricsList4[seek]

    def GetLastMetrics6(self):
        if self.metricsCount6 == 0:
            return None        
        seek = (self.metricsCount6 - 1) % self.metricsNodeNr
        return self.metricsList6[seek]
    
    def GetMetricsByIdx4(self, idx):
        if self.metricsCount4 <= idx:
            return None        
        seek = idx % self.metricsNodeNr
        return self.metricsList4[seek]

    def GetMetricsByIdx6(self, idx):
        if self.metricsCount6 <= idx:
            return None        
        seek = idx % self.metricsNodeNr
        return self.metricsList6[seek]
    
#    def GetMetrics(self):
#        summary = MetricsNode()
#        for idx in range(0, self.metricsNodeNr):
#            if idx >= self.metricsCount:
#                break
#            summary.rttList.extend(self.metricsList[idx].rttList)
#            summary.send = summary.send + self.metricsList[idx].send
#            summary.recv = summary.recv + self.metricsList[idx].recv
#            summary.drop = summary.drop + self.metricsList[idx].drop
#        return summary
    
    def Recv(self, chkSet):
        isNewMetricsExist = False
        while True:
            try:
                data, addr = self.udpServSock.recvfrom(self.BUFSIZE)
                msg = data.decode()
                # print(msg, addr)

                if self.jsonBuf.LoadJson(msg) == True:
                    if self.jsonBuf.sid == self.metricsSid4:
                        seek = self.metricsCount4 % self.metricsNodeNr
                        self.metricsList4[seek].ImportNode(self.jsonBuf)
                        self.metricsCount4 = self.metricsCount4 + 1
                        chkSet[0] = True
                        isNewMetricsExist = True
                    elif self.jsonBuf.sid == self.metricsSid6:
                        seek = self.metricsCount6 % self.metricsNodeNr
                        self.metricsList6[seek].ImportNode(self.jsonBuf)
                        self.metricsCount6 = self.metricsCount6 + 1
                        chkSet[1] = True
                        isNewMetricsExist = True
                    else:
                        print("Invalid Session Id. Ignore. >> " + self.jsonBuf.sid)
                        
            except socket.error as e:
                if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                    break
                else:
                    print(f"Socket Error:{e}")
                    break
                
            return isNewMetricsExist
            

##[ TEST ]###############################################

if __name__ == '__main__':
    
    collector = MetricsCollector('0.0.0.0')

    while True:
        print(time.time())
        if collector.Recv() == True:
            # Render
            # metrics = collector.GetLastMetrics4()
            # metrics.Dump()
            # metrics = collector.GetLastMetrics6()
            # metrics.Dump()
            if (collector.GetMetricsCount4() % 5) == 0:
                print("==[ SUM ] ============================")
                metrics = collector.GetLastMetrics4()
                metrics.Dump()
                print("======================================")
            if (collector.GetMetricsCount6() % 5) == 0:
                print("==[ SUM ] ============================")
                metrics = collector.GetLastMetrics6()
                metrics.Dump()
                print("======================================")
        time.sleep(1)
    
#########################################################
