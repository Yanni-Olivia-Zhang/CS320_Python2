import re
import pandas as pd
import netaddr
from bisect import bisect

ips = pd.read_csv("ip2location.csv")

def lookup_region(ip_addr):
    ip_new = re.sub(r"[a-z]", "0", ip_addr)
    myipint = int(netaddr.IPAddress(ip_new))
    idx = bisect(ips["low"],myipint)
    region = ips.iloc[idx-1]["region"]
    return region

class Filing:
    def __init__(self, html):
        raw_dates = re.findall(r"\d{4}\-\d{2}\-\d{2}", html)
        self.dates = [date for date in raw_dates if date.startswith("19") or date.startswith("20")]
        
        sic_list = re.findall(r"SIC=[^0-9]*?(\d+)",html)
        if sic_list != []:
            self.sic = int(sic_list[0])
        else:
            self.sic = None
       
        addr_list = []
        for addr_html in re.findall(r'<div class="mailer">([\s\S]+?)</div>', html):
            lines=[]
            for line in re.findall(r'<span class="mailerAddress">([\s\S]+?)</span>', addr_html):
                if line.strip() != '':
                    lines.append(line.strip())
            if lines != []:
                addr_list.append("\n".join(lines))
        self.addresses = addr_list

    def state(self):
        for addr in self.addresses:
            state = re.findall(r'[A-Z]{2}\s\d{5}', addr)
            if state != []:
                return state[0].split(' ')[0]
        return None
                