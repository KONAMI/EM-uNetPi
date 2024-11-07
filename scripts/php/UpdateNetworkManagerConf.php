<?php

/*====================================================================================*/

// Network Manager AP 更新用スクリプト

/*====================================================================================*/

if($argc < 2){ exit(-1); }

$key = $argv[1];

//$confPath = "/etc/hostapd/hostapd.conf";
$confPath = "/etc/NetworkManager/system-connections/rpi_ap.nmconnection";
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

    $confDat = "[connection]" . "\n"
        . "id=rpi_ap" . "\n"
        . "uuid=36343839-9ec7-435a-8d0c-9b0877c71a07" . "\n"
        . "type=wifi" . "\n"
        . "autoconnect=true" . "\n"
        . "interface-name=wlan0" . "\n"
        . "timestamp=" . time() . "\n"
        . "" . "\n"
        . "[wifi]" . "\n"
        . "band=bg" . "\n"
        . "channel=" . $ch2 . "\n"
        . "mode=ap" . "\n"
        . "ssid=" . $key . "\n"
        . "" . "\n"
        . "[wifi-security]" . "\n"
        . "key-mgmt=wpa-psk" . "\n"
        . "pairwise=ccmp;" . "\n"
        . "proto=rsn;" . "\n"
        . "psk=" . $key . "\n"
        . "" . "\n"
        . "[ipv4]" . "\n"
        . "address1=192.168.21.1/24" . "\n"
        . "method=shared" . "\n"
        . "" . "\n"
        . "[ipv6]" . "\n"
        . "addr-gen-mode=default" . "\n"
        . "address1=fd00:c0a8:1501::1/64" . "\n"
        . "method=shared" . "\n"
        . "" . "\n"
        . "[proxy]" . "\n"
        . "" . "\n";    
}
else {
    switch($ch){
    case 0:  $ch2 = 36; break;
    case 1:  $ch2 = 40; break;
    case 2:  $ch2 = 44; break;
    case 3:  $ch2 = 48; break;
    default: $ch2 = 36; break;
    }

    $confDat = "[connection]" . "\n"
        . "id=rpi_ap" . "\n"
        . "uuid=36343839-9ec7-435a-8d0c-9b0877c71a07" . "\n"
        . "type=wifi" . "\n"
        . "autoconnect=true" . "\n"
        . "interface-name=wlan0" . "\n"
        . "timestamp=" . time() . "\n"
        . "" . "\n"
        . "[wifi]" . "\n"
        . "band=a" . "\n"
        . "channel=" . $ch2 . "\n"
        . "mode=ap" . "\n"
        . "ssid=" . $key . "\n"
        . "" . "\n"
        . "[wifi-security]" . "\n"
        . "key-mgmt=wpa-psk" . "\n"
        . "pairwise=ccmp;" . "\n"
        . "proto=rsn;" . "\n"
        . "psk=" . $key . "\n"
        . "" . "\n"
        . "[ipv4]" . "\n"
        . "address1=192.168.21.1/24" . "\n"
        . "method=shared" . "\n"
        . "" . "\n"
        . "[ipv6]" . "\n"
        . "addr-gen-mode=default" . "\n"
        . "address1=fd00:c0a8:1501::1/64" . "\n"
        . "method=shared" . "\n"
        . "" . "\n"
        . "[proxy]" . "\n"
        . "" . "\n";        
}

file_put_contents($confPath, $confDat);

exec("nmcli connection down rpi_ap");
sleep(3); // serviceコマンドが非同期なので、適当に寝て待つ
exec("nmcli connection up rpi_ap");

?>
