<?php

/*
 * @sample 
 * php WanemCtl.php 192.168.31.10 512 512 10 20 10 10 0 0
 * このスクリプトを使う必要はなく、要は下記のjsonをUDPでEndpointに送れば良い。
 */

if($argc < 4){
    echo "Invalid Args.\n";
    exit(-1);
}

$endPointIp   = trim($argv[1]);
$bandUp     = (int)$argv[2];
$bandDw     = (int)$argv[3];
$delayUp    = ($argc > 4) ? (int)$argv[4] : 0;
$delayDw    = ($argc > 5) ? (int)$argv[5] : 0;
$lossUp     = ($argc > 6) ? (int)$argv[6] : 0;
$lossDw     = ($argc > 7) ? (int)$argv[7] : 0;
$disconnUp  = ($argc > 8) ? (int)$argv[8] : 0;
$disconnDw  = ($argc > 9) ? (int)$argv[9] : 0;

$endPointPort  = 10393;

$req = array( 
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

socket_sendto($sock, $pkt, $len, 0, $endPointIp, $endPointPort);
socket_close($sock);
    
echo "band : Up " . $bandUp . "kbps / Dw " . $bandDw . "kbps, "
    ."delay : Up " . $delayUp . "msec / Dw " . $delayDw . "msec, " 
    ."loss : Up " . $lossUp . "% / Dw " . $lossDw . "%";
