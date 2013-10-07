#!/usr/bin/python

# Process the input queue
import re
import urllib2
import json
import hashlib
import urllib
import MySQLdb
import ConfigParser


def dlog(msg):
  print ('%s' % msg)

def getid(hook):
    Result=hook.fetchone()
    if (str(Result) == 'None'): 
      return('None')
    else:
      return(str(Result[0]))


config = ConfigParser.ConfigParser()
config.read('config.cfg')

##### START ######
commonregex = '^[\S]*\s([0-9a-f\:\.]{7,})(?:\s[\S]*){2}\s\[([\d\/\w\s:+]*)]\s"([\S]{1,}\s(\S*)\s[\S\.\/]{1,})"\s\d'

logs = [ './sample/out.txt' ]

# Open database connection
db = MySQLdb.connect(config.get("sql", "server"),
	config.get("sql", "user"),
	config.get("sql", "pass"),
	config.get("sql", "dbase"))

# prepare a cursor object using cursor() method
cursor = db.cursor()

winner = []
for log in logs:
  try:
    f = open(log,'r')
    UID = f.readline().rstrip('\n')
    CIP = f.readline().rstrip('\n');
    data = f.readline()


	# Update la table Client si pas client ne fait rien
    cursor.execute('select CLT_ID from T_CLIENT where UID=%s', ( UID, ))	
    CLT_ID = getid(cursor)

	# si pas UID ... stop, drop file, report, checker par php in
    if (CLT_ID == 'Null'): 
      log('CLT_ID not found')
      break
    cursor.execute('UPDATE T_CLIENT set PUSH_TIME=now() where CLT_ID=%s', (CLT_ID,))	

  except:
    dlog ( 'error reading report')
  report = json.loads(data)
  for line in report:
    #print line
	# Scan for http://
    MURL = ''
    IP = ''
    TYPE_ID = 0 # Not scanned
    candidateF=False
    try:
      subreg=re.search(commonregex,line);
      #//phpsubreg = re.search('<\?php', urllib.unquote_plus(subreg.group(1)))
      INJ_HIT = subreg.group(3)
      M_TIME = subreg.group(2)
      IP = subreg.group(1)
      httpsubreg = re.search('((ftp|http)://(\S*))\s', urllib.unquote_plus(subreg.group(3)))
      candidate = (httpsubreg.group(1))
      candidateF = True   
    except:
      pass
    finally:
      if (candidateF==True):
        MURL = candidate
        HITn = INJ_HIT.replace(MURL, '<RFI_INJ>', 1)
        if (INJ_HIT==HITn):
          HITn = INJ_HIT.replace(urllib.quote_plus(MURL), '<RFI_INJ>', 1) 
        INJ_HIT = HITn
      else:
        phpreg = re.search('(<\?php\S*)', subreg.group(3))
        if (phpreg <> None):
          TYPE_ID = 3 # Not scanned
          MURL = ''
          M_FILE  = phpreg.group(1)
          HITn = INJ_HIT.replace(M_FILE, '<RFI_INJ>', 1)
          if (INJ_HIT==HITn):
            HITn = INJ_HIT.replace(urllib.quote_plus(M_FILE), '<RFI_INJ>', 1) 
          INJ_HIT = HITn
          FMD5 = hashlib.md5(M_FILE).hexdigest()
          FSHA = hashlib.sha256(M_FILE).hexdigest()
          FSSDEEP = ''

    if (TYPE_ID<> 3):
      # Fill the malware Url Table
      cursor.execute('select MURL_ID from T_MURL where MURL=%s' , (MURL,))	
      MURL_ID=getid(cursor)
      if (MURL_ID == 'None'): 
        dlog("insert murl")
	    # Si MURL_ID pas trouve
        cursor.execute("INSERT INTO T_MURL (MURL) values (%s)"	,( MURL,))
        MURL_ID=getid(cursor)
    else:
      # It's a direct injection
      # Md5 Sum the injection sauve et insert dans db si inexistant
      cursor.execute('select FILE_ID from T_FILE where FSHA = %s' , ( FSHA,))
      FILE_ID=getid(cursor)
      if (FILE_ID == 'None'):
        dlog("insert FILE ")
        cursor.execute('insert into T_FILE (FMD5, FSHA, FSSDEEP) VALUES (%s, %s, %s)',(FMD5, FSHA, FSSDEEP,))	
        FILE_ID=getid(cursor)
	# Update la table injection
    cursor.execute('select INJ_ID from T_INJ where INJ_HIT = %s' , (INJ_HIT,))	
    INJ_ID=getid(cursor)
    if (INJ_ID == 'None'):
      dlog("insert Injection")
      cursor.execute('insert into T_INJ (INJ_HIT) VALUES (%s) ' , (INJ_HIT,))
      INJ_ID=getid(cursor)

	# Update la table IP Attanquant
    cursor.execute('select IP_ID from T_IP where IP = %s ' , (IP, ))	
    IP_ID=getid(cursor)
    if (IP_ID == 'None'):
      dlog("insert new attaquant IP")
      cursor.execute('insert into T_IP (IP,ATT,LASTSEEN) VALUES (%s, True, now())' , (IP,))
      IP_ID=getid(cursor)
    else:
      dlog("Update IP")
      dlog('update T_IP set LASTSEEN=now(),ATT=True where IP_ID = '+IP_ID)
      cursor.execute('update T_IP set LASTSEEN=now(),ATT=True where IP_ID = %s', (IP_ID,))

	# Update la client IP
    cursor.execute('select IP_ID from T_IP where IP=%s', (CIP, ))
    IP_ID=getid(cursor)
    if (IP_ID == 'None'):
      dlog("insert new client IP")
      cursor.execute('insert into T_IP (IP,CLT,LASTSEEN) VALUES (%s, True, now())' , (CIP,))
      IP_ID=getid(cursor)
    else:
      dlog("Update IP")
      cursor.execute('update T_IP set CLT=True, LASTSEEN=now() where IP_ID = %s', (IP_ID[0],))

    # Updated Client
    cursor.execute('update T_CLIENT set PUSH_TIME=now() where CLT_ID=%s' , (CLT_ID,))
   
    # Insert HIT
    dlog('insert HIt')
    if (TYPE_ID<> 3):
      cursor.execute('insert into T_HIT (CLT_ID,INJ_ID,TYPE_ID,MURL_ID,HIT_TIME) VALUES (%s, %s, %s,%s, now())' , (CLT_ID,INJ_ID,TYPE_ID,MURL_ID,))
    else:
      cursor.execute('insert into T_HIT (CLT_ID,INJ_ID,TYPE_ID,FILE_ID,HIT_TIME) VALUES (%s, %s, %s,%s, now())' , (CLT_ID,INJ_ID,TYPE_ID,FILE_ID,))

cursor.connection.commit();
db.close()
