# ДЗ №6

### Цели:

- Настроить маршрутизацию в рамках Overlay между клиентами

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
|  Service_3  |  23  | 10023 | 10.11.3.0/24 |
|  Service_4  |  24  | 10024 | 10.11.4.0/24 |

**Топология EVE nexus & arista :**

<img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab5/bgp_evpn_l2.png" style="zoom:200%;" />

### Примененные конфигурации EOS для настройки ebgp c Vlan Based Service и L3 Symmetric:

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

**spine1/2 (_конфигурации полностью идентичны_):**

```
service routing protocols model multi-agent 

ip prefix-list REDISTRIBUTE_CONNECTED seq 10 permit 10.8.0.0/24 le 32

route-map REDISTRIBUTE_CONNECTED permit 10
   match ip address prefix-list REDISTRIBUTE_CONNECTED
   
peer-filter AS_FILTER
   10 match as-range 65001-65999 result accept

router bgp 65000
   router-id 10.8.0.0
   timers bgp 1 3
   maximum-paths 128
   bgp listen range 10.8.0.0/24 peer-group LEAF_OVERLAY peer-filter 65001-65999
   bgp listen range 10.10.0.0/22 peer-group LEAF_UNDERLAY peer-filter 65001-65999
   neighbor LEAF_OVERLAY peer group
   neighbor LEAF_OVERLAY update-source Loopback0
   neighbor LEAF_OVERLAY ebgp-multihop 2
   neighbor LEAF_OVERLAY send-community
   neighbor LEAF_UNDERLAY peer group
   neighbor LEAF_UNDERLAY bfd
   neighbor LEAF_UNDERLAY password 7 F0ycgLa3E/blyskQ/za9aQ==
   redistribute connected route-map REDISTRIBUTE_CONNECTED
   !
   address-family evpn
      neighbor LEAF_OVERLAY activate
```

_**leaf1**:_

```
service routing protocols model multi-agent

ip prefix-list REDISTRIBUTE_CONNECTED seq 10 permit 10.8.0.0/24 le 32
ip prefix-list REDISTRIBUTE_CONNECTED seq 20 permit 10.9.0.0/24 le 32

vrf instance SERVICE
ip routing
ip routing vrf SERVICE
no ip routing vrf management

ip virtual-router mac-address 00:00:22:22:33:33

route-map REDISTRIBUTE_CONNECTED permit 10
   match ip address prefix-list REDISTRIBUTE_CONNECTED

router bgp 65001
   router-id 10.8.0.2
   timers bgp 1 3
   maximum-paths 128
   neighbor SPINE_OVERLAY peer group
   neighbor SPINE_OVERLAY remote-as 65000
   neighbor SPINE_OVERLAY update-source Loopback0
   neighbor SPINE_OVERLAY ebgp-multihop 2
   neighbor SPINE_OVERLAY password 7 tZv5KErEqd/gwQMx+naEBw==
   neighbor SPINE_OVERLAY send-community
   neighbor SPINE_UNDERLAY peer group
   neighbor SPINE_UNDERLAY remote-as 65000
   neighbor SPINE_UNDERLAY bfd
   neighbor SPINE_UNDERLAY password 7 fCn3158XaWdTuDgXDrM89g==
   neighbor 10.8.0.0 peer group SPINE_OVERLAY
   neighbor 10.8.0.1 peer group SPINE_OVERLAY
   neighbor 10.10.1.1 peer group SPINE_UNDERLAY
   neighbor 10.10.2.1 peer group SPINE_UNDERLAY
   redistribute connected route-map REDISTRIBUTE_CONNECTED
   !
   vlan 21
      rd 10.8.0.2:10021
      route-target both 1:10021
      redistribute learned
   !
   vlan 22
      rd 10.8.0.2:10022
      route-target both 1:10022
      redistribute learned
   !
   address-family evpn
      neighbor SPINE_OVERLAY activate
   !
   vrf SERVICE
      rd 10.8.0.2:65000
      route-target import evpn 1:65000
      route-target export evpn 1:65000

interface Vxlan1
   vxlan source-interface Loopback1
   vxlan udp-port 4789
   vxlan vlan 20-30 vni 10020-10030
   vxlan vrf SERVICE vni 65000

interface Vlan21
   vrf SERVICE
   ip address virtual 10.11.1.254/24
!
interface Vlan22
   vrf SERVICE
   ip address virtual 10.11.2.254/24
```

