#!/usr/bin/python
#==============================================================================================================#
#                                                                                                              #
# getLastAprsPositonTime ( TargetCallsign, apiKey )                                                            #
#                                                                                                              #
# Copyright (C) 2019 Graham Collins ve3gtc                                                                     #
#                                                                                                              #
# This program is free software; you can redistribute it and/or modify                                         #
# it under the terms of the GNU General Public License as published by                                         #
# the Free Software Foundation; either version 2 of the License, or                                            #
# (at your option) any later version.                                                                          #
#                                                                                                              #
# This program is distributed in the hope that it will be useful,                                              #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                                               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                                #
# GNU General Public License for more details.                                                                 #
#                                                                                                              #
# You should have received a copy of the GNU General Public License along                                      #
# with this program; if not, write to the Free Software Foundation, Inc.,                                      #
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.                                                  #
#                                                                                                              #
#==============================================================================================================#
#
# if not already installled, use pip to install the following
#
#    pip install beautifulsoup
#    pip install bs4
#    pip install lxml
#    pip install pandas
#    pip install requests
#
#==============================================================================================================#

import sys
import string
import requests
import json
import time

"""
Contains a function for getting last aprs position time from aprs.fi
"""

def getLastAprsPositionTime ( targetCallsign, apiKey ) :

	# example result for nothing found:
	#
	# {	"command":"get",
	#	"result":"ok",
	#	"what":"loc",
	#	"found":0,
	#	"entries":[]
	#	}
	#
	# example result when something is found:
	#
	# {	"command":"get",
	#	"result":"ok",
	#	"what":"loc",
	#	"found":1,
	#	"entries":[{
	#		"class":"a",
	#		"name":"W5KUB-11",
	#		"type":"l",
	#		"time":"1579029422",
	#		"lasttime":"1579029422",
	#		"lat":"35.06500",
	#		"lng":"-89.71933",
	#		"altitude":30.1752,
	#		"course":55,
	#		"speed":0,
	#		"symbol":"\/O",
	#		"srccall":"W5KUB-11",
	#		"dstcall":"APLIGA",
	#		"comment":"023TxC 18.80C 1003.10hPa 4.62V 07S http:\/\/www.w5kub.com",
	#		"status":"LightAPRS-W SBS=13",
	#		"status_lasttime":"1579025277",
	#		"path":"WIDE1-1,WIDE2-1,qAR,KA7UEC-10"
	#		}]
	#	}
	#

	url = 'https://api.aprs.fi/api/get?name=' + targetCallsign + '&what=loc&apikey=' + apiKey + '&format=json'

	try:
		aprsData = requests.get(url)
		aprsData.raise_for_status()

	except requests.exceptions.HTTPError as errh:

		with open( 'log.txt', 'a' ) as log_file:
			log_file.write( time.ctime() + ' : http error %s \n' % errh)
			log_file.close()

		return 1

	except requests.exceptions.ConnectionError as errc:

		with open( 'log.txt', 'a' ) as log_file:
			log_file.write( time.ctime() + ' : error connecting %s \n' % errc)
			log_file.close()

		return 1

	except requests.exceptions.Timeout as errt:

		with open( 'log.txt', 'a' ) as log_file:
			log_file.write( time.ctime() + ' : connection timeout %s \n' % errt)
			log_file.close()

		return 1

	except requests.exceptions.RequestException as err:

		with open( 'log.txt', 'a' ) as log_file:
			log_file.write( time.ctime() + ' : some other connection error %s \n' % err)
			log_file.close()

		return 1

	aprsData_dict = json.loads(aprsData.text)

	if ( aprsData_dict['result'] == 'fail' ) :
		with open( 'log.txt', 'a' ) as log_file:
			log_file.write( time.ctime() + ' : aprs.fi query failed : %s\n' % aprsData_dict['description'] )
			log_file.close()

		return 1


	if ( aprsData_dict['found'] == 0 ) :
		with open( 'log.txt', 'a' ) as log_file:
			log_file.write( time.ctime() + ' : nothing found for  %s\n' % targetCallsign )
			log_file.close()

		return 1

	for entry in aprsData_dict['entries'] :

		return entry['lasttime']
