SQL Schema

Table T_CLIENT:  definit le client, 
CLT_ID IP_ID CLT_CRD             EMAIL     UID               CRT_TIME PUSH_TIME MGT_TIME Token
1111   7778  512*SHA256(UID+Pwd) gus@a.org sha256(time+rand) datetime datetime  datetime rand

Table T_TYPE : Definit l'attaque qui a eu lieu
TYPE_ID TYPE
0001 	toreview
0002 	false_positive
0003 	direct php execution
0004 	php_backdoor
0005 	php_scouting
0006 	proxy_scan

Table T_HIT: link l'attaque complete, MURL_ID peut etre a null 
HIT_ID CLT_ID INJ_ID TYPE_ID MURL_ID MFIL_ID HIT_TIME  
2222   1111   3333   0003    4444    6666    datetime

Table T_INJ : Definit l'injection utilisee
INJ_ID INJ_HIT 
3333   'GET /wp-content/themes/newsworld/scripts/timthumb.php?src=<XX_INJ_XX> HTTP/1.1'

Table T_MURL:
MURL_ID MURL
4444    http://machin 

Table T_FILE -> Saved on disk
FILE_ID FSHA  FMD5 SSDEEP
6666    SHA   MD5  A$\\RE 

Table T_IP : Table avec les ip des attaquant
 -> ATT injecteur, BCKD hosteur malware, CLT Client
IP_ID IP          ATT   BCKD  CLT   FIRSTSEEN LAST_SEEN 
7777  192.168.1.1 true  false false datetime  datetime 
7778  192.168.1.2 false false true  datetime  datetime 
