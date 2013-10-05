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
print ('DATA\n');
//$body2 = http_get_request_body();
$body = @file_get_contents('php://input');
		print ('fid ormatok');
print $body;
print(file_get_contents('php://input'));

// Validate the CRC
if(isset($_GET["crc"])) {
	$crc = $_GET["crc"]; 
} else {
	invalid();
}

// Write the data to the Queue

?>
