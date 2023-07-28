import time
from prometheus_client import start_http_server, Gauge
from pysnmp.hlapi import *

# Задаем параметры SNMP
device_ip = "your_device_ip"
community_string = "your_community_string"
snmp_port = 161
device_oid = "1.3.6.1.2.1.1.1.0"  # SysDescr

# Определяем метрику для Prometheus
g = Gauge('device_sys_descr', 'Description of device', ['device_ip'])

def get_data(ip, community, port, oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(community),
               UdpTransportTarget((ip, port)),
               ContextData(),
               ObjectType(ObjectIdentity(oid)))
    )
    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            return varBind[1].prettyPrint()

def collect_data():
    while True:
        data = get_data(device_ip, community_string, snmp_port, device_oid)
        g.labels(device_ip=device_ip).set(data)
        time.sleep(60)

if __name__ == "__main__":
    start_http_server(8000)
    collect_data()
