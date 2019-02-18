<?php
// 参考：https://qiita.com/plageoj/items/3df087999d550338e2b8
$line=array(
    'accessToken' => getenv("LINE_CHANNEL_ACCESS_TOKEN"),
    'channelSecret' => getenv("LINE_CHANNEL_SECRET")
);

$request = file_get_contents("php://input");
$json = json_decode($request,true);

//SIGNATURE CHECK
$signature = $_SERVER['HTTP_X_LINE_SIGNATURE'];
if($signature!==base64_encode(hash_hmac('sha256',$request,$line['channelSecret'],true))){
    error_log('Signature check failed');
    http_response_code(400);
    exit(0);
}
//PASSED!
$image_base="https://chart.apis.google.com/chart?cht=tx&chs=50&chl=";

foreach($json['events'] as $e){
    $tex = '';
    switch($e['type']){
        case 'message':
        if($e['message']['type'] === 'text'){
            switch($e['source']['type']){
                case 'user':
                $tex = $e['message']['text'];
                break;
                case 'room':    //「招待」を使ったトーク
                case 'group':   //グループを作成したトーク
                if(stripos($e['message']['text'],'t:') === 0){
                    $tex = substr($e['message']['text'],2);
                }
                break;
            }
        }
        break;
    }

    $header = array(
        'Content-Type: application/json',
        'Authorization: Bearer ' . $line['accessToken']
    );

    //SEND IT!
    if($tex !== ''){
        $url = $image_base . urlencode('\displaystyle '.$tex);
        $body = array(
            'replyToken' => $e['replyToken'],
            'messages' => array(
                array(
                    'type' => 'image',
                    'originalContentUrl' => $url,
                    'previewImageUrl' => $url
                )
            )
        );
        $context = stream_context_create(array(
            'http' => array(
                'method' => 'POST',
                'header' => implode("\r\n",$header),
                'content' => json_encode($body)
            )
        ));

        $result = file_get_contents("https://api.line.me/v2/bot/message/reply",false,$context);
        
        if (strpos($http_response_header[0], '400') === false) {
        http_response_code(200);
        error_log("Request failed: " . $result);
        }
        if (strpos($http_response_header[0], '200') === false) {
        http_response_code(500);
        error_log("Request failed: " . $result);
        }
    }
}