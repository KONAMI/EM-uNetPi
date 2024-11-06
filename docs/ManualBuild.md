一から構築する手順 for Raspberry Pi 5
==================================================================================================

諸注意
--------------------------------------------------------------------------------------------------

RaspberryPiとLinuxの知識がある程度あることを前提に記述をします。<br />
不明な点等がある場合、まずは、一般的な技術文献をあたってください。

また、最新版では Raspberry Pi 5 を前提にした記述になっています。

Raspberry Pi の初期設定
--------------------------------------------------------------------------------------------------

### 組み立て

ハードウェアのパーツを揃えたら、以下の動画にしたがって、組み立てます。

#### 動画

// TBD

#### USBポートへの接続について

今回使う Raspberry Pi OS は、USB制御（xhci）まわりに不具合があるのか、いくつかのパーツを挿すポートによっては、うまく動きません。

- 有線LAN アダプタ => USB2ポート（青くないポート）

- 無線LAN ドングル => USB3ポート（青いポート）

に接続してください。間違えると、OS起動中にUSBデバイスのリセットループにハマって起動しません。（起動することもありますが、おそらくUSB機器が正常に認識されていないため、うまく動きません）

また、電源アダプタによる出力が安定していない場合、USB機器がうまく認識されないことも確認しています（3V5Aアダプタで妥協していると起きがち）。デバイスがうまく認識されていないと疑わしい時は

```bash
$ lsusb
```

を実行して、適切に認識されているか、確認してください。

### 初期イメージ用意