_**leaf2:**_

```
service routing protocols model multi-agent

ip prefix-list REDISTRIBUTE_CONNECTED seq 10 permit 10.8.0.0/24 le 32
ip prefix-list REDISTRIBUTE_CONNECTED seq 20 permit 10.9.0.0/24 le 32

vrf instance SERVICE
ip routing
ip routing vrf SERVICE
no ip routing vrf management

ip virtual-router mac-address 00:00:22:22:33:33

route-map REDISTRIBUTE_CONNECTED permit 10
   match ip address prefix-list REDISTRIBUTE_CONNECTED

router bgp 65002
   router-id 10.8.0.3
   timers bgp 1 3
   maximum-paths 128
   neighbor SPINE_OVERLAY peer group
   neighbor SPINE_OVERLAY remote-as 65000
   neighbor SPINE_OVERLAY update-source Loopback0
   neighbor SPINE_OVERLAY ebgp-multihop 2
   neighbor SPINE_OVERLAY password 7 tZv5KErEqd/gwQMx+naEBw==
   neighbor SPINE_OVERLAY send-community
   neighbor SPINE_UNDERLAY peer group
   neighbor SPINE_UNDERLAY remote-as 65000
   neighbor SPINE_UNDERLAY bfd
   neighbor SPINE_UNDERLAY password 7 fCn3158XaWdTuDgXDrM89g==
   neighbor 10.8.0.0 peer group SPINE_OVERLAY
   neighbor 10.8.0.1 peer group SPINE_OVERLAY
   neighbor 10.10.1.3 peer group SPINE_UNDERLAY
   neighbor 10.10.2.3 peer group SPINE_UNDERLAY
   redistribute connected route-map REDISTRIBUTE_CONNECTED
   !
   vlan 21
      rd 10.8.0.3:10021
      route-target both 1:10021
      redistribute learned
   !
   vlan 22
      rd 10.8.0.3:10022
      route-target both 1:10022
      redistribute learned
   !
   vlan 23
      rd 10.8.0.3:10023
      route-target both 1:10023
      redistribute learned
   !
   address-family evpn
      neighbor SPINE_OVERLAY activate
   !
   vrf SERVICE
      rd 10.8.0.3:65000
      route-target import evpn 1:65000
      route-target export evpn 1:65000

interface Vxlan1
   vxlan source-interface Loopback1
   vxlan udp-port 4789
   vxlan vlan 20-30 vni 10020-10030
   vxlan vrf SERVICE vni 65000

interface Vlan21
   vrf SERVICE
   ip address virtual 10.11.1.254/24
!
interface Vlan22
   vrf SERVICE
   ip address virtual 10.11.2.254/24
```

_**leaf3:**_

```
service routing protocols model multi-agent

ip prefix-list REDISTRIBUTE_CONNECTED seq 10 permit 10.8.0.0/24 le 32
ip prefix-list REDISTRIBUTE_CONNECTED seq 20 permit 10.9.0.0/24 le 32

vrf instance SERVICE
ip routing
ip routing vrf SERVICE
no ip routing vrf management

ip virtual-router mac-address 00:00:22:22:33:33

route-map REDISTRIBUTE_CONNECTED permit 10
   match ip address prefix-list REDISTRIBUTE_CONNECTED

router bgp 65003
   router-id 10.8.0.4
   timers bgp 1 3
   maximum-paths 128
   neighbor SPINE_OVERLAY peer group
   neighbor SPINE_OVERLAY remote-as 65000
   neighbor SPINE_OVERLAY update-source Loopback0
   neighbor SPINE_OVERLAY ebgp-multihop 2
   neighbor SPINE_OVERLAY password 7 tZv5KErEqd/gwQMx+naEBw==
   neighbor SPINE_OVERLAY send-community
   neighbor SPINE_UNDERLAY peer group
   neighbor SPINE_UNDERLAY remote-as 65000
   neighbor SPINE_UNDERLAY bfd
   neighbor SPINE_UNDERLAY password 7 fCn3158XaWdTuDgXDrM89g==
   neighbor 10.8.0.0 peer group SPINE_OVERLAY
   neighbor 10.8.0.1 peer group SPINE_OVERLAY
   neighbor 10.10.1.5 peer group SPINE_UNDERLAY
   neighbor 10.10.2.5 peer group SPINE_UNDERLAY
   redistribute connected route-map REDISTRIBUTE_CONNECTED
   !
   vlan 21
      rd 10.8.0.4:10021
      route-target both 1:10021
      redistribute learned
   !
   vlan 22
      rd 10.8.0.4:10022
      route-target both 1:10022
      redistribute learned
   !
   vlan 23
      rd 10.8.0.4:10023
      route-target both 1:10023
      redistribute learned
   !
   address-family evpn
      neighbor SPINE_OVERLAY activate
   !
   vrf SERVICE
      rd 10.8.0.4:65000
      route-target import evpn 1:65000
      route-target export evpn 1:65000

interface Vxlan1
   vxlan source-interface Loopback1
   vxlan udp-port 4789
   vxlan vlan 20-30 vni 10020-10030
   vxlan vrf SERVICE vni 65000

interface Vlan21
   vrf SERVICE
   ip address virtual 10.11.1.254/24
!
interface Vlan22
   vrf SERVICE
   ip address virtual 10.11.2.254/24
```



