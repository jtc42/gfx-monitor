from gpiozero import CPUTemperature
import psutil

class StatScanner:
    # TODO: Add psutil.users()

    def __init__(self):
        self.cpu = CPUTemperature()

    @property
    def simple(self):
        mem_gb_total = psutil.virtual_memory().total/10**9
        mem_gb_used = psutil.virtual_memory().used/10**9
        mem_percent = psutil.virtual_memory().percent

        dsk_gb_total = psutil.disk_usage('/').total/10**9
        dsk_gb_used = psutil.disk_usage('/').used/10**9
        dsk_percent = psutil.disk_usage('/').percent

        d = {
            'cpu_temp': '{0:.1f}C'.format(self.cpu.temperature),
            'cpu_load': '{0:3d}%'.format(int(psutil.cpu_percent())),
            'cpu_freq': '{0:.1f}GHz'.format(psutil.cpu_freq().current/1000),
            'mem_info': '{0:.1f}/{1:.1f}GB'.format(mem_gb_used, mem_gb_total),
            'mem_perc': '{0:3d}%'.format(int(mem_percent)),
            'dsk_info': '{0:.1f}/{1:.1f}GB'.format(dsk_gb_used, dsk_gb_total),
            'dsk_perc': '{0:3d}%'.format(int(dsk_percent)),
        }
        
        return d

if __name__ == "__main__":
    scanner = StatScanner()
    print(scanner.simple)