# ДЗ №2

### Цели:

- Исследовать построение Underlay сети с использованием OSPF

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

|          Description          |    IP_subnet    |
| :---------------------------: | :-------------: |
| P2P_Spine**1**_to_LeafN _/31  | 10.2.**1**.0/24 |
| P2P_Spine**2**_to_LeafN  _/31 | 10.2.**2**.0/24 |
|           Loopback            |   10.0.1.0/24   |
|           Loopback            |   10.1.0.0/24   |
|           Service_1           |   10.4.0.0/24   |
|           Service_2           |   10.4.1.0/24   |
|           Service_3           |   10.4.2.0/24   |
|           Service_4           |   10.4.3.0/24   |

**Диаграмма топологии сети:**

<img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab1/topology_1.drawio.png" alt="net_diag" style="zoom:80%;" /> 

**Топология EVE:**

<img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab2/topology_eve.png" alt="eve_net_diag" style="zoom:40%;" />



### Примененные конфигурации:

**Spine1:**

```
hostname Spine1
feature ospf

vrf context management
  ip route 0.0.0.0/0 mgmt0 192.168.254.1

interface Ethernet1/1
  no switchport
  medium p2p
  ip address 10.2.1.1/31
  ip ospf message-digest-key 1 md5 3 9125d59c18a9b015
  ip router ospf UNDERLAY area 0.0.0.0
  no shutdown

interface Ethernet1/2
  no switchport
  medium p2p
  ip address 10.2.1.3/31
  ip ospf message-digest-key 1 md5 3 9125d59c18a9b015
  ip router ospf UNDERLAY area 0.0.0.0
  no shutdown

interface Ethernet1/3
  no switchport
  medium p2p
  ip address 10.2.1.5/31
  ip ospf message-digest-key 1 md5 3 9125d59c18a9b015
  ip router ospf UNDERLAY area 0.0.0.0
  no shutdown

interface mgmt0
  vrf member management
  ip address 192.168.254.50/24

interface loopback0
  ip address 10.0.1.0/32
icam monitor scale

cli alias name wr copy run start
line console
line vty
router ospf UNDERLAY
  router-id 10.0.1.0

```

**Spine2:**

```
hostname Spine2
feature ospf

vrf context management
  ip route 0.0.0.0/0 mgmt0 192.168.254.1

interface Ethernet1/1
  no switchport
  medium p2p
  ip address 10.2.2.1/31
  ip ospf message-digest-key 1 md5 3 9125d59c18a9b015
  ip router ospf UNDERLAY area 0.0.0.0
  no shutdown

interface Ethernet1/2
  no switchport
  medium p2p
  ip address 10.2.2.3/31
  ip ospf message-digest-key 1 md5 3 9125d59c18a9b015
  ip router ospf UNDERLAY area 0.0.0.0
  no shutdown

interface Ethernet1/3
  no switchport
  medium p2p
  ip address 10.2.2.5/31
  ip ospf message-digest-key 1 md5 3 9125d59c18a9b015
  ip router ospf UNDERLAY area 0.0.0.0
  no shutdown
  
interface mgmt0
  vrf member management
  ip address 192.168.254.51/24

interface loopback0
  ip address 10.0.1.1/32
icam monitor scale

cli alias name wr copy run start
line console
line vty
router ospf UNDERLAY
  router-id 10.0.1.1
```

***leaf1:***

```
hostname leaf1
feature ospf

vrf context management
  ip route 0.0.0.0/0 mgmt0 192.168.254.1

interface Ethernet1/1
  no switchport
  medium p2p
  ip address 10.2.1.0/31
  ip ospf message-digest-key 1 md5 3 9125d59c18a9b015
  ip router ospf UNDERLAY area 0.0.0.0
  no shutdown

interface Ethernet1/2
  no switchport
  medium p2p
  ip address 10.2.2.0/31
  ip ospf message-digest-key 1 md5 3 9125d59c18a9b015
  ip router ospf UNDERLAY area 0.0.0.0
  no shutdown

interface mgmt0
  vrf member management
  ip address 192.168.254.52/24

interface loopback0
  ip address 10.0.1.2/32
icam monitor scale

cli alias name wr copy run start
line console
line vty
router ospf UNDERLAY
  router-id 10.0.1.2
```

***leaf2:***

```
hostname leaf2
feature ospf

vrf context management
  ip route 0.0.0.0/0 mgmt0 192.168.254.1

interface Ethernet1/1
  no switchport
  medium p2p
  ip address 10.2.1.2/31
  ip ospf message-digest-key 1 md5 3 9125d59c18a9b015
  ip router ospf UNDERLAY area 0.0.0.0
  no shutdown

interface Ethernet1/2
  no switchport
  medium p2p
  ip address 10.2.2.2/31
  ip ospf message-digest-key 1 md5 3 9125d59c18a9b015
  ip router ospf UNDERLAY area 0.0.0.0
  no shutdown

nterface mgmt0
  vrf member management
  ip address 192.168.254.53/24

interface loopback0
  ip address 10.0.1.3/32
icam monitor scale

cli alias name wr copy run start
line console
line vty
router ospf UNDERLAY
  router-id 10.0.1.3
```

***leaf3:***

```
hostname leaf3
feature ospf

vrf context management
  ip route 0.0.0.0/0 mgmt0 192.168.254.1

interface Ethernet1/1
  no switchport
  medium p2p
  ip address 10.2.1.4/31
  ip ospf message-digest-key 1 md5 3 9125d59c18a9b015
  ip router ospf UNDERLAY area 0.0.0.0
  no shutdown

interface Ethernet1/2
  no switchport
  medium p2p
  ip address 10.2.2.4/31
  ip ospf message-digest-key 1 md5 3 9125d59c18a9b015
  ip router ospf UNDERLAY area 0.0.0.0
  no shutdown

interface mgmt0
  vrf member management
  ip address 192.168.254.54/24

interface loopback0
  ip address 10.0.1.4/32
icam monitor scale

cli alias name wr copy run start
line console
line vty
router ospf UNDERLAY
  router-id 10.0.1.4
```

***Проверка установки соседства ospf между spine и leaf коммутаторами:***

```
Spine1# sh ip ospf neighbors
 OSPF Process ID UNDERLAY VRF default
 Total number of neighbors: 3
 Neighbor ID     Pri State            Up Time  Address         Interface
 10.0.1.2          1 FULL/ -          03:27:43 10.2.1.0        Eth1/1
 10.0.1.3          1 FULL/ -          03:27:14 10.2.1.2        Eth1/2
 10.0.1.4          1 FULL/ -          03:28:25 10.2.1.4        Eth1/3
 
Spine2# show ip ospf neighbors
 OSPF Process ID UNDERLAY VRF default
 Total number of neighbors: 3
 Neighbor ID     Pri State            Up Time  Address         Interface
 10.0.1.2          1 FULL/ -          00:04:02 10.2.2.0        Eth1/1
 10.0.1.3          1 FULL/ -          00:04:04 10.2.2.2        Eth1/2
 10.0.1.4          1 FULL/ -          00:04:04 10.2.2.4        Eth1/3
```

### Примечание:

Дополнительно сделал линк в vrf management для автоматизации управления конфигурацией коммутаторами. Не в тему курса, но все равно думаю не лишнее. Скрипты так же в папке lab2.
