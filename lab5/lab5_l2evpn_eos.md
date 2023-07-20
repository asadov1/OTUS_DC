# ДЗ №5

### Цели:

- Настроить Overlay на основе VxLAN EVPN для L2 связанности между клиентами

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

**spine1/2 (_конфигурации полностью идентичны_):**

- service routing protocols model multi-agent - _без этой команды не работал evpn, не знаю это особенность виртуалки или также работат на железке_

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
   bgp listen range 10.8.0.0/24 peer-group LEAF_OVERLAY pee9
   bgp listen range 10.10.0.0/22 peer-group LEAF_UNDERLAY p9
   neighbor LEAF_OVERLAY peer group
   neighbor LEAF_OVERLAY update-source Loopback0
   neighbor LEAF_OVERLAY ebgp-multihop
   neighbor LEAF_OVERLAY send-community
   neighbor LEAF_UNDERLAY peer group
   neighbor LEAF_UNDERLAY bfd
   neighbor LEAF_UNDERLAY password 7 F0ycgLa3E/blyskQ/za9aQ=
   neighbor SPINE_OVERLAY peer group
   neighbor SPINE_OVERLAY ebgp-multihop 2
   redistribute connected route-map REDISTRIBUTE_CONNECTED
   !
   address-family evpn
      neighbor LEAF_OVERLAY activate
```

**leaf1**:

```
service routing protocols model multi-agent

ip prefix-list REDISTRIBUTE_CONNECTED seq 10 permit 10.8.0.0/24 le 32
ip prefix-list REDISTRIBUTE_CONNECTED seq 20 permit 10.9.0.0/24 le 32

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
      route-target both 65000:10021
      redistribute learned
   !
   address-family evpn
      neighbor SPINE_OVERLAY activate
   !
   address-family ipv4
      no neighbor SPINE_OVERLAY activate

interface Vxlan1
   vxlan source-interface Loopback1
   vxlan udp-port 4789
   vxlan vlan 20-30 vni 10020-10030
```

**leaf2:**

```
service routing protocols model multi-agent

ip prefix-list REDISTRIBUTE_CONNECTED seq 10 permit 10.8.0.0/24 le 32
ip prefix-list REDISTRIBUTE_CONNECTED seq 20 permit 10.9.0.0/24 le 32

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
   vlan 22
      rd 10.8.0.3:10022
      route-target both 65000:10022
      redistribute learned
   !
   vlan 23
      rd 10.8.0.3:10023
      route-target both 65000:10023
      redistribute learned
   !
   address-family evpn
      neighbor SPINE_OVERLAY activate
   !
   address-family ipv4
      no neighbor SPINE_OVERLAY activate

interface Vxlan1
   vxlan source-interface Loopback1
   vxlan udp-port 4789
   vxlan vlan 20-30 vni 10020-10030
```

**leaf3:**

```
service routing protocols model multi-agent

ip prefix-list REDISTRIBUTE_CONNECTED seq 10 permit 10.8.0.0/24 le 32
ip prefix-list REDISTRIBUTE_CONNECTED seq 20 permit 10.9.0.0/24 le 32

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
      route-target both 65000:10021
      redistribute learned
   !
   vlan 23
      rd 10.8.0.4:10023
      route-target both 65000:10023
      redistribute learned
   !
   address-family evpn
      neighbor SPINE_OVERLAY activate
   !
   address-family ipv4
      no neighbor SPINE_OVERLAY activate
interface Vxlan1
   vxlan source-interface Loopback1
   vxlan udp-port 4789
   vxlan vlan 20-30 vni 10020-10030
```



***Проверка установки соседства BGP Underlay между spine и leaf коммутаторами:***

```
leaf2#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.3, local AS number 65002
Neighbor Status Codes: m - Under maintenance
  Neighbor  V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.10.1.3 4 65000          16133     16108    0    0 03:49:00 Estab   5      5
  10.10.2.3 4 65000          11345     11377    0    0 00:45:51 Estab   5      5

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

