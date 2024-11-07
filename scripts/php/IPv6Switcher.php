<?php

if($argc < 2){ echo "argv[1] is Reqruied. please set 0 or 1."; exit(); }

//$settingFile = "test/cmdline.txt";
$settingFile = "/boot/firmware/cmdline.txt";
$conf = file_get_contents($settingFile);
$isIpv6Enabled = 0;
if((int)$argv[1] == 1){ $isIpv6Enabled = 1; }

$state = "ipv6.disable=";

$newConf = trim($conf); // 一旦改行をストリップ
$newConf = UpsertLine($newConf, $state, $isIpv6Enabled);

//echo "\n======================================\n";
//echo $newConf;
//echo "======================================\n";

$ret = file_put_contents($settingFile, $newConf);
if($ret === FALSE){ echo "IPv6 Setting Switch Fail.\n"; }
else              { echo "IPv6 Setting Switch Success. Please Reboot OS.\n"; }

function UpsertLine($buff, $state, $isEnabled){
    $newBuff = "";
    $isFound = strpos($buff, $state);
    if($isFound){        
        $src = $state;
        $dst = $state;
        if($isEnabled == 0){
            $src .= (string)1;
            $dst .= (string)0;
        }
        else {
            $src .= (string)0;
            $dst .= (string)1;
        }
        $newBuff = str_replace($src, $dst, $buff) . "\n";
    }
    else {
        $newBuff = $buff;
        $dst = $state;
        if($isEnabled == 0){
            $dst .= (string)0;
        }
        else {
            $dst .= (string)1;
        }
        $newBuff .= " " . $dst . "\n";        
    }
    return $newBuff;
}

?>
