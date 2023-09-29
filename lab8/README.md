# ДЗ №8

### Цели:

- Настроить отказоустойчивое подключение клиентов с использованием VPC

**План IP адресации**

- _**P2P IP = 10.Dn.Sn.X/31, где:**_

  DN - номер ЦОД;

  SN - номер Spine коммутатора;

  X - значение по порядку

- _**Dn для DC1 =  0 - 7, где:**_

  **0** - первый пул loopback адресов;

  **1** - второй пул loopback адресов;

  **2** - адресация p2p интерфейсов;

  **3** - резерв;

  **4-7** - адресация для сервисов

**Таблиа распределения IP подсетей:**

|          Description          | IP_subnet_pod1_nxos | IP_subnet_pod2_eos |
| :---------------------------: | :-----------------: | :----------------: |
| P2P_Spine**1**_to_LeafN _/31  |   10.2.**1**.0/24   |  10.10.**1**.0/24  |
| P2P_Spine**2**_to_LeafN  _/31 |   10.2.**2**.0/24   |  10.10.**2**.0/24  |
|           Loopback            |     10.0.0.0/24     |    10.8.0.0/24     |
|           Loopback            |     10.1.0.0/24     |    10.9.0.0/24     |
|           Service_1           |     10.4.0.0/24     |    10.11.0.0/24    |
|           Service_2           |     10.4.1.0/24     |    10.11.1.0/24    |
|           Service_3           |     10.4.2.0/24     |    10.11.2.0/24    |
|           Service_4           |     10.4.3.0/24     |    10.11.3.0/24    |

**Таблиа распределения vlan/vni/subnet подсетей:**

| Description | VLAN |  VNI  |    Subnet    |
| :---------: | :--: | :---: | :----------: |
|  Service_1  |  21  | 10021 | 10.11.1.0/24 |
|  Service_2  |  22  | 10022 | 10.11.2.0/24 |

**Топология EVE :**

<img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab8/lab_8_topology_vpc.png" style="zoom:200%;" />

_**Выполненые действия по конфигурированию :**_

- _настроены Underlay и Overlay. Маршуритизация в обоих случаях iBGP_
- _настроены L2 и L3 VNI_
- _на leaf1 и leaf2 сделаны консистентные настройки для работы vpc_
- _для эмуляции клиентского оборудования добавлен еще один Cisco Nexus (CE) и настроен port-channel 100_



### Примененные конфигурации:

_**Пример конфигурации интерфейса spine/leaf :**_

```
interface Ethernet1
   mtu 9214
   no switchport
   ip address 10.10.1.1/31
   bfd echo
   
interface Loopback0
   ip address 10.8.0.0/32

```

**spine1:**

```
nv overlay evpn
feature ospf
feature bgp
feature isis
feature vn-segment-vlan-based
feature bfd
feature nv overlay

vlan 1

ip prefix-list REDISTRIBUTE_CONNECTED seq 10 permit 10.0.0.0/24 le 32
route-map REDISTRIBUTE_CONNECTED permit 10
  match ip address prefix-list REDISTRIBUTE_CONNECTED
vrf context management
  ip route 0.0.0.0/0 mgmt0 192.168.254.1

interface Ethernet1/1
  no switchport
  mtu 9216
  medium p2p
  ip address 10.2.1.1/31
  no shutdown

interface Ethernet1/2
  no switchport
  mtu 9216
  medium p2p
  ip address 10.2.1.3/31
  no shutdown

interface Ethernet1/3
  no switchport
  mtu 9216
  medium p2p
  ip address 10.2.1.5/31
  no shutdown

interface mgmt0
  vrf member management
  ip address 192.168.254.50/24

interface loopback0
  ip address 10.0.0.0/32
icam monitor scale

cli alias name wr copy run start
line console
line vty
router bgp 65000
  router-id 10.0.0.0
  reconnect-interval 12
  address-family ipv4 unicast
    redistribute direct route-map REDISTRIBUTE_CONNECTED
    maximum-paths ibgp 64
  address-family l2vpn evpn
    maximum-paths ibgp 64
    retain route-target all
  template peer LEAF_OVERLAY
    remote-as 65000
    update-source loopback0
    address-family l2vpn evpn
      send-community
      send-community extended
      route-reflector-client
  neighbor 10.0.0.2
    inherit peer LEAF_OVERLAY
  neighbor 10.0.0.3
    inherit peer LEAF_OVERLAY
  neighbor 10.2.0.0/22
    remote-as 65000
    password 3 9125d59c18a9b015
    timers 3 9
    maximum-peers 10
    address-family ipv4 unicast
      route-reflector-client
      next-hop-self all
```