***Проверка установки соседства BGP Underlay между spine и leaf коммутаторами:***

```
spine1#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.0, local AS number 65000
Neighbor Status Codes: m - Under maintenance
  Neighbor  V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.8.0.2  4 65001            633       635    0    0 00:08:46 Estab   2      2
  10.8.0.3  4 65002            636       626    0    0 00:08:42 Estab   2      2
  10.8.0.4  4 65003            633       630    0    0 00:08:46 Estab   2      2
  10.10.1.0 4 65001            626       624    0    0 00:08:47 Estab   2      2
  10.10.1.2 4 65002            623       622    0    0 00:08:47 Estab   2      2
  10.10.1.4 4 65003            623       623    0    0 00:08:47 Estab   2      2

spine2(config)#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.1, local AS number 65000
Neighbor Status Codes: m - Under maintenance
  Neighbor  V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.8.0.2  4 65001            647       649    0    0 00:08:58 Estab   2      2
  10.8.0.3  4 65002            647       645    0    0 00:09:00 Estab   2      2
  10.8.0.4  4 65003            650       645    0    0 00:08:57 Estab   2      2
  10.10.2.0 4 65001            639       637    0    0 00:09:00 Estab   2      2
  10.10.2.2 4 65002            639       639    0    0 00:09:00 Estab   2      2
  10.10.2.4 4 65003            640       641    0    0 00:08:59 Estab   2      2

leaf1#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.2, local AS number 65001
Neighbor Status Codes: m - Under maintenance
  Neighbor  V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.8.0.0  4 65000            688       685    0    0 00:09:31 Estab   5      5
  10.8.0.1  4 65000            687       684    0    0 00:09:30 Estab   5      5
  10.10.1.1 4 65000            676       678    0    0 00:09:32 Estab   5      5
  10.10.2.1 4 65000            675       675    0    0 00:09:32 Estab   5      5
  
leaf2#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.3, local AS number 65002
Neighbor Status Codes: m - Under maintenance
  Neighbor  V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.8.0.0  4 65000            697       709    0    0 00:09:42 Estab   5      5
  10.8.0.1  4 65000            704       705    0    0 00:09:48 Estab   5      5
  10.10.1.3 4 65000            693       693    0    0 00:09:48 Estab   5      5
  10.10.2.3 4 65000            694       695    0    0 00:09:48 Estab   5      5
  
leaf3#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.4, local AS number 65003
Neighbor Status Codes: m - Under maintenance
  Neighbor  V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.8.0.0  4 65000            718       719    0    0 00:10:00 Estab   5      5
  10.8.0.1  4 65000            717       722    0    0 00:09:59 Estab   5      5
  10.10.1.5 4 65000            710       709    0    0 00:10:01 Estab   5      5
  10.10.2.5 4 65000            711       711    0    0 00:10:01 Estab   5      5

```



_***Проверка установки соседства BGP EVPN Overlay между spine и leaf коммутаторами:***_

