#!/usr/bin/python
import re
import urllib
import json

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
posturl = 'http://banthem.trollprod.org/report.php?id=' + api_key

def scan4uri(request):
  pass

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
print winner
"""subreg=re.search(dateregex,line);
urllib.urlopen(posturl,data)
winner=[]
"""
