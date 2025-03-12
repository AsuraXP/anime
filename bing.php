<?php
$conn = mysqli_connect("localhost", 'ryuk_ryuk' , 'Shashank2006@@', "ryuk_ryuk") or die("Connection fail");
require_once 'vendor/autoload.php';


$id = $_GET['id'];

$googlecheck = mysqli_query($conn, "SELECT * FROM `google` WHERE anime_id = '$id'");
$googlecheck = mysqli_fetch_assoc($googlecheck);
if(empty($googlecheck['anime_id'])){
   
    $client = new Google_Client();

    // service_account_file.json is the private key that you created for your service account.
    $client->setAuthConfig('account1.json');
    $client->addScope('https://www.googleapis.com/auth/indexing');
    
    // Get a Guzzle HTTP Client
    $httpClient = $client->authorize();
    $endpoint = 'https://indexing.googleapis.com/v3/urlNotifications:publish';
    
    // Define contents here. The structure of the content is described in the next step.
    $content = '{
      "url": "'.$id.'",
      "type": "URL_UPDATED"
    }';
    
    $response = $httpClient->post($endpoint, [ 'body' => $content ]);
    $status_code = $response->getStatusCode();
  
    
    if ($status_code === 200) {
        //echo "Failed to submit the request.";
        mysqli_query($conn,"INSERT INTO `google` (anime_id) VALUES('$id')");
    } else {
        
    }
}else{
    //
}



