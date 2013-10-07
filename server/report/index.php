<?php

// End with HTTP Denied
function invalid() {
	header('HTTP/1.0 401 Unauthorized');
	exit(0);
}

// Validate the Api Key
function keyexist($lapi_key) {
	if ($lapi_key == "ddf002e00f3176987fcdc47af55b1a2c3f8229dc3bbb83233bb4a4ad0acf06ff" ) {
		return (true);
	} else {
		return (false);
 	}
}

// ****************************************
// Main Code
$base = 'in/';
$password = 'password';
$crc = 'NULL';
$api_key  = 'NULL';

// Validate the api_key
if(isset($_GET["id"])) { // Validate presence
	if (preg_match("/^([a-f0-9]){64}$/", $_GET["id"] )) { // Validate Format
		if (keyexist($_GET["id"])) { // Validate api_key existence
			$api_key = $_GET["id"];
		}
	}
} 
if ($api_key == 'NULL' ) { // if api_key is bad, stop 
	invalid();
}

// Get the content
$body = @file_get_contents('php://input');

// Validate the CRC
if(isset($_GET["crc"])) {
	$crc = $_GET["crc"]; 
	
} else {
	invalid();
}

// Write the data to the Queue
$name = $base.md5(rand(0,100000).microtime(true));
$fp = fopen($name, 'w');
fwrite($fp , $api_key.chr(0x0a));
fwrite($fp , $_SERVER["REMOTE_ADDR"].chr(0x0a));
fwrite($fp , $body);
print ('Data Recorded');
fclose($name);
?>
