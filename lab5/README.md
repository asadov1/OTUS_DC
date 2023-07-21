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

**Таблиа распределения vlan/vni/subnet подсетей:**

| Description | VLAN |  VNI  |    Subnet    |
| :---------: | :--: | :---: | :----------: |
|  Service_1  |  21  | 10021 | 10.11.1.0/24 |
|  Service_2  |  22  | 10022 | 10.11.2.0/24 |
|  Service_3  |  23  | 10023 | 10.11.3.0/24 |
|  Service_4  |  24  | 10024 | 10.11.4.0/24 |

**Топология EVE nexus & arista :**

<img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab5/bgp_evpn_l2.png" style="zoom:200%;" />

### Примененные конфигурации EOS для настройки ebgp c Vlan Based Service:

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

- service routing protocols model multi-agent - без этой команды не работал evpn, не знаю это особенность виртуалки или также работает на железке.

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
   neighbor LEAF_OVERLAY ebgp-multihop
   neighbor LEAF_OVERLAY send-community
   neighbor LEAF_UNDERLAY peer group
   neighbor LEAF_UNDERLAY bfd
   neighbor LEAF_UNDERLAY password 7 F0ycgLa3E/blyskQ/za9aQ==
   neighbor SPINE_OVERLAY peer group
   neighbor SPINE_OVERLAY ebgp-multihop 2
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

_**leaf2:**_

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

_**leaf3:**_

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

_**Вопрос:** Статус Estab(NotNegotiated) для evpn хостов при выводе show ip bgp summary это нормальная реакциия? Так как на самом деле в show bgp evpn summ все ок._

```
spine1#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.0, local AS number 65000
Neighbor Status Codes: m - Under maintenance
  Neighbor  V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.8.0.2  4 65001          72085     72086    0    0 17:03:42 Estab(NotNegotiated)
  10.8.0.3  4 65002          71907     71935    0    0 17:01:36 Estab(NotNegotiated)
  10.8.0.4  4 65003          72121     72105    0    0 17:03:42 Estab(NotNegotiated)
  10.10.1.0 4 65001          71904     71905    0    0 17:01:40 Estab   2      2
  10.10.1.2 4 65002          71925     71960    0    0 17:01:40 Estab   2      2
  10.10.1.4 4 65003          71930     71944    0    0 17:01:40 Estab   2      2

spine2#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.1, local AS number 65000
Neighbor Status Codes: m - Under maintenance
  Neighbor         V  AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.10.2.0        4  65001            348       347    0    0 00:05:39 Estab   1      1
  10.10.2.2        4  65002            342       341    0    0 00:05:35 Estab   1      1
  10.10.2.4        4  65003            338       337    0    0 00:05:31 Estab   1      1

leaf1(config)#sh ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.2, local AS number 65001
Neighbor Status Codes: m - Under maintenance
  Neighbor  V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.10.1.1 4 65000          89277     89294    0    0 17:02:50 Estab   5      5
  10.10.2.1 4 65000          84502     84493    0    0 17:03:56 Estab   5      5
  
leaf2#sh ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.3, local AS number 65002
Neighbor Status Codes: m - Under maintenance
  Neighbor  V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.10.1.3 4 65000          88776     88724    0    0 17:03:10 Estab   5      5
  10.10.2.3 4 65000          83990     83975    0    0 17:02:25 Estab   5      5

leaf3#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.4, local AS number 65003
Neighbor Status Codes: m - Under maintenance
  Neighbor  V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.10.1.5 4 65000          88432     88437    0    0 17:03:45 Estab   5      5
  10.10.2.5 4 65000          83658     83729    0    0 17:03:00 Estab   5      5

```



_***Проверка установки соседства BGP EVPN Overlay между spine и leaf коммутаторами:***_

```
spine1#show bgp evpn summary
BGP summary information for VRF default
Router identifier 10.8.0.0, local AS number 65000
Neighbor Status Codes: m - Under maintenance
  Neighbor V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.8.0.2 4 65001          72709     72704    0    0 17:12:30 Estab   1      1
  10.8.0.3 4 65002          72529     72553    0    0 17:10:24 Estab   2      2
  10.8.0.4 4 65003          72740     72725    0    0 17:12:30 Estab   2      2
  
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



***Проверка доступности между Service_1_leaf1 c ip 10.11.1.100 и Service_1_leaf3 с ip 10.11.1.101***

```
Service_1_l1> ping 10.11.1.101
84 bytes from 10.11.1.101 icmp_seq=1 ttl=64 time=38.103 ms
84 bytes from 10.11.1.101 icmp_seq=2 ttl=64 time=18.610 ms
84 bytes from 10.11.1.101 icmp_seq=3 ttl=64 time=28.706 ms

