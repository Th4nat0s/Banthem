#!/usr/bin/python

# Process the input queue
import re
import urllib2
import json
import hashlib
import urllib
import MySQLdb
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('config.cfg')

##### START ######
commonregex = '^[\S]*\s([0-9a-f\:\.]{7,})(?:\s[\S]*){2}\s\[([\d\/\w\s:+]*)]\s"([\S]{1,}\s(\S*)\s[\S\.\/]{1,})"\s\d'

logs = [ './sample/out.txt' ]


# Open database connection
db = MySQLdb.connect(config.get("sql", "server"),
	config.get("sql", "dbase"),
	config.get("sql", "user"),
	config.get("sql", "pass"))

# prepare a cursor object using cursor() method
cursor = db.cursor()

# execute SQL query using execute() method.
cursor.execute("SELECT VERSION()")

# Fetch a single row using fetchone() method.
data = cursor.fetchone()

print "Database version : %s " % data

# disconnect from server
db.close()



winner = []
for log in logs:
  try:
    f = open(log,'r')
    UID = f.readline().rstrip('\n')
    CIP = f.readline().rstrip('\n');
    data = f.readline()

	# Update la table Client si pas client ne fait rien
    print ('select CLI_ID from T_CLIENT  where UID == \''+UID+'\'')	
    CLI_ID = '1111' # fake
    
	# si pas UID ... stop, drop file, report, checker par php in
    if (CLI_ID == 'Null'): 
      break
    print ('UPDATE PUSHTIME from T_CLIENT  where CLI_ID == \''+CLI_ID+'\'')	
  
  except:
    print 'error reading report'
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
          TYPE_ID = 2 # Not scanned
          MURL = ''
          M_FILE  = phpreg.group(1)
          HITn = INJ_HIT.replace(M_FILE, '<RFI_INJ>', 1)
          if (INJ_HIT==HITn):
            HITn = INJ_HIT.replace(urllib.quote_plus(M_FILE), '<RFI_INJ>', 1) 
          INJ_HIT = HITn
          FMD5 = hashlib.md5(M_FILE).hexdigest()
          FSHA = hashlib.sha256(M_FILE).hexdigest()
          FNEAR = ''

    if (TYPE_ID<> 2):
      # Fill the malware Url Table
      print ('select from T_MURL MURL_ID where MURL == \''+MURL+'\'')	
	  # Si MURL_ID pas trouve
      print ('insert into T_MURL (MURL) VALUES '+MURL)	
      MURL_ID = 4444 
    else:
      # It's a direct injection
      # Md5 Sum the injection sauve et insert dans db si inexistant
      print ('select from T_FILE FILE_ID where FSHA == \''+FSHA+'\'')	
      print ('insert into T_FILE (FMD5, FSHA, FNEAR) VALUES (\''+FMD5+'\',\''+FSHA+'\',\''+FNEAR+'\')')	

	# Update la table injection
    print ('select from T_INJ INJ_ID where INJ_HIT == \''+INJ_HIT+'\'')	
    print ('insert into T_INJ \''+INJ_HIT+'\'')

	# Update la table IP Attanquant
    print ('select from T_IP IP_ID where IP == \''+IP+'\'')	
    print ('insert into T_IP '+IP)
	
	# Update la client IP
    print ('select from T_IP IP_ID where IP == \''+CIP+'\'')	
    print ('insert into T_IP '+CIP)

	# Uptdate Client 
    print ('select CLI_ID T_IP IP_ID where IP == \''+CIP+'\'')	
    print ('XXXXXXXXXXXXXXXXXXXXXXXXX--------------')
	# Update la table Client