import sys, getopt, struct, time, termios, fcntl, sys, os, colorsys, requests, json, socket
from fcntl import ioctl
from DataAsset import CTX


class LogReporter:
    @staticmethod
    def SendLog(pCTX, activityType, activityInfo):

        url = ""

        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "x-api-key": pCTX.activityReportApiKey,
        }

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ifreq = struct.pack('256s', 'eth0')
        SIOCGIFHWADDR = 0x8927
        ifaddr = ioctl(sock.fileno(), SIOCGIFHWADDR, ifreq)
        hwaddr = ''.join(['%02x' % ord(char) for char in ifaddr[18:24]])[:-1]

        params = {
            'macAddr': hwaddr,
            'activityType': activityType,
            'activityInfo': activityInfo
        }

        r = requests.post(pCTX.activityReportApiUrl,
                          headers=headers,
                          data=params)
        print r.text
        #data = r.json()
        #print json.dumps(data, indent=4)

    @staticmethod
    def ReportDhcpClientInfo(pCTX, info, wanemId, isTmp):

        headers = {
            "content-type": "application/json",
            "x-api-key": pCTX.dhcpClientReportApiKey,
        }

        params = {
            'wanemId': wanemId,
            'clientHostname': info[3],
            'clientIp': info[1],
            'clientMacAddr': info[2],
            'registType': isTmp
        }

        r = requests.post(pCTX.dhcpClientReportApiUrl,
                          headers=headers,
                          data=json.dumps(params))
        print r.text
        #print json.dumps(params)


if __name__ == '__main__':
    #main(sys.argv[1:])
    LogReporter.SendLog(1, "Test")
