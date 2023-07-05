# ДЗ №4

### Цели:

- Настроить BGP для Underlay сети

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

|          Description          | IP_subnet_pod1  |  IP_subnet_pod2  |
| :---------------------------: | :-------------: | :--------------: |
| P2P_Spine**1**_to_LeafN _/31  | 10.2.**1**.0/24 | 10.10.**1**.0/24 |
| P2P_Spine**2**_to_LeafN  _/31 | 10.2.**2**.0/24 | 10.10.**2**.0/24 |
|           Loopback            |   10.0.0.0/24   |   10.8.0.0/24    |
|           Loopback            |   10.1.0.0/24   |   10.9.0.0/24    |
|           Service_1           |   10.4.0.0/24   |   10.11.0.0/24   |
|           Service_2           |   10.4.1.0/24   |   10.11.1.0/24   |
|           Service_3           |   10.4.2.0/24   |   10.11.2.0/24   |
|           Service_4           |   10.4.3.0/24   |   10.11.3.0/24   |

**Диаграмма топологии сети:**

<img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab1/topology_1.drawio.png" alt="net_diag" style="zoom:80%;" /> 

**Топология EVE nexus & arista :**

<img src="https://raw.githubusercontent.com/asadov1/OTUS_DC/master/lab4/eve_bgp.png" style="zoom:40%;" />



### Примененные конфигурации:

```
<details>
  <summary>Конфигурация для NX-OS ibgp</summary>
  **Spine1**
  ```feature bgp
  route-map REDISTRIBUTE_CONNECTED permit 10
  match interface loopback0 
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

</details>
```

**Spine1:**

```Spine1
hostname Spine1
feature isis

key chain ISIS
  key 0
    key-string 7 070c285f4d06
vrf context management
  ip route 0.0.0.0/0 mgmt0 192.168.254.1

interface Ethernet1/1
  no switchport
  mtu 9216
  medium p2p
  no ip redirects
  ip address 10.2.1.1/31
  no isis hello-padding always
  isis network point-to-point
  isis authentication-type md5 level-2
  isis authentication key-chain ISIS level-2
  ip router isis UNDERLAY
  no shutdown

interface Ethernet1/2
  no switchport
  mtu 9216
  medium p2p
  no ip redirects
  ip address 10.2.1.3/31
  no isis hello-padding always
  isis network point-to-point
  isis authentication-type md5 level-2
  isis authentication key-chain ISIS level-2
  ip router isis UNDERLAY
  no shutdown

interface Ethernet1/3
  no switchport
  mtu 9216
  medium p2p
  no ip redirects
  ip address 10.2.1.5/31
  no isis hello-padding always
  isis network point-to-point
  isis authentication-type md5 level-2
  isis authentication key-chain ISIS level-2
  ip router isis UNDERLAY
  no shutdown

interface mgmt0
  vrf member management
  ip address 192.168.254.50/24

interface loopback0
  ip address 10.0.1.0/32
  ip router isis UNDERLAY
icam monitor scale

cli alias name wr copy run start
line console
line vty
router isis UNDERLAY
  net 49.0001.0100.0000.1000.00
  is-type level-2
  max-lsp-lifetime 65535
  set-overload-bit on-startup 180
  log-adjacency-changes
  authentication-type md5 level-2
  authentication key-chain ISIS level-2

```



**Spine2:**

```Spine2
hostname Spine2
feature isis

key chain ISIS
  key 0
    key-string 7 070c285f4d06
vrf context management
  ip route 0.0.0.0/0 mgmt0 192.168.254.1
  
interface Ethernet1/1
  no switchport
  mtu 9216
  medium p2p
  no ip redirects
  ip address 10.2.2.1/31
  no isis hello-padding always
  isis network point-to-point
  isis authentication-type md5 level-2
  isis authentication key-chain ISIS level-2
  ip router isis UNDERLAY
  no shutdown

interface Ethernet1/2
  no switchport
  mtu 9216
  medium p2p
  no ip redirects
  ip address 10.2.2.3/31
  no isis hello-padding always
  isis network point-to-point
  isis authentication-type md5 level-2
  isis authentication key-chain ISIS level-2
  ip router isis UNDERLAY
  no shutdown

interface Ethernet1/3
  no switchport
  mtu 9216
  medium p2p
  no ip redirects
  ip address 10.2.2.5/31
  no isis hello-padding always
  isis network point-to-point
  isis authentication-type md5 level-2
  isis authentication key-chain ISIS level-2
  ip router isis UNDERLAY
  no shutdown
  
interface mgmt0
  vrf member management
  ip address 192.168.254.51/24

interface loopback0
  ip address 10.0.1.1/32
  ip router isis UNDERLAY
icam monitor scale

cli alias name wr copy run start
line console
line vty
router isis UNDERLAY
  net 49.0001.0100.0000.1001.00
  is-type level-2
  max-lsp-lifetime 65535
  set-overload-bit on-startup 180
  log-adjacency-changes
  authentication-type md5 level-2
  authentication key-chain ISIS level-2
```

***leaf1:***

```leaf1
hostname leaf1
feature isis

key chain ISIS
  key 0
    key-string 7 070c285f4d06
vrf context management
  ip route 0.0.0.0/0 mgmt0 192.168.254.1

interface Ethernet1/1
  no switchport
  mtu 9216
  medium p2p
  no ip redirects
  ip address 10.2.1.0/31
  no isis hello-padding always
  isis network point-to-point
  isis authentication-type md5 level-2
  isis authentication key-chain ISIS level-2
  ip router isis UNDERLAY
  no shutdown

