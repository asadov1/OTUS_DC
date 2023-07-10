# ДЗ №4

### Цели:

- Настроить eBGP для Underlay сети

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



**Топология EVE nexus & arista :**

<img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab4/eve_bgp.png" style="zoom:40%;" />



### Примененные конфигурации nexus для настройки ebgp:

**Пример конфигурации интерфейса spine/leaf  для cisco nexus:**

```
interface Ethernet1/1
  no switchport
  mtu 9216
  medium p2p
  ip address 10.2.1.1/31
  no shutdown
  
interface loopback0
  ip address 10.0.0.0/32
```



**spine1:**

```  feature bgp
feature bgp
  
route-map REDISTRIBUTE_CONNECTED permit 10
  match interface loopback0
route-map R_AS permit 10
  match as-number 65001-65003
  
router bgp 65000
  router-id 10.0.0.0
  bestpath as-path multipath-relax
  reconnect-interval 12
  address-family ipv4 unicast
    redistribute direct route-map REDISTRIBUTE_CONNECTED
  neighbor 10.2.0.0/22 remote-as route-map R_AS
    password 3 9125d59c18a9b015
    timers 3 9
    maximum-peers 10
    address-family ipv4 unicast
```

**spine2:**

```
feature bgp
  
route-map REDISTRIBUTE_CONNECTED permit 10
  match interface loopback0
route-map R_AS permit 10
  match as-number 65001-65003

router bgp 65000
  router-id 10.0.0.1
  bestpath as-path multipath-relax
  reconnect-interval 12
  address-family ipv4 unicast
    redistribute direct route-map REDISTRIBUTE_CONNECTED
  neighbor 10.2.0.0/22 remote-as route-map R_AS
    password 3 9125d59c18a9b015
    timers 3 9
    maximum-peers 10
    address-family ipv4 unicast
```

**leaf1:**

```
feature bgp
  
route-map REDISTRIBUTE_CONNECTED permit 10
  match interface loopback0

router bgp 65001
  router-id 10.0.0.2
  reconnect-interval 12
  address-family ipv4 unicast
    redistribute direct route-map REDISTRIBUTE_CONNECTED
    maximum-paths 64
  template peer SPINE
    remote-as 65000
    password 3 9125d59c18a9b015
    timers 3 9
    address-family ipv4 unicast
  neighbor 10.2.1.1
    inherit peer SPINE
  neighbor 10.2.2.1
    inherit peer SPINE
```

**leaf2:**

```
feature bgp

route-map REDISTRIBUTE_CONNECTED permit 10
  match interface loopback0

router bgp 65002
  router-id 10.0.0.3
  reconnect-interval 12
  address-family ipv4 unicast
    redistribute direct route-map REDISTRIBUTE_CONNECTED
    maximum-paths 64
  template peer SPINE
    remote-as 65000
    password 3 9125d59c18a9b015
    timers 3 9
    address-family ipv4 unicast
  neighbor 10.2.1.3
    inherit peer SPINE
  neighbor 10.2.2.3
    inherit peer SPINE
```

**leaf3:**

```
feature bgp

route-map REDISTRIBUTE_CONNECTED permit 10
  match interface loopback0
  
router bgp 65003
  router-id 10.0.0.4
  reconnect-interval 12
  address-family ipv4 unicast
    redistribute direct route-map REDISTRIBUTE_CONNECTED
    maximum-paths 64
  template peer SPINE
    remote-as 65000
    password 3 9125d59c18a9b015
    timers 3 9
    address-family ipv4 unicast
  neighbor 10.2.1.5
    inherit peer SPINE
  neighbor 10.2.2.5
    inherit peer SPINE
```



***Проверка установки соседства BGP между spine и leaf коммутаторами:***

```
spine1# sh ip bgp summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.2.1.0        4 65001     285     284       12    0    0 00:13:15 1
10.2.1.2        4 65002     282     281       12    0    0 00:12:50 1
10.2.1.4        4 65003     282     281       12    0    0 00:12:28 1

spine2# show ip bgp summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.2.2.0        4 65001     283     282       14    0    0 00:13:34 1
10.2.2.2        4 65002     283     282       14    0    0 00:13:14 1
10.2.2.4        4 65003     281     281       14    0    0 00:12:50 1

leaf1(config)# show ip bgp summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.2.1.1        4 65000     285     282       11    0    0 00:13:54 3
10.2.2.1        4 65000     284     281       11    0    0 00:13:50 3

spine1# sh ip bgp
   Network            Next Hop            Metric     LocPrf     Weight Path
*>e10.0.0.0/32        10.2.1.1                 0                     0 65000 ?
*>e10.0.0.1/32        10.2.2.1                 0                     0 65000 ?
*>r10.0.0.2/32        0.0.0.0                  0        100      32768 ?
*|e10.0.0.3/32        10.2.2.1                                       0 65000 650
02 ?
*>e                   10.2.1.1                                       0 65000 650
02 ?
*|e10.0.0.4/32        10.2.2.1                                       0 65000 650
03 ?
*>e                   10.2.1.1                                       0 65000 650
03 ?

leaf1(config)# show ip route 10.0.0.3
10.0.0.3/32, ubest/mbest: 2/0
    *via 10.2.1.1, [20/0], 00:03:36, bgp-65001, external, tag 65000
    *via 10.2.2.1, [20/0], 00:03:36, bgp-65001, external, tag 65000

```



