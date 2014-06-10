#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Silvio Katzmann'
__application__ = 'Youtube Channel download'
__version__ = 0.1


import os
from datetime import date

from http.client import HTTPSConnection as Https
from urllib.parse import urlencode

import json
import subprocess

jsonPath = os.path.join(os.path.dirname(os.path.realpath(__file__)),"config.json")

def push(event, msg):
  global config

  data = {'apikey': config["API_KEY"],
          'application': __application__,
          'event': event,
          'description': msg,
          'priority': 0}

  h = Https(config["API_DOMAIN"])

  h.request("POST",
            "/publicapi/add",
            headers={'Content-type': "application/x-www-form-urlencoded",
                     'User-Agent': __application__ + '/' + str(__version__)
                     },
            body=urlencode(data))

  response = h.getresponse()
  request_status = response.status

  if request_status == 200:
    return True
  else:
    return False


def readConfig():
  global config
  with open(jsonPath) as json_file:
    config = json.load(json_file)


def writeConfig():
  global config
  with open(jsonPath, 'w') as outfile:
    json.dump(config, outfile)

def callProcessWithChannelName(script, channel, destination):
  postCmd = [
             'python',
             '-u',
             script,
             channel,
             destination
            ]
  postProcess = subprocess.Popen(postCmd, stdout=subprocess.PIPE)
  postOut = postProcess.communicate()[0]
  print(postOut)

def download():
  for channel in config["Channels"]:
    dest = os.path.join(config["Destination"],channel["Channel"])

    if not os.path.exists(dest):
      os.makedirs(dest)

    ydlCmd = [
                'youtube-dl',
                '-ciw',
                'ytuser:'+ channel["Channel"],
                '-o', dest + os.sep + '%(title)s.%(ext)s',
                '--restrict-filenames',
                '--dateafter', channel["lastUpdate"],
                '--max-quality', 'FORMAT',
                '--write-info-json',
                '--write-thumbnail',
                '-q'
              ]

    process = subprocess.Popen(ydlCmd, stdout=subprocess.PIPE)
    output = process.communicate()[0]

    if len(output) > 0:
      push("error", output)
    else:
      channel["lastUpdate"] = date.today().strftime("%Y%m%d")
      if channel["postProcessingScript"]:
        if os.path.exists(channel["postProcessingScript"]):
          callProcessWithChannelName(channel["postProcessingScript"],
                                     channel["Channel"], dest)
        elif os.path.exists(
                  os.path.join(
                    os.path.dirname(
                      os.path.realpath(__file__)),
                    channel["postProcessingScript"])):
          callProcessWithChannelName(os.path.exists(
                                      os.path.join(
                                        os.path.dirname(
                                          os.path.realpath(__file__)),
                                        channel["postProcessingScript"]),
                                      channel["Channel"]), dest)
        else:
          push("error", "postProcessingScript %s for channel %s not found"
               %(channel["postProcessingScript"],channel["Channel"]))

if __name__ == '__main__':
  readConfig()
  download()
  writeConfig()
