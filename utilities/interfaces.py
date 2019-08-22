import netifaces

class IfaceScanner:
    def __init__(self, ifaces=["eth0", "wlan0"]):
        self.ifaces = ifaces

    @property
    def simple(self):
        d = {}
        available_ifaces = netifaces.interfaces()

        for iface in self.ifaces:
            if iface not in available_ifaces:
                d[iface] = "Unavailable"
            else:
                iface_addresses = netifaces.ifaddresses(iface)

                if not 2 in iface_addresses:  # If no AF_INET block
                    d[iface] = "Disconnected"
                else:
                    d[iface] = iface_addresses[2][0]['addr']
        
        return d

if __name__ == "__main__":
    scanner = IfaceScanner()
    print(scanner.simple)