```
```



_**leaf1**:_

```
nv overlay evpn
feature ospf
feature bgp
feature isis
feature interface-vlan
feature vn-segment-vlan-based
feature lacp
feature vpc
feature lldp
feature bfd
feature nv overlay

fabric forwarding anycast-gateway-mac 0000.1111.2222
vlan 1,21,999
vlan 21
  vn-segment 20001
vlan 999
  vn-segment 99900

ip prefix-list REDISTRIBUTE_CONNECTED seq 10 permit 10.0.0.0/24 le 32
ip prefix-list REDISTRIBUTE_CONNECTED seq 20 permit 10.1.0.0/24 le 32
route-map REDISTRIBUTE_CONNECTED permit 10
  match ip address prefix-list REDISTRIBUTE_CONNECTED
vrf context KEEPALIVE
vrf context PROD
  vni 99900
  rd auto
  address-family ipv4 unicast
    route-target both auto
    route-target both auto evpn
vrf context management
  ip route 0.0.0.0/0 mgmt0 192.168.254.1
vpc domain 10
  peer-switch
  role priority 20
  peer-keepalive destination 192.168.0.2 source 192.168.0.1 vrf KEEPALIVE
  delay restore 10
  peer-gateway
  ip arp synchronize


interface Vlan1
  no ip redirects
  no ipv6 redirects

interface Vlan21
  no shutdown
  vrf member PROD
  no ip redirects
  ip address 10.11.1.254/24
  no ipv6 redirects
  fabric forwarding mode anycast-gateway

interface Vlan999
  description Inter VXLAN Routing
  no shutdown
  vrf member PROD
  no ip redirects
  ip forward
  no ipv6 redirects

interface port-channel100
  description CE
  switchport mode trunk
  vpc 100

interface port-channel200
  description Peer-Link Aggregation
  switchport mode trunk
  spanning-tree port type network
  vpc peer-link

interface nve1
  no shutdown
  host-reachability protocol bgp
  source-interface loopback1
  member vni 20001
    ingress-replication protocol bgp
  member vni 99900 associate-vrf

interface Ethernet1/1
  no switchport
  mtu 9216
  medium p2p
  ip address 10.2.1.0/31
  no shutdown

interface Ethernet1/2
  no switchport
  mtu 9216
  medium p2p
  ip address 10.2.2.0/31
  no shutdown

interface Ethernet1/3
  description CE
  switchport mode trunk
  channel-group 100 mode active

interface Ethernet1/4
  description Peer-Link
  switchport mode trunk
  channel-group 200 mode active

interface Ethernet1/5
  description Peer-Link
  switchport mode trunk
  channel-group 200 mode active

interface Ethernet1/6
  description Peer-Keepalive Port
  no switchport
  vrf member KEEPALIVE
  ip address 192.168.0.1/30
  no shutdown

interface mgmt0
  vrf member management
  ip address 192.168.254.52/24

interface loopback0
  ip address 10.0.0.2/32

interface loopback1
  ip address 10.1.0.2/32
  ip address 10.1.0.100/32 secondary
icam monitor scale

cli alias name wr copy run start
line console
line vty
router bgp 65000
  router-id 10.0.0.2
  bestpath as-path multipath-relax
  reconnect-interval 12
  address-family ipv4 unicast
    redistribute direct route-map REDISTRIBUTE_CONNECTED
    maximum-paths ibgp 64
  address-family l2vpn evpn
    maximum-paths ibgp 64
    retain route-target all
  template peer SPINE
    remote-as 65000
    password 3 9125d59c18a9b015
    timers 3 9
    address-family ipv4 unicast
  template peer SPINE_OVERLAY
    remote-as 65000
    update-source loopback0
    address-family l2vpn evpn
      send-community
      send-community extended
  neighbor 10.0.0.0
    inherit peer SPINE_OVERLAY
  neighbor 10.0.0.1
    inherit peer SPINE_OVERLAY
  neighbor 10.2.1.1
    inherit peer SPINE
  neighbor 10.2.2.1
    inherit peer SPINE
  vrf PROD
    address-family ipv4 unicast
evpn
  vni 20001 l2
    rd auto
    route-target import auto
    route-target export auto
```

_**leaf2**:_

