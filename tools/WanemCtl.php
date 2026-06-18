<?php

/*
 * @sample 
 * php WanemCtl.php 192.168.31.10 set 512 512 10 20 10 10 0 0
 * このスクリプトを使う必要はなく、要は下記のjsonをUDPでEndpointに送れば良い。
 */

if($argc < 4){
    echo "Invalid Args.\n";
    exit(-1);
}

$endPointIp   = trim($argv[1]);
$action     = trim($argv[2]);
$bandUp     = (int)$argv[3];
$bandDw     = (int)$argv[4];
$delayUp    = ($argc > 5) ? (int)$argv[5] : 0;
$delayDw    = ($argc > 6) ? (int)$argv[6] : 0;
$lossUp     = ($argc > 7) ? (int)$argv[7] : 0;
$lossDw     = ($argc > 8) ? (int)$argv[8] : 0;
$disconnUp  = ($argc > 9) ? (int)$argv[9] : 0;
$disconnDw  = ($argc > 10) ? (int)$argv[10] : 0;

$endPointPort  = 10393;

$req = array( 
    "action"  => $action,  
    "bandUp"  => $bandUp,  
    "bandDw"  => $bandDw,  
    "delayUp" => $delayUp, 
    "delayDw" => $delayDw, 
    "lossUp"  => $lossUp,  
    "lossDw"  => $lossDw,  
    "disconnUp" => $disconnUp, 
    "disconnDw" => $disconnDw, 
);

$pkt  = json_encode($req);
$sock = socket_create(AF_INET, SOCK_DGRAM, SOL_UDP);
$len  = strlen($pkt);

// 受信待ちタイムアウト設定
socket_set_option($sock, SOL_SOCKET, SO_RCVTIMEO, array(
    "sec"  => 5,
    "usec" => 0,
));

$ret = socket_sendto($sock, $pkt, $len, 0, $endPointIp, $endPointPort);
if ($ret === false) {
    die("socket_sendto failed: " . socket_strerror(socket_last_error($sock)) . PHP_EOL);
}

// レスポンス受信待ち
$buf = '';
$fromIp = '';
$fromPort = 0;

$ret = socket_recvfrom($sock, $buf, 65535, 0, $fromIp, $fromPort);

if ($ret === false) {
    $err = socket_last_error($sock);
    echo "socket_recvfrom failed: " . socket_strerror($err) . PHP_EOL;
} else {
    echo "received from {$fromIp}:{$fromPort}, {$ret} bytes" . PHP_EOL;
    echo "---- response dump ----" . PHP_EOL;

    // 文字列として表示
    echo $buf . PHP_EOL;

    // JSONなら整形表示
    $json = json_decode($buf, true);
    if (json_last_error() === JSON_ERROR_NONE) {
        echo "---- json decoded ----" . PHP_EOL;
        var_dump($json);
    } else {
        echo "---- raw hex dump ----" . PHP_EOL;
        echo bin2hex($buf) . PHP_EOL;
    }
}

socket_close($sock);
    
echo "band : Up " . $bandUp . "kbps / Dw " . $bandDw . "kbps, "
    ."delay : Up " . $delayUp . "msec / Dw " . $delayDw . "msec, " 
    ."loss : Up " . $lossUp . "% / Dw " . $lossDw . "%";
