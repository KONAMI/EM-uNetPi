一から構築する手順
==================================================================================================

諸注意
--------------------------------------------------------------------------------------------------

RaspberryPiとLinuxの知識がある程度あることを前提に記述をします。<br />
不明な点等がある場合、まずは、一般的な技術文献をあたってください。

Raspberry Pi の初期設定
--------------------------------------------------------------------------------------------------

### 初期イメージ用意

- 以下のバージョンの 「RASPBIAN STRETCH LITE」 のイメージファイルを [RaspberryPi公式ページ](https://www.raspberrypi.org) からダウンロードし、SDカードに焼き、本体に挿入します。

#### 使用するOSのバージョン

- Version:June 2018
- Release date:2018-06-27
- Kernel version:4.14

> カーネルのバージョンが異なったりすると、正常に動作しない可能性が高いので、必ず指定のバージョンを使用すること。

### OSの設定

#### raspi-configで設定変更

デフォルトのpiユーザでログイン、下記コマンドで設定画面を呼び出し、

- SSHログインを有効にする
- SPIを有効にする
- Host名を任意の名前に変更する

```
$ sudo raspi-config
```

#### ユーザ設定

下記のように作業用のユーザを作成、sudo権限付与する。
これ以降は、作成したユーザでsshログインして作業を進める。

```
$ sudo adduser user
$ sudo gpasswd -a user sudo
```

#### ミドルウェア諸々追加

```
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install screen
$ sudo apt-get install rsync
$ sudo apt-get install git
$ sudo apt-get install php
$ sudo apt-get install python-dev
$ sudo apt-get install python-pip
$ sudo pip install --upgrade pip
$ sudo pip install requests
$ sudo apt-get install bc
$ sudo apt-get install libnl-genl-3-dev
$ sudo apt-get install libssl-dev
```

### Networkの設定

#### /etc/network/interfaces.d/eth0

WAN側の設定

```
auto eth0
allow-hotplug eth0
iface eth0 inet dhcp
dns-nameservers 1.1.1.1
```

#### /etc/network/interfaces.d/eth1

管理用/APIMode用の固定アドレス。

```
iface eth1 inet static
address 192.168.31.10
netmask 255.255.255.0
```

#### /etc/network/interfaces.d/eth2

LAN側（有線）の設定

```
auto eth2
iface eth2 inet static
address 192.168.21.1
netmask 255.255.255.0
```

#### /etc/network/interfaces.d/wlan0

LAN側（無線）の設定

```
allow-hotplug wlan0
iface wlan0 inet static
address 192.168.20.1
netmask 255.255.255.0
```

#### /etc/dhcpcd.conf

末尾に追加

```
interface eth0
noipv4

interface eth1
noipv4

interface eth2
noipv4

interface wlan0
noipv4
```

### APの設定

#### 2.4GHz向けAPの準備

```
$ sudo apt-get install hostapd
$ sudo cp /usr/sbin/hostapd /usr/local/sbin/hostapd.24
$ sudo chmod +x /usr/local/sbin/hostapd.24
```

#### 5GHz向けAPの準備

```
$ wget https://w1.fi/releases/hostapd-2.6.tar.gz
$ tar -zxf hostapd-2.6.tar.gz
$ cd hostapd-2.6/hostapd
$ cp defconfig .config
$ echo CONFIG_LIBNL32=y >> .config
$ make
$ sudo mv hostapd /usr/local/sbin/hostapd.5
$ sudo chmod +x /usr/local/sbin/hostapd.5
```

#### 5GHz向けドングルのドライバ準備

```
$ sudo wget "https://raw.githubusercontent.com/notro/rpi-source/master/rpi-source" -O /usr/bin/rpi-source
$ sudo chmod +x /usr/bin/rpi-source
$ sudo rpi-source --skip-gcc
$ git clone https://github.com/abperiasamy/rtl8812AU_8821AU_linux.git
$ cd rtl8812AU_8821AU_linux
```

MakefileのPlatform部分を下記のように変更

```
CONFIG_PLATFORM_I386_PC = n
CONFIG_PLATFORM_ARM_RPI = y
```

そして、ビルド、インストール

```
$ sudo make
$ sudo make install
$ sudo modprobe -a rtl8812au
```

### NAT等の設定

#### DHCPサーバの設定

```
sudo apt-get install isc-dhcp-server
sudo update-rc.d isc-dhcp-server enable
```

/etc/dhcp/dhcpd.conf の末尾に追加

```
ping-check true;

subnet 192.168.20.0 netmask 255.255.255.0 {
authoritative;
option routers 192.168.20.1;
option broadcast-address 192.168.20.255;
option subnet-mask 255.255.255.0;
option domain-name "wanem-02";
option domain-name-servers 8.8.8.8,8.8.4.4;
default-lease-time 600;
max-lease-time 7200;
range 192.168.20.101 192.168.20.254;
}

subnet 192.168.21.0 netmask 255.255.255.0 {
authoritative;
option routers 192.168.21.1;
option broadcast-address 192.168.21.255;
option subnet-mask 255.255.255.0;
option domain-name "wanem-02";
option domain-name-servers 8.8.8.8,8.8.4.4;
default-lease-time 600;
max-lease-time 7200;
range 192.168.21.101 192.168.21.254;
}
```

/etc/default/isc-dhcp-server のインターフェース指定を下記のように修正

```
INTERFACESv4="wlan0 eth2"
```

#### forwardingの設定

/etc/sysctl.conf の下記コメントアウトを外す

```
# net.ipv4.ip_forward=1
```

### タッチパネルの設定

```
sudo apt-get install fbi 
git clone https://github.com/swkim01/waveshare-dtoverlays.git
sudo cp waveshare-dtoverlays/waveshare35a-overlay.dtb /boot/overlays/
```

さらに

/boot/config.txt の dtparam=spi=on の次あたりに

```
dtoverlay=waveshare35a:rotate=90,swapxy=1 
```

を追加

### その他の設定

自動ログイン設定

/lib/systemd/system/getty@.service の

```
ExecStart=-/sbin/agetty --noclear %I $TERM
```

を

```
ExecStart=-/sbin/getty/ --noclear -a pi %I $TERM
```

へ変更。

また、スプラッシュスクリーンの設定で、 /etc/rc.local の exitの手前に追加

```
fbi -d /dev/fb1 -T 1 -noverbose -a /home/pi/EM-uNetPi/misc/textures/Splash.jpg
```

上の方の

```
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"
fi  
```

はコメントアウト

### 回線エミュレーターの設定

```
cd /home/pi
git clone https://github.com/KONAMI/EM-uNetPi.git
cd EM-uNetPi
git submodule update --init --recursive
sudo make prop
```

起動後に実行する処理を /home/pi/.bash_profile に追加

```
sudo iptables-restore < /etc/iptables.ipv4.nat
route del -net default gw 192.168.31.1 eth1
sudo python EM-uNetPi/Wanem.py
```

最後にリブートをして、タッチパネルに操作コンソールが表示されれば構築完了。

> キーボード等を接続している場合、リブート前に抜いてください。
