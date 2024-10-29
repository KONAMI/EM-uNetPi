import time, sys, subprocess, random


class HttpUtil:
    @staticmethod
    def CheckConnectivity(host, retryLimit, proxy=""):
        proxyArg = ""
        if proxy != "":
            proxyArg = "--proxy " + str(proxy)
        cmd = "curl " + proxyArg + " -s -m 5 -o /dev/null " + host + "?" + str(
            random.random())
        ret = False
        retryCnt = 0
        while ret == False:
            try:
                print("HttpCheck >> " + cmd);
                subprocess.check_call(cmd.strip().split(" "))
                ret = True
            except subprocess.CalledProcessError:
                print("HttpCheck Fail. Retry after 1sec.")
                time.sleep(1)
                retryCnt += 1
                if retryLimit > 0 and retryLimit <= retryCnt:
                    break
        return ret

    @staticmethod
    def Get(url, savePath, retryLimit, proxy=""):
        proxyArg = ""
        if proxy != "":
            proxyArg = "--proxy " + str(proxy)
#        cmd = "curl " + proxyArg + " -s -m 5 -o " + savePath + " " + url
        cmd = "wget " + url + " -O " + savePath + " --timeout=5"
        print("Get >> " + cmd);
        ret = False
        retryCnt = 0
        while ret == False:
            try:
                subprocess.check_call(cmd.strip().split(" "))
                ret = True
            except subprocess.CalledProcessError:
                print("HttpCheck Fail. Retry after 1sec.")
                time.sleep(1)
                retryCnt += 1
                if retryLimit > 0 and retryLimit <= retryCnt:
                    break
        return ret