Service_1_l3> ping 10.11.1.100
84 bytes from 10.11.1.100 icmp_seq=1 ttl=64 time=38.630 ms
84 bytes from 10.11.1.100 icmp_seq=2 ttl=64 time=16.611 ms
84 bytes from 10.11.1.100 icmp_seq=3 ttl=64 time=28.116 ms
```

```
leaf1(config)#show vxlan vtep detail
Remote VTEPS for Vxlan1:

VTEP           Learned Via         MAC Address Learning       Tunnel Type(s)
-------------- ------------------- -------------------------- --------------
10.9.0.4       control plane       control plane              unicast, flood

leaf3#show vxlan vtep detail
Remote VTEPS for Vxlan1:

VTEP           Learned Via         MAC Address Learning       Tunnel Type(s)
-------------- ------------------- -------------------------- --------------
10.9.0.2       control plane       control plane              flood, unicast
10.9.0.3       control plane       control plane              flood
```

```
leaf3#show bgp evpn route-type mac-ip
BGP routing table information for VRF default
Router identifier 10.8.0.4, local AS number 65003
Route status codes: * - valid, > - active, S - Stale, E - ECMP head, e - ECMP
                    c - Contributing to ECMP, % - Pending BGP convergence
Origin codes: i - IGP, e - EGP, ? - incomplete
AS Path Attributes: Or-ID - Originator ID, C-LST - Cluster List, LL Nexthop - Link Local Nexthop

          Network                Next Hop              Metric  LocPref Weight  Path
 * >Ec    RD: 10.8.0.2:10021 mac-ip 0050.7966.683d
                                 10.9.0.2              -       100     0       65000 65001 i
 *  ec    RD: 10.8.0.2:10021 mac-ip 0050.7966.683d
                                 10.9.0.2              -       100     0       65000 65001 i
 * >      RD: 10.8.0.4:10023 mac-ip 0050.7966.683f
                                 -                     -       -       0       i
 * >      RD: 10.8.0.4:10021 mac-ip 0050.7966.6840
                                 -                     -       -       0       i
 * >Ec    RD: 10.8.0.3:10023 mac-ip 0050.7966.6843
                                 10.9.0.3              -       100     0       65000 65002 i
 *  ec    RD: 10.8.0.3:10023 mac-ip 0050.7966.6843
                                 10.9.0.3              -       100     0       65000 65002 i
                                 
leaf1(config)#show bgp evpn route-type mac-ip
BGP routing table information for VRF default
Router identifier 10.8.0.2, local AS number 65001
Route status codes: * - valid, > - active, S - Stale, E - ECMP head, e - ECMP
                    c - Contributing to ECMP, % - Pending BGP convergence
Origin codes: i - IGP, e - EGP, ? - incomplete
AS Path Attributes: Or-ID - Originator ID, C-LST - Cluster List, LL Nexthop - Link Local Nexthop

          Network                Next Hop              Metric  LocPref Weight  Path
 * >      RD: 10.8.0.2:10021 mac-ip 0050.7966.683d
                                 -                     -       -       0       i
 * >Ec    RD: 10.8.0.4:10023 mac-ip 0050.7966.683f
                                 10.9.0.4              -       100     0       65000 65003 i
 *  ec    RD: 10.8.0.4:10023 mac-ip 0050.7966.683f
                                 10.9.0.4              -       100     0       65000 65003 i
 * >Ec    RD: 10.8.0.4:10021 mac-ip 0050.7966.6840
                                 10.9.0.4              -       100     0       65000 65003 i
 *  ec    RD: 10.8.0.4:10021 mac-ip 0050.7966.6840
                                 10.9.0.4              -       100     0       65000 65003 i
 * >Ec    RD: 10.8.0.3:10023 mac-ip 0050.7966.6843
                                 10.9.0.3              -       100     0       65000 65002 i
 *  ec    RD: 10.8.0.3:10023 mac-ip 0050.7966.6843
                                 10.9.0.3              -       100     0       65000 65002 i
