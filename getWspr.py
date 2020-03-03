#!/usr/bin/python
#==============================================================================================================#
#                                                                                                              #
# getWspr                                                                                                      #
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
import traceback
import string
import time
from bs4 import BeautifulSoup
import requests
import pandas as pd


"""
Contains a function for getting wspr spots from wsprnet.org
"""

def getWspr( gwStrCallsign ):
	"""
	Takes a CALLSIGN and gets WSPR spots for that callsign from wsprnet.org
	"""

	with open("log.txt", "a") as log_file:
		log_file.write( time.ctime() + " : getWspr start\n" )

	url = 'http://wsprnet.org/olddb?mode=html&band=all&limit=50&findcall=' + gwStrCallsign + '&findreporter=&sort=date'


	try:
		r = requests.get(url)
		r.raise_for_status()

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
			log_file.write( time.ctime() + ' : some other connection error %s \n' % err )
			log_file.close()

		return 1

	data = r.text

	pd.set_option('display.expand_frame_repr', False)

	soup = BeautifulSoup(data, 'lxml')

	table = soup.find_all('table')[2]            # want third table

	rows = table.find_all('tr')[2:]      # skip first two rows

	data = {
		'dateTime' : [],
		'Call' : [],
		'Frequency' : [],
		'SNR' : [],
		'drift' : [],
		'Grid' : [],
		'powerDBM' : [],
		'powerWatts' : [],
		'reporter' : [],
		'reporterGrid' : [],
		'distanceKM' : [],
		'distanceMI' : []
		}

	try:
		# extract values and remove unicode &nbsp;
		for row in rows:
			cols = row.find_all('td')
			data['dateTime'].append( cols[0].get_text().replace(u'\xa0', "") )
			data['Call'].append( cols[1].get_text().replace(u'\xa0', "") )
			data['Frequency'].append( cols[2].get_text().replace(u'\xa0', "") )
			data['SNR'].append( cols[3].get_text().replace(u'\xa0', "") )
			data['drift'].append( cols[4].get_text().replace(u'\xa0', "") )
			data['Grid'].append( cols[5].get_text().replace(u'\xa0', "") )
			data['powerDBM'].append( cols[6].get_text().replace(u'\xa0', "") )
			data['powerWatts'].append( cols[7].get_text().replace(u'\xa0', "") )
			data['reporter'].append( cols[8].get_text().replace(u'\xa0', "") )
			data['reporterGrid'].append( cols[9].get_text().replace(u'\xa0', "") )
			data['distanceKM'].append( cols[10].get_text().replace(u'\xa0', "") )
			data['distanceMI'].append( cols[11].get_text().replace(u'\xa0', "") )

	except IndexError:

		with open("log.txt", "a") as log_file:
			log_file.write( time.ctime() + " : no wspr spots for %s\n" % gwStrCallsign )
			return 1

	spots = pd.DataFrame( data )

	# will return only the first spot from the list which is the latest spot reported by wsprnet.org
	Spot = spots['dateTime'].values[0]
	Spot = Spot + " " + spots['Call'].values[0]
	Spot = Spot + " " + spots['Frequency'].values[0]
	Spot = Spot + " " + spots['SNR'].values[0]
	Spot = Spot + " " + spots['drift'].values[0]
	Spot = Spot + " " + spots['Grid'].values[0]
	Spot = Spot + " " + spots['powerDBM'].values[0]
	#Spot = Spot + " " + spots['powerWatts'].values[0]      # commented out
	Spot = Spot + " " + spots['reporter'].values[0]
	Spot = Spot + " " + spots['reporterGrid'].values[0]
	#Spot = Spot + " " + spots['distanceKM'].values[0]      # commented out
	Spot = Spot + " " + spots['distanceMI'].values[0]

	with open("log.txt", "a") as log_file:
		log_file.write(time.ctime() + " : wspr spots collected\n")


	return Spot
