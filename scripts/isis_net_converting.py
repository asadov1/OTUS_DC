# -*- coding: utf-8 -*-

def isis_net(ip_add):
    area = "0001"
    isis_net = ip_add.split(".")
    net_isis = ""
    for octets in isis_net:
        pad_octets = octets.zfill(3)
        net_isis += pad_octets
    result = '.'.join(net_isis[i:i+4] for i in range(0, len(net_isis), 4))
    return f"49.{area}.{result}.00"

# Более красиво
# def isis_net(ip_add):
#     net_isis = '.'.join(map(lambda x: x.zfill(3), ip_add.split(".")))
#     result = '.'.join(net_isis[i:i+4] for i in range(0, len(net_isis), 4))
#     return f"49.{area}.{result}.00"

if __name__ == '__main__':
    ip = "10.0.1.2"
    area = "0001"
    print(isis_net(ip))