- 以下のバージョンの 「Raspberry Pi OS Lite」 のイメージファイルを [RaspberryPi公式ページ](https://www.raspberrypi.com/software/) からダウンロードし、SDカードに焼き、本体に挿入します。

#### 使用するOSのバージョン

- Raspberry Pi OS Lite

  - Release date: July 4th 2024

  - System: 64-bit

  - Kernel version: 6.6

  - Debian version: 12 (bookworm)

  - Size: 432MB

> カーネルのバージョンが異なったりすると、正常に動作しない可能性が高いので、必ず指定のバージョンを使用すること。

### OSの設定

#### 初回起動

昔のバージョンと違って、起動時にユーザ作成が要求されるため「pi」というユーザで作成してください（オートログインの設定を後で行うので、パスワードは任意でOK）。

> 提供するイメージの pi ユーザの passwordは、以前のバージョンと同じ「raspberry」となっています。適宜変更してください。

異なるユーザ名で作成した場合、スクリプトを一部書き換える必要が出てくるので、どうしても変えたい方は合わせて追加修正を行うようにしてください。

#### raspi-configで設定変更

ユーザ設定後、raspi-configで以下の項目を設定し再起動してください。

- SSHログインを有効にする

- SPIを有効にする
- Host名を任意の名前に変更する
- Boot オプションから Auto Login を有効にする

```bash
$ sudo raspi-config
```

以後の作業はsshで行なって大丈夫です。

#### 作業用ユーザ設定

下記のように作業用のユーザを作成、sudo権限付与する。
これ以降は、作成したユーザでsshログインして作業を進める。

```bash
$ sudo adduser user
$ sudo gpasswd -a user sudo
```

> 提供するイメージの user ユーザの password は「password」になっています。適宜変更してください。

#### ミドルウェア諸々追加

```bash
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install screen
$ sudo apt-get install rsync
$ sudo apt-get install git
$ sudo apt-get install php
$ sudo apt-get install python-dev-is-python3
$ sudo apt-get install python3-pip
$ sudo apt-get install bc
$ sudo apt-get install libnl-genl-3-dev
$ sudo apt-get install libssl-dev
$ sudo apt-get install conntrack 
$ sudo apt-get install iptables
$ sudo apt-get install iptables-persistent 
$ sudo apt-get install radvd
$ sudo apt-get install radvdump
```

iptablesのあたりで現在のルールを保存するか訊かれますが、任意で答えて問題ありません。

radvd は自動起動設定が有効にされてしまうのは厄介なので

```bash
$ sudo systemctl disable radvd
```

として、自動起動を無効化しておいてください。

### リポジトリからソースの取得・必要なリソース生成

EM-uNetPiのリポジトリをCloneし

```bash
$ cd /home/pi
$ git clone https://github.com/KONAMI/EM-uNetPi.git
$ cd EM-uNetPi
$ git submodule update --init --recursive
$ sudo make setup
```

###  各種デバイス・ドライバのセットアップ

#### タッチパネルドライバのビルド&セットアップ

```bash
$ sudo apt-get install fbi 
$ git clone https://github.com/swkim01/waveshare-dtoverlays.git
```

リポジトリのモジュールはRaspberry Pi 5 に対応していないので、Raspberry Pi  5 環境でリビルドする必要あり

```
$ cd waveshare-dtoverlays
$ make clean all
$ sudo cp waveshare35a.dtbo /boot/overlays/
```

最後に

/boot/firmware/config.txt の dtparam=spi=on の次あたりに

```
dtoverlay=waveshare35a:rotate=90,swapxy=1 
```

を追加して、再起動後、タッチパネルにコンソール画面が描画されていれば無事セットアップ完了です。

> 同じ WaveShare の 3.5inch_RPi_LCD_(A) を組み込んだタッチパネルであっても、モノによって結線が違うことがあるので、rotateの回転角度は環境によって 90 or 270 で適宜書き換えてください。

一応確認のために、

```bash
$ hexdump /dev/input/event1
```

と打った後に適当に画面をタップして、イベントが拾えているか確認を奨励。

> もし、タップしてもなにも表示されない場合、event1 を event0 や event2 に変更して検証。それで拾えた場合は、リポジトリのソースをそれに合わせて修正する必要あり。
>
> 大体、キーボードやその他の不要なデバイスを繋ぎっぱなしが原因でズレるので、余計なものを外して再起動すると、想定通りの event1 で拾えるようになるはず。

#### 無線LANアダプタのビルド&セットアップ

相変わらず本体の無線LANチップが貧弱で、そのままAP化するとWANエミュレートに不都合な無線品質になるため、外部の無線LANアダプタを使います。

まずは、オンボードの無線LANデバイスを無効化します。

/etc/modprobe.d/raspi-blacklist.conf　に下記を追記して再起動すると無効化されます。

```
blacklist brcmfmac
blacklist brcmutil
```

再起動後に

```bash
$ ip addr
```

と打って、wlan0のインターフェースが消えていればOK。

その後、ドライバをビルドします。

```
git clone https://github.com/morrownr/rtl8852bu.git
cd rtl8852bu
make
make install
```

再起動後に

```bash
$ ip addr
```

と打って、wlan0のインターフェースが現れていればOK。

### Networkの設定

最新のRaspberry Pi OS では dhcpd, interface.d を使った設定からNetworkManagerを使った方式に変わっているので、従来とは大きく設定手順が異なる。

またこれに合わせて、無線APを構築する方法もhostapdを使わないものに変わっているので要注意。

#### 下準備

ここまでの手順をこなしていれば問題ないと思いますが、

```bash
$ ip addr
```

を実行して、eth0, eth1, eth2, wlan0 がそれぞれ認識されていることを確認しましょう。

出てこない場合、供給電力が足りていないか、接続を間違えているか、パーツが破損しています。

#### connection 設定（有線）

メトリクスを明示指定しないと、意味不明な優先順番になる可能性があるので、明示指定

```bash
$ sudo nmcli connection modify "Wired connection 1" ipv4.route-metric 100
$ sudo nmcli connection modify "Wired connection 2" ipv4.route-metric 200
$ sudo nmcli connection modify "Wired connection 3" ipv4.route-metric 300
$ sudo nmcli connection modify "Wired connection 1" connection.autoconnect yes
$ sudo nmcli connection modify "Wired connection 2" connection.autoconnect yes
$ sudo nmcli connection modify "Wired connection 3" connection.autoconnect yes
```

LAN側のポートの設定をする

```bash
$ sudo nmcli connection modify "Wired connection 2" ipv4.addresses "192.168.20.1/24"
$ sudo nmcli connection modify "Wired connection 2" ipv4.method manual
$ sudo nmcli connection modify "Wired connection 2" ipv6.addresses "fd00:c0a8:1401::1"
$ sudo nmcli connection modify "Wired connection 2" ipv6.method manual
$ sudo nmcli connection up "Wired connection 2"
```

管理ポートの設定をする

```bash
$ sudo nmcli connection modify "Wired connection 3" ipv4.addresses "192.168.31.67/24"
$ sudo nmcli connection modify "Wired connection 3" ipv4.method manual
$ sudo nmcli connection up "Wired connection 3"
```

最後に Netowork Manager を再起動

```bash
$ sudo systemctl restart NetworkManager
```

#### connection設定（無線）

まず、初期設定を行います。

SSID・パスワード含む細かい設定は、EM-uNetPiのメインプロセス設定後、起動時に自動上書きされるので、今は気にしなくてよいです。

```bash
$ sudo nmcli connection add type wifi ifname wlan0 con-name rpi_ap autoconnect yes ssid wanem-xxxxxx 802-11-wireless.mode ap 802-11-wireless.band a 802-11-wireless.channel 48 ipv4.method shared ipv4.address 192.168.21.1/24 ipv6.method shared ipv6.address fd00:c0a8:1501::1/128 wifi-sec.key-mgmt wpa-psk wifi-sec.pairwise ccmp wifi-sec.proto rsn wifi-sec.psk "wanem-xxxxxx"
$ sudo nmcli connection up rpi_ap
$ sudo nmcli connection modify rpi_ap autoconnect yes
```

最後に Netowork Manager を再起動

```bash
$ sudo systemctl restart NetworkManager
```

#### IPv6の切り替え（任意）

IPv6を無効にしたい場合下記を実行し、再起動する。

```bash
$ cd /home/pi/EM-uNetPi/scripts/php/
$ sudo php IPv6Switcher.php 1
```

この切り替えは、EM-uNetPi起動後にタッチパネルからの操作（Setting）からでも行うことが出来ます。

### NAT等の設定（IPv4）

#### DHCPサーバの設定

```
sudo apt-get install isc-dhcp-server
```

インストール後に起動にこけるが、設定ファイルを適切に構成してないせいなので、無視して良い。

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
INTERFACESv4="wlan0 eth1"
```

この状態で起動して問題なければOK

```
$ sudo systemctl start isc-dhcp-server.service
```

#### forwardingの設定

/etc/sysctl.conf の下記コメントアウトを外す

```
# net.ipv4.ip_forward=1
# net.ipv6.conf.all.forwarding=1
```

### NAT等の設定（IPv6）※ experimental

NAT66の設定を行います。

必要な追加設定を行いますが、起動後に「Settings > IP/NAT」の IPv6 Mode を NAT66 にしない限り有効にはなりません。

NAT66実装に関しては、こちらの [実装に至った経緯](NAT66Info.md) も併せて参照ください。

#### アドレス設計について

/64 環境での利用を想定しているため、ULAの fd00::/8 空間を使用します。

一部プラットフォーム/アプリケーションでは、ULAを用いたNAT66環境下で、IPv6通信がうまく行えない可能性があるので、ご留意ください。

#### radvd の設定

コンフィグファイルを /etc/radvd.conf として、下記の通り定義します。

```
interface eth1 {

    AdvSendAdvert on;
    MinRtrAdvInterval 3;
    MaxRtrAdvInterval 10;
    AdvDefaultPreference high;

    prefix fd00:c0a8:1401::/64
    {
        AdvOnLink on;
        AdvAutonomous on;
        AdvRouterAddr off;
    };

    RDNSS 2001:4860:4860::8888 2001:4860:4860::8844 {
        AdvRDNSSLifetime 3600;
    };
};

interface wlan0 {

    AdvSendAdvert on;
    MinRtrAdvInterval 3;
    MaxRtrAdvInterval 10;
    AdvDefaultPreference high;

    prefix fd00:c0a8:1501::/64
    {
        AdvOnLink on;
        AdvAutonomous on;
        AdvRouterAddr off;
    };

    RDNSS 2001:4860:4860::8888 2001:4860:4860::8844 {
        AdvRDNSSLifetime 3600;
    };
};
```

### その他の設定

#### 起動画面設定

スプラッシュスクリーンの設定で、 /etc/rc.local の exitの手前に追加

```
sudo fbi -d /dev/fb0 -T 1 -noverbose -a /home/pi/EM-uNetPi/misc/textures/Splash.jpg
```

上の方の

```
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"
fi  
```

はコメントアウト

#### 画面出力抑制（任意）

タッチパネル側の描画に出てきてしまう余計な描画を抑制したい場合は /boot/firmware/cmdline.txt の rootwait の後に下記を追加。（末尾は ipv6.disable=1 or 0 のままにすること）

```
vt.global_cursor_default=0 quiet logo.nologo
```

### 自動ログインユーザの起動時の処理を設定

~/.bash_profile を作成し、以下を記載

```bash
$ sudo nmcli connection up "Wired connection 2"
$ sudo nmcli connection up "Wired connection 3"
$ sudo route del -net default gw 192.168.31.1 eth2
$ sudo iw wlan0 set power_save off
$ sudo systemctl stop isc-dhcp-server.service
$ sudo systemctl start isc-dhcp-server.service
$ sudo iptables-restore < /etc/iptables.ipv4.nat
$ sudo python EM-uNetPi/Wanem.py 1>/dev/null 2>/dev/null
```

最後にリブートをして、タッチパネルに操作コンソールが表示されれば構築完了。

> キーボード等を接続している場合、リブート前に抜いてください。
