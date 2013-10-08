#!/usr/bin/python

import thread
import threading
import select
import time
import subprocess
import re
import urllib2
import json
import hashlib
import urllib
import os
import datetime

# Fill your API KEY
api_key = 'ddf002e00f3176987fcdc47af55b1a2c3f8229dc3bbb83233bb4a4ad0acf06ff'

# Fill your Password
password = 'password'

# Fill some regex to exclude false positives
excludes = ['^http://badbastogne\.be',
            '^http://www\.badbastogne\.be',
            '^http://[\S\d]{1,}\.trollprod\.' ]

# Fill your HTTP Logs file
logs = [ './sample/users.log',
         '/var/log/apache2/badbastogne.log' ]


##### FUNCTION ###
##### START ######
commonregex = '^.*"[\S]{1,} (.*) [\S\.\/]{1,}".*".*".*".*"$'
dateregex = '^.*\[(.*)\]'
posturl = 'http://banthem.trollprod.org/report/?id=' + api_key
UserAgent = 'BanThem/0.0'


# Log
def dlog(chaine):
  Lock.acquire()
  print datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), 
  print chaine
  Lock.release()

# Hash pass
def init():
  global hashpass
  hashpass = password + api_key
  for i in range (0,512):
    hashpass = hashlib.sha256(hashpass).hexdigest()

def sendreport(mbuffer):
  dlog('Reporting')
  data = [datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), mbuffer]
  data=json.dumps(data)
  url= posturl+'&crc='+hashlib.sha256(data+hashpass).hexdigest()
  headers = { 'User-Agent' : UserAgent, 'Content-Type': 'application/json'  }

  #Upload data
  try: 
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
    the_page = response.read()
    dlog('Reported successfully')

  except urllib2.HTTPError as e:
    if (e.code==401):
      dlog('Error Bad password or api key ')
    elif (e.code==404):
      #print e.code
      dlog('Error url not found ')
    else:
      dlog('Reporting error')

def win(wcandidate):
  global winner
  Lock.acquire()
  winner.append(wcandidate)
  Lock.release()

def mscan(mcandidate):
  candidatef = False
  # Scan for http://
  subreg=re.search(commonregex,mcandidate);
  try:
    httpsubreg = re.search('(ftp|http)://(.*)$', urllib.unquote_plus(subreg.group(1)), re.IGNORECASE)
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
        if (re.search(exclude,candidate,) <> None ):
          exclusion = exclusion + 1
      if (exclusion == 0):
        win(mcandidate) 
    else:
      try:
        if (re.search('<\?php', subreg.group(1), re.IGNORECASE) <> None):
          win(mcandidate) 
      except:
        pass

def monitor(filename):
  dlog('Start Thread: Watching %s' % (filename))
  try:
    f = subprocess.Popen(['tail','-F',filename],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  except:
    dlog('Error Watching %s' % (filename))
    return()
  
  p = select.poll()
  p.register(f.stdout)

  while True:
    if p.poll(1):
      cand = f.stdout.readline()
      mscan(cand)
    time.sleep(0.1)

def report(name):
  global winner
  dlog('Start reporting thread')
  while True:
    if (len(winner) >= 1):
      #Lock.acquire()
      dlog('Reporting %d candidates' % (len( winner)))
      sendreport(winner)
      winner = []
      #Lock.release()
    time.sleep(60)


init()
winner = []
Lock = threading.Lock() # lock
# Start Parse thread
thread.start_new_thread( report , ('nil',))
# Start Read Threads
for log in logs:
   thread.start_new_thread( monitor, (log, ) )

while True:
  time.sleep(15)