```
spine1#show bgp evpn summary
BGP summary information for VRF default
Router identifier 10.8.0.0, local AS number 65000
Neighbor Status Codes: m - Under maintenance
  Neighbor V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.8.0.2 4 65001            751       755    0    0 00:10:29 Estab   4      4
  10.8.0.3 4 65002            758       746    0    0 00:10:25 Estab   5      5
  10.8.0.4 4 65003            753       750    0    0 00:10:28 Estab   5      5
  
spine2#show bgp evpn summary
BGP summary information for VRF default
Router identifier 10.8.0.1, local AS number 65000
Neighbor Status Codes: m - Under maintenance
  Neighbor V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.8.0.2 4 65001          72629     72627    0    0 17:11:59 Estab   1      1
  10.8.0.3 4 65002          72517     72518    0    0 17:10:08 Estab   2      2
  10.8.0.4 4 65003          72537     72599    0    0 17:10:07 Estab   2      2
  
leaf1(config)#show bgp evpn summary
BGP summary information for VRF default
Router identifier 10.8.0.2, local AS number 65001
Neighbor Status Codes: m - Under maintenance
  Neighbor V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.8.0.0 4 65000          89849     89897    0    0 17:13:14 Estab   4      4
  10.8.0.1 4 65000          84661     84680    0    0 17:12:16 Estab   4      4

leaf2#show bgp evpn summary
BGP summary information for VRF default
Router identifier 10.8.0.3, local AS number 65002
Neighbor Status Codes: m - Under maintenance
  Neighbor V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.8.0.0 4 65000          89371     89366    0    0 17:11:24 Estab   3      3
  10.8.0.1 4 65000          84614     84624    0    0 17:10:41 Estab   3      3

leaf3#show bgp evpn summary
BGP summary information for VRF default
Router identifier 10.8.0.4, local AS number 65003
Neighbor Status Codes: m - Under maintenance
  Neighbor V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.8.0.0 4 65000          89058     89083    0    0 17:13:45 Estab   3      3
  10.8.0.1 4 65000          84312     84302    0    0 17:10:55 Estab   3      3
```



***Проверка доступности между Service_1_leaf1 c ip 10.11.1.100 и Service_3_leaf3 с ip 10.11.3.1010***

```
Service_1_l1> ping 10.11.1.101
84 bytes from 10.11.1.101 icmp_seq=1 ttl=64 time=38.103 ms
84 bytes from 10.11.1.101 icmp_seq=2 ttl=64 time=18.610 ms
84 bytes from 10.11.1.101 icmp_seq=3 ttl=64 time=28.706 ms

Service_3_l3> ping 10.11.3.100
84 bytes from 10.11.3.100 icmp_seq=1 ttl=64 time=38.630 ms
84 bytes from 10.11.3.100 icmp_seq=2 ttl=64 time=16.611 ms
84 bytes from 10.11.3.100 icmp_seq=3 ttl=64 time=28.116 ms
```

```
leaf1#show vxlan vtep detail
Remote VTEPS for Vxlan1:

VTEP           Learned Via         MAC Address Learning       Tunnel Type(s)
-------------- ------------------- -------------------------- --------------
10.9.0.3       control plane       control plane              unicast, flood
10.9.0.4       control plane       control plane              unicast, flood

Total number of remote VTEPS:  2
leaf1#
leaf1#
leaf1#show vxlan vtep detail
Remote VTEPS for Vxlan1:

VTEP           Learned Via         MAC Address Learning       Tunnel Type(s)
-------------- ------------------- -------------------------- --------------
10.9.0.3       control plane       control plane              unicast, flood
10.9.0.4       control plane       control plane              unicast, flood

Total number of remote VTEPS:  2
```

```
leaf1#show bgp evpn route-type mac-ip
BGP routing table information for VRF default
Router identifier 10.8.0.2, local AS number 65001
Route status codes: * - valid, > - active, S - Stale, E - ECMP head, e - ECMP
                    c - Contributing to ECMP, % - Pending BGP convergence
Origin codes: i - IGP, e - EGP, ? - incomplete
AS Path Attributes: Or-ID - Originator ID, C-LST - Cluster List, LL Nexthop - Link Local Nexthop

          Network                Next Hop              Metric  LocPref Weight  Path
 * >      RD: 10.8.0.2:10021 mac-ip 0050.7966.683d
                                 -                     -       -       0       i
 * >      RD: 10.8.0.2:10021 mac-ip 0050.7966.683d 10.11.1.100
                                 -                     -       -       0       i
 * >Ec    RD: 10.8.0.4:10023 mac-ip 0050.7966.683f
                                 10.9.0.4              -       100     0       65000 65003 i
 *  ec    RD: 10.8.0.4:10023 mac-ip 0050.7966.683f
                                 10.9.0.4              -       100     0       65000 65003 i
 * >Ec    RD: 10.8.0.4:10023 mac-ip 0050.7966.683f 10.11.3.100
                                 10.9.0.4              -       100     0       65000 65003 i
 *  ec    RD: 10.8.0.4:10023 mac-ip 0050.7966.683f 10.11.3.100
                                 10.9.0.4              -       100     0       65000 65003 i
 * >Ec    RD: 10.8.0.3:10023 mac-ip 0050.7966.6843
                                 10.9.0.3              -       100     0       65000 65002 i
 *  ec    RD: 10.8.0.3:10023 mac-ip 0050.7966.6843
                                 10.9.0.3              -       100     0       65000 65002 i
 * >Ec    RD: 10.8.0.3:10023 mac-ip 0050.7966.6843 10.11.3.101
                                 10.9.0.3              -       100     0       65000 65002 i
 *  ec    RD: 10.8.0.3:10023 mac-ip 0050.7966.6843 10.11.3.101
                                 10.9.0.3              -       100     0       65000 65002 i
```

