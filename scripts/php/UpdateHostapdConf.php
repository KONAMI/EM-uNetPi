<?php

/*====================================================================================*/

// Hostapd更新用スクリプト

/*====================================================================================*/

if($argc < 2){ exit(-1); }

$key = $argv[1];

$confPath = "/etc/hostapd/hostapd.conf";
$confDat  = "";

$mode = (int)file_get_contents("/etc/wanem/apmode.prop");
$ch   = (int)file_get_contents("/etc/wanem/apchannel.prop");

if($mode == 0){
    switch($ch){
    case 0:  $ch2 = 1; break;
    case 1:  $ch2 = 6; break;
    case 2:  $ch2 = 11; break;
    default: $ch2 = 1; break;
    }
    
    $confDat   = "interface=wlan0" . "\n"
        . "driver=nl80211" . "\n"
        . "ssid=" . $key . "\n"
        . "hw_mode=g" . "\n"
        . "channel=" . $ch2 . "\n"
        . "macaddr_acl=0" . "\n"
        . "auth_algs=1" . "\n"
        . "wpa=2" . "\n"
        . "wpa_passphrase=" . $key . "\n"
        . "wpa_key_mgmt=WPA-PSK" . "\n"
        . "wpa_pairwise=TKIP" . "\n"
        . "rsn_pairwise=CCMP" . "\n"
        ;
    exec("unlink /usr/sbin/hostapd");    
    exec("ln -s /usr/local/sbin/hostapd.24 /usr/sbin/hostapd");    
}
else {
    switch($ch){
    case 0:  $ch2 = 36; break;
    case 1:  $ch2 = 40; break;
    case 2:  $ch2 = 44; break;
    case 3:  $ch2 = 48; break;
    default: $ch2 = 36; break;
    }
    $confDat   = "interface=wlan0" . "\n"
        . "ssid=" . $key . "\n"
        . "hw_mode=a" . "\n"
        . "channel=" . $ch2 . "\n"
        . "macaddr_acl=0" . "\n"
        . "auth_algs=1" . "\n"
        . "wpa=2" . "\n"
        . "wpa_passphrase=" . $key . "\n"
        . "wpa_key_mgmt=WPA-PSK" . "\n"
        . "wpa_pairwise=TKIP" . "\n"
        . "rsn_pairwise=CCMP" . "\n"
        ;    
    exec("unlink /usr/sbin/hostapd");    
    exec("ln -s /usr/local/sbin/hostapd.5 /usr/sbin/hostapd");    
}

file_put_contents($confPath, $confDat);

exec("service hostapd stop");
sleep(5); // serviceコマンドが非同期なので、適当に寝て待つ
exec("killall -9 hostapd -q");
exec("/usr/sbin/hostapd -B /etc/hostapd/hostapd.conf");

?>