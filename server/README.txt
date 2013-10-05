SQL Schema

Table CLIENT:
CLT_ID CLT_IP PASSWORD EMAIL UID CREATIONTIME LASTPUSHTIME
0001 192.168.1.4 SHA(UID+PASS) RAND(128B) thanspam@trollprod.org datetime datetim  

Table HIT_TYPE
TYPE_ID TYPE
0000 notdefined
0001 php_backdoor
0002 proxy_scan
0003 false_positive

Table HIT:
HIT_ID MURL_ID CLT_ID HIT DATETIME CODE TYPE_ID 
0002   0003    0001   GET /truc?http://machin DATEtime CODE 001

Table MURL:
M_URLID HIT_ID M_FILID
0004    http://machin 0005

Table MFILE:
M_FILID MD5 
0005 md5