```
nv overlay evpn
feature ospf
feature bgp
feature isis
feature interface-vlan
feature vn-segment-vlan-based
feature lacp
feature vpc
feature lldp
feature bfd
feature nv overlay

fabric forwarding anycast-gateway-mac 0000.1111.2222
vlan 1,21-22,999
vlan 21
  vn-segment 20001
vlan 22
  vn-segment 20002
vlan 999
  vn-segment 99900

ip prefix-list REDISTRIBUTE_CONNECTED seq 10 permit 10.0.0.0/24 le 32
ip prefix-list REDISTRIBUTE_CONNECTED seq 20 permit 10.1.0.0/24 le 32
route-map REDISTRIBUTE_CONNECTED permit 10
  match ip address prefix-list REDISTRIBUTE_CONNECTED
vrf context KEEPALIVE
vrf context PROD
  vni 99900
  rd auto
  address-family ipv4 unicast
    route-target both auto
    route-target both auto evpn
vrf context management
  ip route 0.0.0.0/0 mgmt0 192.168.254.1
vpc domain 10
  peer-switch
  role priority 30
  peer-keepalive destination 192.168.0.1 source 192.168.0.2 vrf KEEPALIVE
  delay restore 10
  peer-gateway
  ip arp synchronize


interface Vlan1
  no ip redirects
  no ipv6 redirects

interface Vlan21
  no shutdown
  vrf member PROD
  no ip redirects
  ip address 10.11.1.254/24
  no ipv6 redirects
  fabric forwarding mode anycast-gateway

interface Vlan22
  no shutdown
  vrf member PROD
  no ip redirects
  ip address 10.11.2.254/24
  no ipv6 redirects
  fabric forwarding mode anycast-gateway

interface Vlan999
  description Inter VXLAN Routing
  no shutdown
  vrf member PROD
  no ip redirects
  ip forward
  no ipv6 redirects

interface port-channel100
  description CE
  switchport mode trunk
  vpc 100

interface port-channel200
  description Peer-Link Aggregation
  switchport mode trunk
  spanning-tree port type network
  vpc peer-link

interface nve1
  no shutdown
  host-reachability protocol bgp
  source-interface loopback1
  member vni 20001
    ingress-replication protocol bgp
  member vni 20002
    ingress-replication protocol bgp
  member vni 99900 associate-vrf

interface Ethernet1/1
  no switchport
  mtu 9216
  medium p2p
  ip address 10.2.1.2/31
  no shutdown

interface Ethernet1/2
  no switchport
  mtu 9216
  medium p2p
  ip address 10.2.2.2/31
  no shutdown

interface Ethernet1/3
  switchport access vlan 22

interface Ethernet1/4
  description Peer-Link
  switchport mode trunk
  channel-group 200 mode active

interface Ethernet1/5
  description Peer-Link
  switchport mode trunk
  channel-group 200 mode active

interface Ethernet1/6
  description Peer-Keepalive Port
  no switchport
  vrf member KEEPALIVE
  ip address 192.168.0.2/30
  no shutdown

interface Ethernet1/7
  description CE
  switchport mode trunk
  channel-group 100 mode active

interface mgmt0
  vrf member management
  ip address 192.168.254.53/24

interface loopback0
  ip address 10.0.0.3/32

interface loopback1
  ip address 10.1.0.3/32
  ip address 10.1.0.100/32 secondary
icam monitor scale

cli alias name wr copy run start
line console
line vty
router bgp 65000
  router-id 10.0.0.3
  bestpath as-path multipath-relax
  reconnect-interval 12
  address-family ipv4 unicast
    redistribute direct route-map REDISTRIBUTE_CONNECTED
    maximum-paths ibgp 64
  address-family l2vpn evpn
    maximum-paths ibgp 64
    retain route-target all
  template peer SPINE
    remote-as 65000
    password 3 9125d59c18a9b015
    timers 3 9
    address-family ipv4 unicast
  template peer SPINE_OVERLAY
    remote-as 65000
    update-source loopback0
    address-family l2vpn evpn
      send-community
      send-community extended
  neighbor 10.0.0.0
    inherit peer SPINE_OVERLAY
  neighbor 10.0.0.1
    inherit peer SPINE_OVERLAY
  neighbor 10.2.1.3
    inherit peer SPINE
  neighbor 10.2.2.3
    inherit peer SPINE
  vrf PROD
    address-family ipv4 unicast
evpn
  vni 20001 l2
    rd auto
    route-target import auto
    route-target export auto
  vni 20002 l2
    rd auto
    route-target import auto
    route-target export auto
```

_**CE:**_