interface Ethernet1/2
  no switchport
  mtu 9216
  medium p2p
  no ip redirects
  ip address 10.2.2.0/31
  no isis hello-padding always
  isis network point-to-point
  isis authentication-type md5 level-2
  isis authentication key-chain ISIS level-2
  ip router isis UNDERLAY
  no shutdown

interface mgmt0
  vrf member management
  ip address 192.168.254.52/24

interface loopback0
  ip address 10.0.1.2/32
  ip router isis UNDERLAY
icam monitor scale

cli alias name wr copy run start
line console
line vty
router isis UNDERLAY
  net 49.0001.0100.0000.1002.00
  is-type level-2
  max-lsp-lifetime 65535
  set-overload-bit on-startup 180
  log-adjacency-changes
  authentication-type md5 level-2
  authentication key-chain ISIS level-2
```

***leaf2:***

```leaf2
hostname leaf2
feature isis

key chain ISIS
  key 0
    key-string 7 070c285f4d06
vrf context management
  ip route 0.0.0.0/0 mgmt0 192.168.254.1

interface Ethernet1/1
  no switchport
  mtu 9216
  medium p2p
  no ip redirects
  ip address 10.2.1.2/31
  no isis hello-padding always
  isis network point-to-point
  isis authentication-type md5 level-2
  isis authentication key-chain ISIS level-2
  ip router isis UNDERLAY
  no shutdown

interface Ethernet1/2
  no switchport
  mtu 9216
  medium p2p
  no ip redirects
  ip address 10.2.2.2/31
  no isis hello-padding always
  isis network point-to-point
  isis authentication-type md5 level-2
  isis authentication key-chain ISIS level-2
  ip router isis UNDERLAY
  no shutdown

interface mgmt0
  vrf member management
  ip address 192.168.254.53/24

interface loopback0
  ip address 10.0.1.3/32
  ip router isis UNDERLAY
icam monitor scale

cli alias name wr copy run start
line console
line vty
router isis UNDERLAY
  net 49.0001.0100.0000.1003.00
  is-type level-2
  max-lsp-lifetime 65535
  set-overload-bit on-startup 180
  log-adjacency-changes
  authentication-type md5 level-2
  authentication key-chain ISIS level-2
```

***leaf3:***

```leaf3
hostname leaf3
feature isis

key chain ISIS
  key 0
    key-string 7 070c285f4d06
vrf context management
  ip route 0.0.0.0/0 mgmt0 192.168.254.1

interface Ethernet1/1
  no switchport
  mtu 9216
  medium p2p
  no ip redirects
  ip address 10.2.1.4/31
  no isis hello-padding always
  isis network point-to-point
  isis authentication-type md5 level-2
  isis authentication key-chain ISIS level-2
  ip router isis UNDERLAY
  no shutdown

interface Ethernet1/2
  no switchport
  mtu 9216
  medium p2p
  no ip redirects
  ip address 10.2.2.4/31
  no isis hello-padding always
  isis network point-to-point
  isis authentication-type md5 level-2
  isis authentication key-chain ISIS level-2
  ip router isis UNDERLAY
  no shutdown
interface mgmt0
  vrf member management
  ip address 192.168.254.54/24

interface loopback0
  ip address 10.0.1.4/32
  ip router isis UNDERLAY
icam monitor scale

cli alias name wr copy run start
line console
line vty
router isis UNDERLAY
  net 49.0001.0100.0000.1004.00
  is-type level-2
  max-lsp-lifetime 65535
  set-overload-bit on-startup 180
  log-adjacency-changes
  authentication-type md5 level-2
  authentication key-chain ISIS level-2
```

***Проверка установки соседства ospf между spine и leaf коммутаторами:***

```isis_adj
Spine1# show isis adjacency
IS-IS process: UNDERLAY VRF: default
IS-IS adjacency database:
Legend: '!': No AF level connectivity in given topology
System ID       SNPA            Level  State  Hold Time  Interface
leaf1           N/A             2      UP     00:00:32   Ethernet1/1
leaf2           N/A             2      UP     00:00:26   Ethernet1/2
leaf3           N/A             2      UP     00:00:26   Ethernet1/3
 
Spine2# show isis adjacency
IS-IS process: UNDERLAY VRF: default
IS-IS adjacency database:
Legend: '!': No AF level connectivity in given topology
System ID       SNPA            Level  State  Hold Time  Interface
leaf1           N/A             2      UP     00:00:26   Ethernet1/1
leaf2           N/A             2      UP     00:00:32   Ethernet1/2
leaf3           N/A             2      UP     00:00:26   Ethernet1/3
```

### Примечание:

* Дополнительно сделал линк в vrf management для автоматизации управления конфигурацией коммутаторами. Не в тему курса, но все равно думаю не лишнее. Скрипты так же в папке _scripts_ репозитория.
* Сделал отдельно шаблоны jinja для интерфейсов, ospf, isis. Теперь можно выбрать с каким протоколом запустить лабу и конфигурация поностью перестроиться под isis или ospf. Те можно в один клик переключатсья между underlay настройками для тестирвония. Продолжу для остальных проткоколов реализовывать автоматизацию конфигурации.
* Отдельно написал скриптик, который преобразует ip адрес в идентификатор isis и интрегрировал его как фильтр в шаблон jinja
* Поднял рядом топологию на Arista, дополню все прошлые ДЗ на альтернативном оборудовании.

