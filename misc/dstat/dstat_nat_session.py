class dstat_plugin(dstat):
    def __init__(self):
        self.name   = 'NAT Session'
        self.nick   = ('tcp','udp')
        self.vars   = ('tcpNr', 'udpNr')
        self.type   = 's'
        self.width  = 8
        self.scale  = 0

    def Update(self):
        import commands
        self.val['tcpNr'] = commands.getoutput("cat /proc/net/nf_conntrack | grep tcp | wc -l ")
        self.val['udpNr'] = commands.getoutput("cat /proc/net/nf_conntrack | grep udp | wc -l ")
        
    def extract(self):
        self.Update()
