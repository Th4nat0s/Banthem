#!/usr/bin/python
import re
import urllib2
import json
import hashlib

# Fill your API KEY
api_key = '1234567890987654321'

# Fill your Password
password = 'password'

# Fill some regex to exclude false positives
excludes = ['^http://badbastogne\.be',
            '^http://www\.badbastogne\.be',
            '^http://[\S\d]{1,}\.trollprod\.(org|com)' ]

# Fill your HTTP Logs file
logs = [ './sample/users.log',
         '/var/log/apache2/badbastogne.log' ]


##### START ######
commonregex = '^.*"[\S]{1,} (.*) [\S\.\/]{1,}".*".*".*".*"$'
dateregex = '^.*\[(.*)\]'
posturl = 'http://banthem.trollprod.org/report/?id=' + api_key
UserAgent = 'BanThem/0.0'

hashpass = password
for i in range (0,512):
  hashpass = hashlib.sha256(hashpass).hexdigest()

winner = []
for log in logs:
  try:
    f = open(log,'r')
    for line in f.readlines():
      candidatef = False
      # Scan for http://
      try:
        subreg=re.search(commonregex,urllib.unquote_plus(line));
        #//phpsubreg = re.search('<\?php', urllib.unquote_plus(subreg.group(1)))
        httpsubreg = re.search('(ftp|http)://(.*)$', subreg.group(1))
        scheme = (httpsubreg.group(1))
        candidate = (httpsubreg.group(2))
        candidatef = True
      except:
        pass
      finally:
        if (candidatef == True):
          candidate = scheme+'://'+candidate
          exclusion = 0
          for exclude in excludes:
            if (re.search(exclude,candidate) <> None ):
              ##)(candidate.find(exclude) <> -1):
              exclusion = exclusion + 1
            # Got a Winner
          if (exclusion == 0):
            print candidate
            winner.append( (api_key,candidate,line) )
        else:
          try:
            if (re.search('<\?php', subreg.group(1)) <> None):
              winner.append( (api_key,candidate,line) )
              print subreg.group(1)
          except:
            pass
            
    f.close()
  except:
    print('read error %s' % log)
data=json.dumps(winner)
url= posturl+'&crc='+hashlib.sha256(data+hashpass).hexdigest()
headers = { 'User-Agent' : UserAgent  }
#try:
try: 
  req = urllib2.Request(url, data, headers)
  response = urllib2.urlopen(req)
  the_page = response.read()
  
except urllib2.HTTPError as e:
  if (e.code==401):
    print e.code
    print 'Bad password or api key'
  elif (e.code==404):
    print e.code
    print 'url not found'
  else:
    print e.code
    print 'Unexpectd Error'