### Примененные конфигурации EOS для настройки ebgp:

**Пример конфигурации интерфейса spine/leaf  для arista**:

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
peer-filter AS_FILTER
   10 match as-range 65001-65999 result accept

router bgp 65000
   router-id 10.8.0.0
   timers bgp 1 3
   maximum-paths 128
   bgp listen range 10.10.0.0/22 peer-group LEAFS peer-filter 65001-65999
   neighbor LEAFS peer group
   neighbor LEAFS bfd
   neighbor LEAFS password 7 qcZqPZg4u36aJMQlNFmhpQ==
```

**spine2:**

```
peer-filter AS_FILTER
   10 match as-range 65001-65999 result accept
!
router bgp 65000
   router-id 10.8.0.1
   timers bgp 1 3
   maximum-paths 128
   bgp listen range 10.10.0.0/22 peer-group LEAFS peer-filter 65001-65999
   neighbor LEAFS peer group
   neighbor LEAFS bfd
   neighbor LEAFS password 7 qcZqPZg4u36aJMQlNFmhpQ==
```

**leaf1**:

```
route-map REDISTRIBUTE_CONNECTED permit 10
   match interface Loopback0

router bgp 65001
   router-id 10.8.0.2
   timers bgp 1 3
   maximum-paths 128
   neighbor SPINES peer group
   neighbor SPINES remote-as 65000
   neighbor SPINES bfd
   neighbor SPINES password 7 jHZ88O3chwnpmpxrF1e8qQ==
   neighbor 10.10.1.1 peer group SPINES
   neighbor 10.10.2.1 peer group SPINES
   redistribute connected route-map REDISTRIBUTE_CONNECTED
```

**leaf2:**

```
route-map REDISTRIBUTE_CONNECTED permit 10
   match interface Loopback0

router bgp 65002
   router-id 10.8.0.3
   timers bgp 1 3
   maximum-paths 128
   neighbor SPINES peer group
   neighbor SPINES remote-as 65000
   neighbor SPINES bfd
   neighbor SPINES password 7 jHZ88O3chwnpmpxrF1e8qQ==
   neighbor 10.10.1.3 peer group SPINES
   neighbor 10.10.2.3 peer group SPINES
   redistribute connected route-map REDISTRIBUTE_CONNECTED
```

**leaf3:**

```
route-map REDISTRIBUTE_CONNECTED permit 10
   match interface Loopback0

router bgp 65003
   router-id 10.8.0.4
   timers bgp 1 3
   maximum-paths 128
   neighbor SPINES peer group
   neighbor SPINES remote-as 65000
   neighbor SPINES bfd
   neighbor SPINES password 7 jHZ88O3chwnpmpxrF1e8qQ==
   neighbor 10.10.1.5 peer group SPINES
   neighbor 10.10.2.5 peer group SPINES
   redistribute connected route-map REDISTRIBUTE_CONNECTED
```



***Проверка установки соседства BGP между spine и leaf коммутаторами:***

```
spine1#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.0, local AS number 65000
Neighbor Status Codes: m - Under maintenance
  Neighbor         V  AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.10.1.0        4  65001            313       317    0    0 00:05:06 Estab   1      1
  10.10.1.2        4  65002            307       310    0    0 00:05:02 Estab   1      1
  10.10.1.4        4  65003            303       304    0    0 00:04:58 Estab   1      1

spine2#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.1, local AS number 65000
Neighbor Status Codes: m - Under maintenance
  Neighbor         V  AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.10.2.0        4  65001            348       347    0    0 00:05:39 Estab   1      1
  10.10.2.2        4  65002            342       341    0    0 00:05:35 Estab   1      1
  10.10.2.4        4  65003            338       337    0    0 00:05:31 Estab   1      1

leaf1#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.2, local AS number 65001
Neighbor Status Codes: m - Under maintenance
  Neighbor         V  AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.10.1.1        4  65000            381       378    0    0 00:06:12 Estab   2      2
  10.10.2.1        4  65000            377       378    0    0 00:06:10 Estab   2      2
  
leaf1#show ip bgp
BGP routing table information for VRF default
Router identifier 10.8.0.2, local AS number 65001
Route status codes: * - valid, > - active, # - not installed, E - ECMP head, e - ECMP
                    S - Stale, c - Contributing to ECMP, b - backup, L - labeled-unicast
Origin codes: i - IGP, e - EGP, ? - incomplete
AS Path Attributes: Or-ID - Originator ID, C-LST - Cluster List, LL Nexthop - Link Local Nexthop

         Network                Next Hop            Metric  LocPref Weight  Path
 * >     10.8.0.2/32            -                     0       0       -       i
 * >Ec   10.8.0.3/32            10.10.1.1             0       100     0       65000 65002 i
 *  ec   10.8.0.3/32            10.10.2.1             0       100     0       65000 65002 i
 * >Ec   10.8.0.4/32            10.10.1.1             0       100     0       65000 65003 i
 *  ec   10.8.0.4/32            10.10.2.1             0       100     0       65000 65003 i
```



### Примечание:

* ​	Добавил шаблоны конфигурации jinja для ibg и ebgp для nsos и eos. Объеденил их через if/elif внутри шаблона. Убрал пересечения между работой шаблона для ibgp и ebgp конфигураций.
* nx_os_loader_v2.py добавил в скрипт для конфигурирования устройств возможность потоковой работы с помощью ThreadPoolExecutor.

