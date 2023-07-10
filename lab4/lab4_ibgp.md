# ДЗ №4

### Цели:

- Настроить iBGP для Underlay сети

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



### Примененные конфигурации nexus для настройки ibgp:

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
  
  interface loopback0
  ip address 10.10.0.0/32
  
  router bgp 65000
  router-id 10.10.0.0
  neighbor 10.2.0.0/22
    remote-as 65000
    password 3 9125d59c18a9b015
    timers 3 9
    maximum-peers 10
    address-family ipv4 unicast
      route-reflector-client
      next-hop-self all
```

**spine2:**

```
  feature bgp
  
  interface loopback0
  ip address 10.0.0.2/32
  
router bgp 65000
  router-id 10.0.0.1
  neighbor 10.2.0.0/22
    remote-as 65000
    password 3 9125d59c18a9b015
    timers 3 9
    maximum-peers 10
    address-family ipv4 unicast
      route-reflector-client
      next-hop-self all
```

**leaf1:**

```
feature bgp

interface loopback0
  ip address 10.0.0.2/32
  
router bgp 65000
  router-id 10.0.0.2
  reconnect-interval 12
  address-family ipv4 unicast
    redistribute direct route-map REDISTRIBUTE_CONNECTED
    maximum-paths ibgp 64
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

interface loopback0
  ip address 10.0.0.3/32

router bgp 65000
  router-id 10.0.0.3
  reconnect-interval 12
  address-family ipv4 unicast
    redistribute direct route-map REDISTRIBUTE_CONNECTED
    maximum-paths ibgp 64
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

interface loopback0
  ip address 10.0.0.3/32
  
router bgp 65000
  router-id 10.0.0.4
  reconnect-interval 12
  address-family ipv4 unicast
    redistribute direct route-map REDISTRIBUTE_CONNECTED
    maximum-paths ibgp 64
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

```isis_adj
spine1# sh ip bgp summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.2.1.0        4 65000    9365    9362       16    0    0 07:47:56 1
10.2.1.2        4 65000    9359    9356       16    0    0 07:47:36 1
10.2.1.4        4 65000    9362    9361       16    0    0 07:47:23 1

spine2# show ip bgp summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.2.2.0        4 65000    9362    9361       14    0    0 07:48:44 1
10.2.2.2        4 65000    9376    9371       14    0    0 07:48:44 1
10.2.2.4        4 65000    9372    9369       14    0    0 07:48:23 1

leaf1# show ip bgp summary
Neighbor        V    AS MsgRcvd MsgSent   TblVer  InQ OutQ Up/Down  State/PfxRcd
10.2.1.1        4 65000    9386    9382       11    0    0 07:49:51 2
10.2.2.1        4 65000    9380    9379       11    0    0 07:49:35 2

spine2# sh ip bgp
   Network            Next Hop            Metric     LocPrf     Weight Path
*>i10.0.0.2/32        10.2.2.0                 0        100          0 ?
*>i10.0.0.3/32        10.2.2.2                 0        100          0 ?
*>i10.0.0.4/32        10.2.2.4                 0        100          0 ?

leaf1# show ip route 10.0.0.3
10.0.0.3/32, ubest/mbest: 2/0
    *via 10.2.1.1, [200/0], 07:55:27, bgp-65000, internal, tag 65000
    *via 10.2.2.1, [200/0], 07:55:11, bgp-65000, internal, tag 65000

```



### Примененные конфигурации EOS для настройки ibgp:

**Пример конфигурации интерфейса spine/leaf  для arista**:

```
interface Ethernet1
   mtu 9214
   no switchport
   ip address 10.10.1.1/31
   bfd echo
```

**spine1:**

```
router bgp 65000
   router-id 10.8.0.0
   timers bgp 1 3
   maximum-paths 128
   bgp listen range 10.10.0.0/22 peer-group LEAFS remote-as 65000
   neighbor LEAFS peer group
   neighbor LEAFS next-hop-self
   neighbor LEAFS bfd
   neighbor LEAFS route-reflector-client
   neighbor LEAFS password 7 qcZqPZg4u36aJMQlNFmhpQ==
```

**spine2:**

```
router bgp 65000
   router-id 10.8.0.1
   timers bgp 1 3
   maximum-paths 128
   bgp listen range 10.10.0.0/22 peer-group LEAFS remote-as 65000
   neighbor LEAFS peer group
   neighbor LEAFS next-hop-self
   neighbor LEAFS bfd
   neighbor LEAFS route-reflector-client
   neighbor LEAFS password 7 qcZqPZg4u36aJMQlNFmhpQ==
```

**leaf1**:

```
route-map REDISTRIBUTE_CONNECTED permit 10
   match interface Loopback0

router bgp 65000
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

router bgp 65000
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

router bgp 65000
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
  10.10.1.0        4  65000            398       403    0    0 00:06:33 Estab   1      1
  10.10.1.2        4  65000            393       397    0    0 00:06:29 Estab   1      1
  10.10.1.4        4  65000            389       390    0    0 00:06:24 Estab   1      1

spine2#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.1, local AS number 65000
Neighbor Status Codes: m - Under maintenance
  Neighbor         V  AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.10.2.0        4  65000            422       426    0    0 00:06:58 Estab   1      1
  10.10.2.2        4  65000            418       419    0    0 00:06:54 Estab   1      1
  10.10.2.4        4  65000            414       415    0    0 00:06:50 Estab   1      1

leaf1#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.2, local AS number 65000
Neighbor Status Codes: m - Under maintenance
  Neighbor         V  AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.10.1.1        4  65000            453       448    0    0 00:07:23 Estab   2      2
  10.10.2.1        4  65000            449       446    0    0 00:07:21 Estab   2      2
  
leaf1#show ip bgp
BGP routing table information for VRF default
Router identifier 10.8.0.2, local AS number 65000
Route status codes: * - valid, > - active, # - not installed, E - ECMP head, e - ECMP
                    S - Stale, c - Contributing to ECMP, b - backup, L - labeled-unicast
Origin codes: i - IGP, e - EGP, ? - incomplete
AS Path Attributes: Or-ID - Originator ID, C-LST - Cluster List, LL Nexthop - Link Local Nexthop

         Network                Next Hop            Metric  LocPref Weight  Path
 * >     10.8.0.2/32            -                     0       0       -       i
 * >Ec   10.8.0.3/32            10.10.1.1             0       100     0       i Or-ID: 10.8.0.3 C-LST: 10.8.0.0
 *  ec   10.8.0.3/32            10.10.2.1             0       100     0       i Or-ID: 10.8.0.3 C-LST: 10.8.0.1
 * >Ec   10.8.0.4/32            10.10.1.1             0       100     0       i Or-ID: 10.8.0.4 C-LST: 10.8.0.0
 *  ec   10.8.0.4/32            10.10.2.1             0       100     0       i Or-ID: 10.8.0.4 C-LST: 10.8.0.1
```

### Примечание:

* ​	Добавил шаблоны конфигурации jinja для ibg и ebgp для nsos и eos. Объеденил их через if/elif внутри шаблона. Убрал пересечения между работой шаблона для ibgp и ebgp конфигураций.
* nx_os_loader_v2.py добавил в скрипт для конфигурирования устройств возможность потоковой работы с помощью ThreadPoolExecutor.