```

_***Немного смотрим wireshark:***_

- Сбросил полностью bgp на leaf1 и включил в wireshark фильтра _**bgp.update.path_attributes**_ чтобы посмотреть все сообщения update. Также после установки сессии underlay ebgp выполнил ping между service_1 на leaf1 и leaf3. Для установки маршрутов и mac-ip.

  - Видим, что нам пришел BGP update из Underlay сети от Spine1. В NLRI видим информацию о loopback адресах на leaf2 и leaf3. Также в соседнем update отдаем в сторону Spine1 (и Spine2) информацию о анансируемых loopback на leaf1.

  <img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab5/bgp_up_under.png" style="zoom:80%;" />

  - Далее от Spine1 (и Spine2 конечно тоже) получаем update evpn **type-3**

    - Данный update c next-hop 10.9.0.3 т.е. от leaf2. Также подобные update есть от leaf3. В целом их количесво зависит от количества VNI передавемых в update.
    - В NLRI видим, что это маршрут Route 3, в данном случае он нужен для подписки данного VTEP на рассылку BUM трафика.
    - Также в NLRI видим информацию об RD для 10.8.0.3:10023 для обеспечения уникальность информации пришедшей от leaf3 
    - В extended_community видим значение RT 65000:10023 для импорта/экспорта информации в vrf 65000 и информацию о типе инкапсуляции - VXLAN
    - Далее в атрибуте PMSI_TUNNEL_ATTRIBUE (Provider Multicast Service Interface) мы видим, что  наш vtep leaf1 в данном update подписывается на прием информации BUM от VNI 10023

      <img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab5/evpnL3route.png" style="zoom:80%;" />

  - Следущий update это evpn **type-2**. Он в данном случае исходящий с leaf 1 в момент  запуска ping от Service_1 расположенном на leaf1.

    - В MP_REACH_NLRI передаем адрес lo1 на leaf1 как next-hop.
    - В NLRI EVPN видим типа маршрута 2.
    - Указываетcя наш RT 10.8.0.2:10021 для соотвествия IP.
    - В поле MAC_Adress видим mac от выученного устройства Servicre1 на leaf1.
    - Ethenet tag - 0 (тк VLAN BASE модель).
    - IP Adrees поле пусто так как фабрика данный момент L2.
    - Для передачи данных самих данных через data plane передаем VNI: 10021.
    - В Ex. communities передаем RT для импорта/экспорта информации в mac-vrf 65000:10021

	   <img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab5/evpnL2route.png" style="zoom:80%;" />





### Примененные конфигурации EOS для настройки ebgp c Vlan Aware Service:

_**Конфигурации BGP для leaf1, leaf2, leaf3 (изменения только в настройке vlan):**_

- В данной конфигурации мы назначамем общие значения RD и RT для всех клиентов на каждом leaf. Изменения только в RD, для идентификации IP каждого leaf.
- все остальные настройка аналогичны vlan base

```
leaf1:
   vlan-aware-bundle SERVICES
      rd 10.8.0.2:10000
      route-target both 65000:10000
      redistribute learned
      vlan 20-30
      
leaf2:
  vlan-aware-bundle SERVICES
      rd 10.8.0.3:10000
      route-target both 65000:10000
      redistribute learned
      vlan 20-30
    
 leaf3:
  vlan-aware-bundle SERVICES
      rd 10.8.0.4:10000
      route-target both 65000:10000
      redistribute learned
      vlan 20-30
    
```

_***Немного смотрим wireshark:***_

- Связность в настроенной модели vlan aware работает.
- Основное, что мы видим - это Ethernet Tag для определения из какого vlan у нас прилетел изученый mac адрес. В данном случае это update от leaf3, vlan 21 и mac его клиента :68:40

<img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab5/evnl3_aware.png" style="zoom:80%;" />





### Примечание:

* Добавил шаблоны конфигурации jinja для ibg и ebgp для nsos и eos. Объеденил их через if/elif внутри шаблона. Убрал пересечения между работой шаблона для ibgp и ebgp конфигураций.

* nx_os_loader_v2.py добавил в скрипт для конфигурирования устройств возможность потоковой работы с помощью ThreadPoolExecutor.

* Планирую сделать Ansible проект аналогично моему самописному скрипту на python для автоматизации сценарием конфигураций Underlay и Overlay в лабе.

  

