# ДЗ №7

### Цели:

- Реализовать передачу суммарных префиксов через EVPN route-type 5

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

**Топология EVE arista :**

<img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab7/bgp_evpn_l2_with_FW.png" style="zoom:200%;" />

### Примененные конфигурации EOS для настройки ebgp c Vlan Based Service и L3 Asymmetric IRB:

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

_**leaf1 (применены vlan 21-24, для разнообразия в vrf SERVICE_2 упаковал vlan 23 и 24**:_

```
! Command: show running-config
! device: leaf1 (vEOS-lab, EOS-4.29.2F)
!
! boot system flash:/vEOS-lab.swi
!
no aaa root
!
username admin privilege 15 role network-admin secret sha512 $6$o5Z1pkhWx5uchk2k$GV7EqcNzDThaT66sWShqcItDHj5nfiGcSktOo8AhQaNGbqV8zmdHM3JulLBdJ4zQirHCB9pMQ09UsI1FEg82b.
username cisco_automate privilege 15 secret sha512 $6$CLdhWrq3g.EW/BdZ$EXRT9nYJd6sW9ko5Yu58cJ4BepCwYt1IZT86nPs1YmZG/wnZdQctuerC0hyA3KPIgSSE4txqmnVEGo36T0hDv.
!
transceiver qsfp default-mode 4x10G
!
service routing protocols model multi-agent
!
no logging console
!
hostname leaf1
!
spanning-tree mode mstp
!
vlan 20-30
!
vrf instance SERVICE
!
vrf instance SERVICE_1
!
vrf instance SERVICE_2
!
vrf instance management
!
interface Ethernet1
   mtu 9214
   no switchport
   ip address 10.10.1.0/31
   bfd echo
!
interface Ethernet2
   mtu 9214
   no switchport
   ip address 10.10.2.0/31
   bfd echo
!
interface Ethernet3
   switchport access vlan 21
!
interface Ethernet4
   switchport access vlan 22
!
interface Ethernet5
   switchport access vlan 23
!
interface Ethernet6
!
interface Ethernet7
!
interface Ethernet8
!
interface Loopback0
   ip address 10.8.0.2/32
!
interface Loopback1
   ip address 10.9.0.2/32
!
interface Management1
   vrf management
   ip address 192.168.254.57/24
!
interface Vlan21
   vrf SERVICE
   ip address virtual 10.11.1.254/24
!
interface Vlan22
   vrf SERVICE_1
   ip address virtual 10.11.2.254/24
!
interface Vlan23
   vrf SERVICE_2
   ip address virtual 10.11.3.254/24
!
interface Vlan24
   vrf SERVICE_2
   ip address virtual 10.11.4.254/24
!
interface Vxlan1
   vxlan source-interface Loopback1
   vxlan udp-port 4789
   vxlan vlan 20-30 vni 10020-10030
   vxlan vrf SERVICE vni 1
   vxlan vrf SERVICE_1 vni 2
   vxlan vrf SERVICE_2 vni 3
!
ip virtual-router mac-address 00:00:22:22:33:33
!
ip routing
ip routing vrf SERVICE
ip routing vrf SERVICE_1
ip routing vrf SERVICE_2
no ip routing vrf management
!
ip prefix-list REDISTRIBUTE_CONNECTED seq 10 permit 10.8.0.0/24 le 32
ip prefix-list REDISTRIBUTE_CONNECTED seq 20 permit 10.9.0.0/24 le 32
!
ip route vrf management 0.0.0.0/0 Management1 192.168.254.1
!
route-map REDISTRIBUTE_CONNECTED permit 10
   match ip address prefix-list REDISTRIBUTE_CONNECTED
!
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
   vlan 23
      rd 10.8.0.2:10023
      route-target both 1:10023
      redistribute learned
   !
   vlan 24
      rd 10.8.0.2:10024
      route-target both 1:10024
      redistribute learned
   !
   address-family evpn
      neighbor SPINE_OVERLAY activate
   !
   vrf SERVICE
      rd 10.8.0.2:1
      route-target import evpn 1:1
      route-target export evpn 1:1
   !
   vrf SERVICE_1
      rd 10.8.0.2:2
      route-target import evpn 1:2
      route-target export evpn 1:2
   !
   vrf SERVICE_2
      rd 10.8.0.2:3
      route-target import evpn 1:3
      route-target export evpn 1:3
```

_**leaf2 (применены vlan 21-24, для разнообразия в vrf SERVICE_2 упаковал vlan 23 и 24**:_

```
! Command: show running-config
! device: leaf2 (vEOS-lab, EOS-4.29.2F)
!
! boot system flash:/vEOS-lab.swi
!
no aaa root
!
username admin privilege 15 role network-admin secret sha512 $6$GjhdgzF0oU2.u1LC$TgWfg5bT8BfdSd0Mdccm1tm.ikLCUNt6Bgkz3gFCX0zh6/aPM8TMRJxYkofgSu53vakhLHY4nq9ebDY2GAjci.
username cisco_automate privilege 15 secret sha512 $6$BSPZYqlrfL0kAF6K$UbhgimAJoQL9ZK.hB3jP.x0t/B9Tgd3kFmnkpWbTe3NAooDAkGbkhfL7RslNTTfH.fj9NBZGDTjlDmz4nQFLu/
!
transceiver qsfp default-mode 4x10G
!
service routing protocols model multi-agent
!
no logging console
!
hostname leaf2
!
spanning-tree mode mstp
!
vlan 20-30
!
vrf instance SERVICE
!
vrf instance SERVICE_1
!
vrf instance SERVICE_2
!
vrf instance management
!
interface Ethernet1
   mtu 9214
   no switchport
   ip address 10.10.1.2/31
   bfd echo
!
interface Ethernet2
   mtu 9214
   no switchport
   ip address 10.10.2.2/31
   bfd echo
!
interface Ethernet3
   switchport access vlan 21
!
interface Ethernet4
   switchport access vlan 22
!
interface Ethernet5
   switchport access vlan 23
!
interface Ethernet6
   switchport access vlan 24
!
interface Ethernet7
!
interface Ethernet8
!
interface Ethernet9
!
interface Ethernet10
!
interface Loopback0
   ip address 10.8.0.3/32
!
interface Loopback1
   ip address 10.9.0.3/32
!
interface Management1
   vrf management
   ip address 192.168.254.58/24
!
interface Vlan21
   vrf SERVICE
   ip address virtual 10.11.1.254/24
!
interface Vlan22
   vrf SERVICE_1
   ip address virtual 10.11.2.254/24
!
interface Vlan23
   vrf SERVICE_2
   ip address virtual 10.11.3.254/24
!
interface Vlan24
   vrf SERVICE_2
   ip address virtual 10.11.4.254/24
!
interface Vxlan1
   vxlan source-interface Loopback1
   vxlan udp-port 4789
   vxlan vlan 20-30 vni 10020-10030
   vxlan vrf SERVICE vni 1
   vxlan vrf SERVICE_1 vni 2
   vxlan vrf SERVICE_2 vni 3
!
ip virtual-router mac-address 00:00:22:22:33:33
!
ip routing
ip routing vrf SERVICE
ip routing vrf SERVICE_1
ip routing vrf SERVICE_2
no ip routing vrf management
!
ip prefix-list REDISTRIBUTE_CONNECTED seq 10 permit 10.8.0.0/24 le 32
ip prefix-list REDISTRIBUTE_CONNECTED seq 20 permit 10.9.0.0/24 le 32
!
ip route vrf management 0.0.0.0/0 Management1 192.168.254.1
!
route-map REDISTRIBUTE_CONNECTED permit 10
   match ip address prefix-list REDISTRIBUTE_CONNECTED
!
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
   vlan 24
      rd 10.8.0.3:10024
      route-target both 1:10024
      redistribute learned
   !
   address-family evpn
      neighbor SPINE_OVERLAY activate
   !
   vrf SERVICE
      rd 10.8.0.3:1
      route-target import evpn 1:1
      route-target export evpn 1:1
   !
   vrf SERVICE_1
      rd 10.8.0.3:2
      route-target import evpn 1:2
      route-target export evpn 1:2
   !
   vrf SERVICE_2
      rd 10.8.0.3:3
      route-target import evpn 1:3
      route-target export evpn 1:3
!
end

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

_**borderlead:**_

```
! Command: show running-config
! device: borderleaf (vEOS-lab, EOS-4.29.2F)
!
! boot system flash:/vEOS-lab.swi
!
no aaa root
!
username admin privilege 15 role network-admin secret sha512 $6$uWvB03bnxURuNGlq$051QbRk3WVVdTzaJqI6Z8nHG995IcOtDLfemS27D0iIQHDhu.tS.ljTfRqnR6NmD2QNeQ1pEnoDk/4wlzANri/
username cisco_automate privilege 15 secret sha512 $6$WhgHXR5BclaJPB53$oQqCApL1B8NTn.uXlikPafhmj9VCdN8avxbj/73Q2cfxt3NwbCCs4wjXcksXzrxxfO4XiP1TkVNxEz1vzL3LM/
!
transceiver qsfp default-mode 4x10G
!
service routing protocols model multi-agent
!
no logging console
!
hostname borderleaf
!
spanning-tree mode mstp
!
vlan 20-30
!
vrf instance SERVICE
!
vrf instance SERVICE_1
!
vrf instance SERVICE_2
!
vrf instance management
!
interface Ethernet1
   mtu 9214
   no switchport
   ip address 10.10.1.4/31
   bfd echo
!
interface Ethernet2
   mtu 9214
   no switchport
   ip address 10.10.2.4/31
   bfd echo
!
interface Ethernet3
   no switchport
!
interface Ethernet3.1
   encapsulation dot1q vlan 1
   vrf SERVICE
   ip address 10.10.1.6/31
!
interface Ethernet3.2
   encapsulation dot1q vlan 2
   vrf SERVICE_1
   ip address 10.10.1.8/31
!
interface Ethernet3.3
   encapsulation dot1q vlan 3
   vrf SERVICE_2
   ip address 10.10.1.10/31
!
interface Ethernet4
!
interface Ethernet5
!
interface Ethernet6
!
interface Ethernet7
!
interface Ethernet8
!
interface Loopback0
   ip address 10.8.0.4/32
!
interface Loopback1
   ip address 10.9.0.4/32
!
interface Management1
   vrf management
   ip address 192.168.254.59/24
!
interface Vlan21
   vrf SERVICE
   ip address virtual 10.11.1.254/24
!
interface Vlan22
   vrf SERVICE_1
   ip address virtual 10.11.2.254/24
!
interface Vlan23
   vrf SERVICE_2
   ip address virtual 10.11.3.254/24
!
interface Vlan24
   vrf SERVICE_2
   ip address virtual 10.11.4.254/24
!
interface Vxlan1
   vxlan source-interface Loopback1
   vxlan udp-port 4789
   vxlan vlan 20-30 vni 10020-10030
   vxlan vrf SERVICE vni 1
   vxlan vrf SERVICE_1 vni 2
   vxlan vrf SERVICE_2 vni 3
!
ip routing
ip routing vrf SERVICE
ip routing vrf SERVICE_1
ip routing vrf SERVICE_2
no ip routing vrf management
!
ip prefix-list PROD seq 10 permit 10.0.0.0/8 le 32
ip prefix-list REDISTRIBUTE_CONNECTED seq 10 permit 10.8.0.0/24 le 32
ip prefix-list REDISTRIBUTE_CONNECTED seq 20 permit 10.9.0.0/24 le 32
!
ip route vrf management 0.0.0.0/0 Management1 192.168.254.1
!
route-map PROD permit 10
   match ip address prefix-list PROD
!
route-map REDISTRIBUTE_CONNECTED permit 10
   match ip address prefix-list REDISTRIBUTE_CONNECTED
!
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
   vlan 24
      rd 10.8.0.4:10024
      route-target both 1:10024
      redistribute learned
   !
   address-family evpn
      neighbor SPINE_OVERLAY activate
   !
   vrf SERVICE
      rd 10.8.0.4:1
      route-target import evpn 1:1
      route-target export evpn 1:1
      neighbor 10.10.1.7 remote-as 4259905000
      neighbor 10.10.1.7 local-as 4259840001 no-prepend replace-as
      redistribute connected route-map PROD
   !
   vrf SERVICE_1
      rd 10.8.0.4:2
      route-target import evpn 1:2
      route-target export evpn 1:2
      neighbor 10.10.1.9 remote-as 4259905000
      neighbor 10.10.1.9 local-as 4259840002 no-prepend replace-as
      redistribute connected route-map PROD
   !
   vrf SERVICE_2
      rd 10.8.0.4:3
      route-target import evpn 1:3
      route-target export evpn 1:3
      neighbor 10.10.1.11 remote-as 4259905000
      neighbor 10.10.1.11 local-as 4259840003 no-prepend replace-as
      redistribute connected route-map PROD
!
end
```

_**FW1:**_

```
fw1#sh run
! Command: show running-config
  ! device: fw1 (vEOS-lab, EOS-4.29.2F)
!
! boot system flash:/vEOS-lab.swi
!
no aaa root
!
transceiver qsfp default-mode 4x10G
!
service routing protocols model multi-agent
!
hostname fw1
!
spanning-tree mode mstp
 !
vrf instance management
!
interface Ethernet1
   no switchport
!
interface Ethernet1.1
   encapsulation dot1q vlan 1
   ip address 10.10.1.7/31
!
interface Ethernet1.2
   encapsulation dot1q vlan 2
   ip address 10.10.1.9/31
!
interface Ethernet1.3
   encapsulation dot1q vlan 3
   ip address 10.10.1.11/31
!
interface Ethernet2
!
interface Ethernet3
!
interface Ethernet4
!
interface Ethernet5
!
interface Ethernet6
!
interface Ethernet7
!
interface Ethernet8
!
interface Ethernet9
!
interface Ethernet10
!
interface Loopback0
   ip address 10.0.0.4/32
!
interface Loopback1
   ip address 8.8.8.8/32
!
interface Management1
   vrf management
   ip address 192.168.254.65/24
!
ip routing
no ip routing vrf management
!
ip prefix-list PRIVATE seq 10 permit 10.0.0.0/8 le 32
ip prefix-list PRIVATE seq 20 permit 192.168.0.0/16 le 32
ip prefix-list PRIVATE seq 30 permit 172.16.0.0/12 le 32
!
ip route vrf management 0.0.0.0/0 Management1 192.168.254.1
!
route-map INTERNET deny 10
   match ip address prefix-list PRIVATE
!
route-map INTERNET permit 20
!
router bgp 4259905000
   router-id 10.0.0.4
   neighbor 10.10.1.6 remote-as 4259840001
   neighbor 10.10.1.8 remote-as 4259840002
   neighbor 10.10.1.10 remote-as 4259840003
   aggregate-address 8.0.0.0/8 summary-only
   redistribute connected route-map INTERNET
!
end
```

***Проверка установки соседства BGP между spine и leaf коммутаторами:***

```
leaf1#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.2, local AS number 65001
Neighbor Status Codes: m - Under maintenance
  Neighbor  V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.8.0.0  4 65000          20618     20538    0    0 00:25:43 Estab   5      5
  10.8.0.1  4 65000          20620     20669    0    0 00:25:43 Estab   5      5
  10.10.1.1 4 65000          20370     20338    0    0 00:25:44 Estab   5      5
  10.10.2.1 4 65000          20388     20351    0    0 00:25:44 Estab   5      5

leaf2#show ip bgp summary
BGP summary information for VRF default
Router identifier 10.8.0.3, local AS number 65002
Neighbor Status Codes: m - Under maintenance
  Neighbor  V AS           MsgRcvd   MsgSent  InQ OutQ  Up/Down State   PfxRcd PfxAcc
  10.8.0.0  4 65000          20631     20604    0    0 04:49:14 Estab   5      5
  10.8.0.1  4 65000          20635     20672    0    0 04:49:14 Estab   5      5
  10.10.1.3 4 65000          20419     20382    0    0 04:35:54 Estab   5      5
  10.10.2.3 4 65000          20360     20392    0    0 04:35:54 Estab   5      5
```

_***Проверка установки соседства BGP между borderleaf и FW1:***_

```
borderleaf#show ip bgp vrf all
BGP routing table information for VRF default
Router identifier 10.8.0.4, local AS number 65003
Route status codes: s - suppressed contributor, * - valid, > - active, E - ECMP head, e - ECMP
                    S - Stale, c - Contributing to ECMP, b - backup, L - labeled-unicast
                    % - Pending BGP convergence
Origin codes: i - IGP, e - EGP, ? - incomplete
RPKI Origin Validation codes: V - valid, I - invalid, U - unknown
AS Path Attributes: Or-ID - Originator ID, C-LST - Cluster List, LL Nexthop - Link Local Nexthop

          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >      10.8.0.0/32            10.10.1.5             0       -          100     0       65000 i
 *        10.8.0.0/32            10.8.0.0              0       -          100     0       65000 i
 * >      10.8.0.1/32            10.10.2.5             0       -          100     0       65000 i
 *        10.8.0.1/32            10.8.0.1              0       -          100     0       65000 i
 * >Ec    10.8.0.2/32            10.10.1.5             0       -          100     0       65000 65001 i
 *  ec    10.8.0.2/32            10.10.2.5             0       -          100     0       65000 65001 i
 *  E     10.8.0.2/32            10.8.0.0              0       -          100     0       65000 65001 i
 *  e     10.8.0.2/32            10.8.0.1              0       -          100     0       65000 65001 i
 * >Ec    10.8.0.3/32            10.10.1.5             0       -          100     0       65000 65002 i
 *  ec    10.8.0.3/32            10.10.2.5             0       -          100     0       65000 65002 i
 *  E     10.8.0.3/32            10.8.0.0              0       -          100     0       65000 65002 i
 *  e     10.8.0.3/32            10.8.0.1              0       -          100     0       65000 65002 i
 * >      10.8.0.4/32            -                     -       -          -       0       i
 * >Ec    10.9.0.2/32            10.10.1.5             0       -          100     0       65000 65001 i
 *  ec    10.9.0.2/32            10.10.2.5             0       -          100     0       65000 65001 i
 *  E     10.9.0.2/32            10.8.0.0              0       -          100     0       65000 65001 i
 *  e     10.9.0.2/32            10.8.0.1              0       -          100     0       65000 65001 i
 * >Ec    10.9.0.3/32            10.10.1.5             0       -          100     0       65000 65002 i
 *  ec    10.9.0.3/32            10.10.2.5             0       -          100     0       65000 65002 i
 *  E     10.9.0.3/32            10.8.0.0              0       -          100     0       65000 65002 i
 *  e     10.9.0.3/32            10.8.0.1              0       -          100     0       65000 65002 i
 * >      10.9.0.4/32            -                     -       -          -       0       i
BGP routing table information for VRF SERVICE
Router identifier 10.11.1.254, local AS number 65003
Route status codes: s - suppressed contributor, * - valid, > - active, E - ECMP head, e - ECMP
                    S - Stale, c - Contributing to ECMP, b - backup, L - labeled-unicast
                    % - Pending BGP convergence
Origin codes: i - IGP, e - EGP, ? - incomplete
RPKI Origin Validation codes: V - valid, I - invalid, U - unknown
AS Path Attributes: Or-ID - Originator ID, C-LST - Cluster List, LL Nexthop - Link Local Nexthop

          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >      8.0.0.0/8              10.10.1.7             0       -          100     0       4259905000 i
 * >      10.10.1.6/31           -                     -       -          -       0       i
 * >      10.10.1.8/31           10.10.1.7             0       -          100     0       4259905000 4259840002 i
 * >      10.10.1.10/31          10.10.1.7             0       -          100     0       4259905000 4259840003 i
 * >      10.11.1.0/24           -                     -       -          -       0       i
 * >      10.11.2.0/24           10.10.1.7             0       -          100     0       4259905000 4259840002 i
 * >      10.11.3.0/24           10.10.1.7             0       -          100     0       4259905000 4259840003 i
 * >      10.11.4.0/24           10.10.1.7             0       -          100     0       4259905000 4259840003 i
BGP routing table information for VRF SERVICE_1
Router identifier 10.11.2.254, local AS number 65003
Route status codes: s - suppressed contributor, * - valid, > - active, E - ECMP head, e - ECMP
                    S - Stale, c - Contributing to ECMP, b - backup, L - labeled-unicast
                    % - Pending BGP convergence
Origin codes: i - IGP, e - EGP, ? - incomplete
RPKI Origin Validation codes: V - valid, I - invalid, U - unknown
AS Path Attributes: Or-ID - Originator ID, C-LST - Cluster List, LL Nexthop - Link Local Nexthop

          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >      8.0.0.0/8              10.10.1.9             0       -          100     0       4259905000 i
 * >      10.10.1.6/31           10.10.1.9             0       -          100     0       4259905000 4259840001 i
 * >      10.10.1.8/31           -                     -       -          -       0       i
 * >      10.10.1.10/31          10.10.1.9             0       -          100     0       4259905000 4259840003 i
 * >      10.11.1.0/24           10.10.1.9             0       -          100     0       4259905000 4259840001 i
 * >      10.11.2.0/24           -                     -       -          -       0       i
 * >      10.11.3.0/24           10.10.1.9             0       -          100     0       4259905000 4259840003 i
 * >      10.11.4.0/24           10.10.1.9             0       -          100     0       4259905000 4259840003 i
BGP routing table information for VRF SERVICE_2
Router identifier 10.11.3.254, local AS number 65003
Route status codes: s - suppressed contributor, * - valid, > - active, E - ECMP head, e - ECMP
                    S - Stale, c - Contributing to ECMP, b - backup, L - labeled-unicast
                    % - Pending BGP convergence
Origin codes: i - IGP, e - EGP, ? - incomplete
RPKI Origin Validation codes: V - valid, I - invalid, U - unknown
AS Path Attributes: Or-ID - Originator ID, C-LST - Cluster List, LL Nexthop - Link Local Nexthop

          Network                Next Hop              Metric  AIGP       LocPref Weight  Path
 * >      8.0.0.0/8              10.10.1.11            0       -          100     0       4259905000 i
 * >      10.10.1.6/31           10.10.1.11            0       -          100     0       4259905000 4259840001 i
 * >      10.10.1.8/31           10.10.1.11            0       -          100     0       4259905000 4259840002 i
 * >      10.10.1.10/31          -                     -       -          -       0       i
 * >      10.11.1.0/24           10.10.1.11            0       -          100     0       4259905000 4259840001 i
 * >      10.11.2.0/24           10.10.1.11            0       -          100     0       4259905000 4259840002 i
 * >      10.11.3.0/24           -                     -       -          -       0       i
 * >      10.11.4.0/24           -                     -       -          -       0       i
 
 
```



***Проверка маршрутов со стороный FW1 на borderleaf (видим суммированый маршрут 8.0.0.0/8 в vrf SERVICE, для остальных vrf аналогично)***

```
borderleaf#show ip route vrf SERVICE 8.8.8.8

VRF: SERVICE
Codes: C - connected, S - static, K - kernel,
       O - OSPF, IA - OSPF inter area, E1 - OSPF external type 1,
       E2 - OSPF external type 2, N1 - OSPF NSSA external type 1,
       N2 - OSPF NSSA external type2, B - Other BGP Routes,
       B I - iBGP, B E - eBGP, R - RIP, I L1 - IS-IS level 1,
       I L2 - IS-IS level 2, O3 - OSPFv3, A B - BGP Aggregate,
       A O - OSPF Summary, NG - Nexthop Group Static Route,
       V - VXLAN Control Service, M - Martian,
       DH - DHCP client installed default route,
       DP - Dynamic Policy Route, L - VRF Leaked,
       G  - gRIBI, RC - Route Cache Route

 B E      8.0.0.0/8 [200/0] via 10.10.1.7, Ethernet3.1
```

***Проверям все маршруты на leaf1 и leaf2. Видим, что маршруты  из других vrf приходят от borderleaf, также видим сеть 8.0.0.0/8 анонсируюмую с fw1. Доступно от хостов есть***

```
leaf1#show bgp evpn route-type ip-prefix ipv4
BGP routing table information for VRF default
Router identifier 10.8.0.2, local AS number 65001
Route status codes: * - valid, > - active, S - Stale, E - ECMP head, e - ECMP
                    c - Contributing to ECMP, % - Pending BGP convergence
Origin codes: i - IGP, e - EGP, ? - incomplete
AS Path Attributes: Or-ID - Originator ID, C-LST - Cluster List, LL Nexthop - Link Local Nexthop

          Network                Next Hop              Metric  LocPref Weight  Path
 * >Ec    RD: 10.8.0.4:1 ip-prefix 8.0.0.0/8
                                 10.9.0.4              -       100     0       65000 65003 4259905000 i
 *  ec    RD: 10.8.0.4:1 ip-prefix 8.0.0.0/8
                                 10.9.0.4              -       100     0       65000 65003 4259905000 i
 * >Ec    RD: 10.8.0.4:2 ip-prefix 8.0.0.0/8
                                 10.9.0.4              -       100     0       65000 65003 4259905000 i
 *  ec    RD: 10.8.0.4:2 ip-prefix 8.0.0.0/8
                                 10.9.0.4              -       100     0       65000 65003 4259905000 i
 * >Ec    RD: 10.8.0.4:3 ip-prefix 8.0.0.0/8
                                 10.9.0.4              -       100     0       65000 65003 4259905000 i
 *  ec    RD: 10.8.0.4:3 ip-prefix 8.0.0.0/8
                                 10.9.0.4              -       100     0       65000 65003 4259905000 i
 * >Ec    RD: 10.8.0.4:1 ip-prefix 10.10.1.6/31
                                 10.9.0.4              -       100     0       65000 65003 i
 *  ec    RD: 10.8.0.4:1 ip-prefix 10.10.1.6/31
                                 10.9.0.4              -       100     0       65000 65003 i
 * >Ec    RD: 10.8.0.4:2 ip-prefix 10.10.1.6/31
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840001 i
 *  ec    RD: 10.8.0.4:2 ip-prefix 10.10.1.6/31
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840001 i
 * >Ec    RD: 10.8.0.4:3 ip-prefix 10.10.1.6/31
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840001 i
 *  ec    RD: 10.8.0.4:3 ip-prefix 10.10.1.6/31
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840001 i
 * >Ec    RD: 10.8.0.4:1 ip-prefix 10.10.1.8/31
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840002 i
 *  ec    RD: 10.8.0.4:1 ip-prefix 10.10.1.8/31
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840002 i
 * >Ec    RD: 10.8.0.4:2 ip-prefix 10.10.1.8/31
                                 10.9.0.4              -       100     0       65000 65003 i
 *  ec    RD: 10.8.0.4:2 ip-prefix 10.10.1.8/31
                                 10.9.0.4              -       100     0       65000 65003 i
 * >Ec    RD: 10.8.0.4:3 ip-prefix 10.10.1.8/31
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840002 i
 *  ec    RD: 10.8.0.4:3 ip-prefix 10.10.1.8/31
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840002 i
 * >Ec    RD: 10.8.0.4:1 ip-prefix 10.10.1.10/31
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840003 i
 *  ec    RD: 10.8.0.4:1 ip-prefix 10.10.1.10/31
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840003 i
 * >Ec    RD: 10.8.0.4:2 ip-prefix 10.10.1.10/31
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840003 i
 *  ec    RD: 10.8.0.4:2 ip-prefix 10.10.1.10/31
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840003 i
 * >Ec    RD: 10.8.0.4:3 ip-prefix 10.10.1.10/31
                                 10.9.0.4              -       100     0       65000 65003 i
 *  ec    RD: 10.8.0.4:3 ip-prefix 10.10.1.10/31
                                 10.9.0.4              -       100     0       65000 65003 i
 * >Ec    RD: 10.8.0.4:1 ip-prefix 10.11.1.0/24
                                 10.9.0.4              -       100     0       65000 65003 i
 *  ec    RD: 10.8.0.4:1 ip-prefix 10.11.1.0/24
                                 10.9.0.4              -       100     0       65000 65003 i
 * >Ec    RD: 10.8.0.4:2 ip-prefix 10.11.1.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840001 i
 *  ec    RD: 10.8.0.4:2 ip-prefix 10.11.1.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840001 i
 * >Ec    RD: 10.8.0.4:3 ip-prefix 10.11.1.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840001 i
 *  ec    RD: 10.8.0.4:3 ip-prefix 10.11.1.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840001 i
 * >Ec    RD: 10.8.0.4:1 ip-prefix 10.11.2.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840002 i
 *  ec    RD: 10.8.0.4:1 ip-prefix 10.11.2.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840002 i
 * >Ec    RD: 10.8.0.4:2 ip-prefix 10.11.2.0/24
                                 10.9.0.4              -       100     0       65000 65003 i
 *  ec    RD: 10.8.0.4:2 ip-prefix 10.11.2.0/24
                                 10.9.0.4              -       100     0       65000 65003 i
 * >Ec    RD: 10.8.0.4:3 ip-prefix 10.11.2.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840002 i
 *  ec    RD: 10.8.0.4:3 ip-prefix 10.11.2.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840002 i
 * >Ec    RD: 10.8.0.4:1 ip-prefix 10.11.3.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840003 i
 *  ec    RD: 10.8.0.4:1 ip-prefix 10.11.3.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840003 i
 * >Ec    RD: 10.8.0.4:2 ip-prefix 10.11.3.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840003 i
 *  ec    RD: 10.8.0.4:2 ip-prefix 10.11.3.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840003 i
 * >Ec    RD: 10.8.0.4:3 ip-prefix 10.11.3.0/24
                                 10.9.0.4              -       100     0       65000 65003 i
 *  ec    RD: 10.8.0.4:3 ip-prefix 10.11.3.0/24
                                 10.9.0.4              -       100     0       65000 65003 i
 * >Ec    RD: 10.8.0.4:1 ip-prefix 10.11.4.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840003 i
 *  ec    RD: 10.8.0.4:1 ip-prefix 10.11.4.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840003 i
 * >Ec    RD: 10.8.0.4:2 ip-prefix 10.11.4.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840003 i
 *  ec    RD: 10.8.0.4:2 ip-prefix 10.11.4.0/24
                                 10.9.0.4              -       100     0       65000 65003 4259905000 4259840003 i
 * >Ec    RD: 10.8.0.4:3 ip-prefix 10.11.4.0/24
                                 10.9.0.4              -       100     0       65000 65003 i
 *  ec    RD: 10.8.0.4:3 ip-prefix 10.11.4.0/24
                                 10.9.0.4              -       100     0       65000 65003 i
```

```
VPC> show

NAME   IP/MASK              GATEWAY                             GATEWAY
VPC    10.11.4.102/24       10.11.4.254
       fe80::250:79ff:fe66:6830/64

VPC> ping 10.11.1.101

84 bytes from 10.11.1.101 icmp_seq=1 ttl=60 time=53.907 ms
84 bytes from 10.11.1.101 icmp_seq=2 ttl=60 time=42.174 ms
^C
VPC> trace 10.11.1.101
trace to 10.11.1.101, 8 hops max, press Ctrl+C to stop
 1   10.11.4.254   4.268 ms  3.720 ms  3.602 ms
 2   10.11.3.254   14.952 ms  14.813 ms  14.049 ms
 3   10.10.1.11   18.495 ms  21.575 ms  21.672 ms
 4   10.10.1.6   25.634 ms  24.733 ms  27.430 ms
 5   10.11.1.254   33.982 ms  35.746 ms  36.676 ms
 6   *10.11.1.101   47.973 ms (ICMP type:3, code:3, Destination port unreachable)

VPC> ping 8.8.8.8

84 bytes from 8.8.8.8 icmp_seq=1 ttl=62 time=25.988 ms
^C
VPC> trace 8.8.8.8
trace to 8.8.8.8, 8 hops max, press Ctrl+C to stop
 1   10.11.4.254   4.017 ms  3.873 ms  3.605 ms
 2   10.11.3.254   14.383 ms  13.411 ms  13.283 ms
 3     *  *  *
 4     *  *  *
```