```
feature interface-vlan
feature lacp

ip route 0.0.0.0/0 10.11.1.254
vlan 1,21
vlan 21
  name CLIENT-1

vrf context management

interface Vlan1

interface Vlan21
  no shutdown
  ip address 10.11.1.102/24

interface port-channel100
  description To LEAFS
  switchport mode trunk

interface Ethernet1/1
  switchport mode trunk
  channel-group 100 mode active

interface Ethernet1/2
  switchport mode trunk
  channel-group 100 mode active

interface mgmt0
  vrf member management
icam monitor scale

cli alias name wr copy run start
line console
line vty

```



***Проверка установки соседства BGP между spine и leaf коммутаторами:***

```
leaf1(config)# show ip bgp
BGP routing table information for VRF default, address family IPv4 Unicast
BGP table version is 30, Local Router ID is 10.0.0.2
Status: s-suppressed, x-deleted, S-stale, d-dampened, h-history, *-valid, >-best
Path type: i-internal, e-external, c-confed, l-local, a-aggregate, r-redist, I-i
njected
Origin codes: i - IGP, e - EGP, ? - incomplete, | - multipath, & - backup, 2 - b
est2

   Network            Next Hop            Metric     LocPrf     Weight Path
*>i10.0.0.0/32        10.2.1.1                 0        100          0 ?
*>r10.0.0.2/32        0.0.0.0                  0        100      32768 ?
*>i10.0.0.3/32        10.2.1.1                 0        100          0 ?
*>r10.1.0.2/32        0.0.0.0                  0        100      32768 ?
*>i10.1.0.3/32        10.2.1.1                 0        100          0 ?
*>r10.1.0.100/32      0.0.0.0                  0        100      32768 ?

leaf1(config)# sh bgp l2vpn evpn
BGP routing table information for VRF default, address family L2VPN EVPN
BGP table version is 63, Local Router ID is 10.0.0.2
Status: s-suppressed, x-deleted, S-stale, d-dampened, h-history, *-valid, >-best
Path type: i-internal, e-external, c-confed, l-local, a-aggregate, r-redist, I-i
njected
Origin codes: i - IGP, e - EGP, ? - incomplete, | - multipath, & - backup, 2 - b
est2

   Network            Next Hop            Metric     LocPrf     Weight Path
Route Distinguisher: 10.0.0.2:32788    (L2VNI 20001)
*>l[2]:[0]:[0]:[48]:[5000.3100.1b08]:[0]:[0.0.0.0]/216
                      10.1.0.100                        100      32768 i
*>l[2]:[0]:[0]:[48]:[5000.3100.1b08]:[32]:[10.11.1.102]/272
                      10.1.0.100                        100      32768 i
*>l[3]:[0]:[32]:[10.1.0.100]/88
                      10.1.0.100                        100      32768 i
                      
leaf2(config)# sh bgp l2vpn evpn
BGP routing table information for VRF default, address family L2VPN EVPN
BGP table version is 63, Local Router ID is 10.0.0.3
Status: s-suppressed, x-deleted, S-stale, d-dampened, h-history, *-valid, >-best
Path type: i-internal, e-external, c-confed, l-local, a-aggregate, r-redist, I-i
njected
Origin codes: i - IGP, e - EGP, ? - incomplete, | - multipath, & - backup, 2 - b
est2

   Network            Next Hop            Metric     LocPrf     Weight Path
Route Distinguisher: 10.0.0.3:32788    (L2VNI 20001)
*>l[2]:[0]:[0]:[48]:[5000.3100.1b08]:[0]:[0.0.0.0]/216
                      10.1.0.100                        100      32768 i
*>l[2]:[0]:[0]:[48]:[5000.3100.1b08]:[32]:[10.11.1.102]/272
                      10.1.0.100                        100      32768 i
*>l[3]:[0]:[32]:[10.1.0.100]/88
                      10.1.0.100                        100      32768 i

Route Distinguisher: 10.0.0.3:32789    (L2VNI 20002)
*>l[2]:[0]:[0]:[48]:[0050.7966.6807]:[0]:[0.0.0.0]/216
                      10.1.0.100                        100      32768 i
*>l[2]:[0]:[0]:[48]:[0050.7966.6807]:[32]:[10.11.2.102]/272
                      10.1.0.100                        100      32768 i
*>l[3]:[0]:[32]:[10.1.0.100]/88
                      10.1.0.100                        100      32768 i



```

_***Проверка VPC на leaf1 и leaf2:***_