_**Видим, что маршруты до 10.11.3.100 на leaf 3 в vlan 23 доступен через Spine1 и Spine 2. Также видим связку vni 10023 и L3VNI 65000 для маршрутизации. Также для проверки симметричной модели убрал vlan23 с leaf1.**_

```
leaf1#show bgp evpn route-type mac-ip 10.11.3.100 detail
BGP routing table information for VRF default
Router identifier 10.8.0.2, local AS number 65001
BGP routing table entry for mac-ip 0050.7966.683f 10.11.3.100, Route Distinguisher: 10.8.0.4:10023
 Paths: 2 available
  65000 65003
    10.9.0.4 from 10.8.0.0 (10.8.0.0)
      Origin IGP, metric -, localpref 100, weight 0, tag 0, valid, external, ECMP head, ECMP, best, ECMP contributor
      Extended Community: Route-Target-AS:1:10023 Route-Target-AS:1:65000 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:50:5f:8e:f8:90:42
      VNI: 10023 L3 VNI: 65000 ESI: 0000:0000:0000:0000:0000
  65000 65003
    10.9.0.4 from 10.8.0.1 (10.8.0.1)
      Origin IGP, metric -, localpref 100, weight 0, tag 0, valid, external, ECMP, ECMP contributor
      Extended Community: Route-Target-AS:1:10023 Route-Target-AS:1:65000 TunnelEncap:tunnelTypeVxlan EvpnRouterMac:50:5f:8e:f8:90:42
      VNI: 10023 L3 VNI: 65000 ESI: 0000:0000:0000:0000:0000
```



_***Немного смотрим wireshark:***_

- Сбросил полностью bgp на leaf1 и включил в wireshark фильтра _**bgp.update.path_attributes**_ чтобы посмотреть все сообщения update. Также после установки сессии underlay ebgp выполнил ping между service_1 на leaf1 и service_3 leaf3.

  -  Помимо "обычных" маршрутов типа 2 и 3 видим маршрут типа 2 в котором видим стек меток (vni) 10023  для коммутации и 65000 для маршрутизации  в нашем vrf. 	Так же видим два RT для импорта в mac-vrf 10023 и наш ip-vrf 65000. 

  - Так же  видим поле с Tranitive EVPN, в котром находится mac адрес сгенерировнный leaf3, который будет переписан как dst при передачи пакета от leaf1 к leaf3. Кстати заметил в выводе leaf3, Transitive EVPN mac генерируется коммутатором в сервисном vlan 4096 и назначет источником vxlan и cpu.

    ```
    leaf3#sh mac address-table
              Mac Address Table
    ------------------------------------------------------------------
    
    Vlan    Mac Address       Type        Ports      Moves   Last Move
    ----    -----------       ----        -----      -----   ---------
    4069    50f3.a8aa.779e    DYNAMIC     Vx1        1       0:33:35 ago
    4069* VLAN4069                         active    Cpu, Vx1
    ```
  
    
  
  <img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab6/summ.png" style="zoom:100%;" />
  
   


​     	

### Примечание:

* Так как все варинаты конфигурации лабы такие как ebgp, ibgp, vlan_aware, vlan base И так далее автоматизированы через шаблоны jinja2, то получилось пораскатывать разные сценарии и посмотреть как работает сеть в различных реализациях.

  <img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab6/j2_1.png" style="zoom:40%;" /> <img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab6/j2_2.png" style="zoom:35%;" />

* Планирую сделать Ansible проект аналогично моему самописному скрипту на python для автоматизации сценариев конфигураций Underlay и Overlay в лабе.