```
leaf1# sh vpc
Legend:
		(*) - local vPC is down, forwarding via vPC peer-link

vPC domain id                     : 10
Peer status                       : peer adjacency formed ok
vPC keep-alive status             : peer is alive
Configuration consistency status  : success
Per-vlan consistency status       : failed
Type-2 consistency status         : success
vPC role                          : primary
Number of vPCs configured         : 1
Peer Gateway                      : Enabled
Dual-active excluded VLANs        : -
Graceful Consistency Check        : Enabled
Auto-recovery status              : Disabled
Delay-restore status              : Timer is off.(timeout = 10s)
Delay-restore SVI status          : Timer is off.(timeout = 10s)
Operational Layer3 Peer-router    : Disabled
Virtual-peerlink mode             : Disabled

vPC Peer-link status
---------------------------------------------------------------------
id    Port   Status Active vlans
--    ----   ------ -------------------------------------------------
1     Po200  up     1,21,999


vPC status
----------------------------------------------------------------------------
Id    Port          Status Consistency Reason                Active vlans
--    ------------  ------ ----------- ------                ---------------
100   Po100         up     success     success               1,21,999

leaf2(config)# sh vpc
Legend:
                (*) - local vPC is down, forwarding via vPC peer-link

vPC domain id                     : 10
Peer status                       : peer adjacency formed ok
vPC keep-alive status             : peer is alive
Configuration consistency status  : success
Per-vlan consistency status       : failed
Type-2 consistency status         : success
vPC role                          : secondary
Number of vPCs configured         : 1
Peer Gateway                      : Enabled
Dual-active excluded VLANs        : -
Graceful Consistency Check        : Enabled
Auto-recovery status              : Disabled
Delay-restore status              : Timer is off.(timeout = 10s)
Delay-restore SVI status          : Timer is off.(timeout = 10s)
Operational Layer3 Peer-router    : Disabled
Virtual-peerlink mode             : Disabled

vPC Peer-link status
---------------------------------------------------------------------
id    Port   Status Active vlans
--    ----   ------ -------------------------------------------------
1     Po200  up     1,21,999


vPC status
----------------------------------------------------------------------------
Id    Port          Status Consistency Reason                Active vlans
--    ------------  ------ ----------- ------                ---------------
100   Po100         up     success     success               1,21,999
```



***Проверка клиентских подключений между CE и клиентов за leaf2 в другом vni (20002)***

```
VPC7> show ip

NAME        : VPC7[1]
IP/MASK     : 10.11.2.102/24
GATEWAY     : 10.11.2.254
DNS         :
MAC         : 00:50:79:66:68:07
LPORT       : 20000
RHOST:PORT  : 127.0.0.1:30000
MTU         : 1500

VPC7> ping 10.11.1.102 -c 1000

84 bytes from 10.11.1.102 icmp_seq=1 ttl=254 time=5.262 ms
84 bytes from 10.11.1.102 icmp_seq=2 ttl=254 time=4.193 ms
84 bytes from 10.11.1.102 icmp_seq=3 ttl=254 time=4.324 ms

CE(config)# show ip int br

IP Interface Status for VRF "default"(1)
Interface            IP Address      Interface Status
Vlan21               10.11.1.102     protocol-up/link-up/admin-up

CE(config)# sh port-channel s
scale-fanout   summary
CE(config)# sh port-channel summary
Flags:  D - Down        P - Up in port-channel (members)
        I - Individual  H - Hot-standby (LACP only)
        s - Suspended   r - Module-removed
        b - BFD Session Wait
        S - Switched    R - Routed
        U - Up (port-channel)
        p - Up in delay-lacp mode (member)
        M - Not in use. Min-links not met
--------------------------------------------------------------------------------
Group Port-       Type     Protocol  Member Ports
      Channel
--------------------------------------------------------------------------------
100   Po100(SU)   Eth      LACP      Eth1/1(P)    Eth1/2(P)

CE(config)# ping 10.11.2.102 source-interface vlan 21
PING 10.11.2.102 (10.11.2.102): 56 data bytes
64 bytes from 10.11.2.102: icmp_seq=0 ttl=62 time=9.864 ms
64 bytes from 10.11.2.102: icmp_seq=1 ttl=62 time=3.415 ms
64 bytes from 10.11.2.102: icmp_seq=2 ttl=62 time=4.645 ms
64 bytes from 10.11.2.102: icmp_seq=3 ttl=62 time=3.298 ms
64 bytes from 10.11.2.102: icmp_seq=4 ttl=62 time=3.344 ms
```





