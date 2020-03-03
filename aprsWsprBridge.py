#!/usr/bin/python
#==============================================================================================================#
#                                                                                                              #
# aprsWsprBridge.py - simple python script to collect WSPR spots and upload a position to APRS                 #
#                                                                                                              #
# Copyright (C) 2019 Graham Collins ve3gtc                                                                     #
#                                                                                                              #
# This program is free software; you can redistribute it and/or modify                                         #
# it under the terms of the GNU General Public License as published by                                         #
# the Free Software Foundation; either version 2 of the License, or                                            #
# (at your option) any later version.                                                                          #
#                                                                                                              #
#  http://www.gnu.org/licenses/gpl-3.0.html                                                                    #
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
import datetime
import time

from aprsUtilities import *
from getWspr import *
from getLastAprsPositionTime import *

#------------------------ starts here -----------------------------#

with open( "log.txt", "a" ) as log_file:
    log_file.write( time.ctime() + " :#----------------------------------------------------------------------------------------------------------------------------------\n" )

if sys.version_info[0] > 3 :
	raise NameError( 'Tested on only Python ver 3 ')

else :
	with open( "log.txt", "a" ) as log_file:
		log_file.write( time.ctime() + " : Cleared to continue\n" )

strUserCallSign = 'your callsign - the one who will be uploading the spot to APRS'
aprsApiKey = 'your aprs api key see: https://aprs.fi/page/api you will need to create and account and you will find your key here: https://aprs.fi/account/'

strWsprCallSign = 'callsign of the wspr target'

strBalloonCallSign = 'callsign you want your balloon to appear as on APRS i.e. W1XXX-12'

strIcon = 'O'                                        # balloon

wsprSpot = getWspr( strWsprCallSign )

# 2020-01-15 22:10 VE3GHM 14.097184 -26 0 FN25ig +10 KD6RF EM22 1375

if wsprSpot == 1 :                                   # some sort of exception occured, check log

	with open( 'log.txt', 'a' ) as log_file:
		log_file.write( time.ctime() + ' : connection error or no wspr spots encountered \n' )
		log_file.write( time.ctime() + " :#----------------------------------------------------------------------------------------------------------------------------------\n" )
		log_file.close()
		sys.exit( 0 )

lastAprsPositionTimeStamp = int( getLastAprsPositionTime ( strBalloonCallSign, aprsApiKey ) )

print ( lastAprsPositionTimeStamp )

wsprSpotDetails = wsprSpot.split()

wsprDateTime = wsprSpotDetails[0] + ' ' + wsprSpotDetails[1]

wsprSpotDateTime = datetime.datetime.strptime( wsprDateTime, '%Y-%m-%d %H:%M' )

wsprSpotTimeStamp = int( time.mktime( wsprSpotDateTime.timetuple() ) )

with open( "log.txt", "a" ) as log_file:
	log_file.write( time.ctime() + " : last APRS postion timestamp %s\n" % lastAprsPositionTimeStamp )

with open( "log.txt", "a" ) as log_file:
	log_file.write( time.ctime() + " : last WSPR postion timestamp %s\n" % wsprSpotTimeStamp )

if wsprSpotTimeStamp > lastAprsPositionTimeStamp + 15 :

	strGrid = wsprSpotDetails[6]

	if isValidGridSquare( strGrid ) :
		with open( "log.txt", "a" ) as log_file:
			log_file.write( time.ctime() + " : %s is a valid grid square\n" % strGrid )

	else:
		with open("log.txt", "a") as log_file:
			log_file.write( time.ctime() + " : %s is NOT a valid grid square\n" % strGrid )

		sys.exit( 0 )

	latitudeLongitude = gridToLatLong(strGrid).split()

	strLatitude  = toDegreesMinutes( latitudeLongitude[0], 'Latitude' )
	strLongitude = toDegreesMinutes( latitudeLongitude[1], 'Longitude' )

	# save the spot for posterity
	with open( "wspr_spotsLog.txt", "a" ) as spotsLog_file:
		spotsLog_file.write( time.ctime() + " : %s \n" % wsprSpot )

	AprsSendPacket(strUserCallSign, strBalloonCallSign, strLatitude, strLongitude, strIcon, wsprSpot)

else:
	with open( 'log.txt', 'a' ) as log_file:
		log_file.write( time.ctime() + ' : wspr spot is less than 15 minutes older than latest aprs position\n' )
		log_file.close()


# last line for this log entry
with open( "log.txt", "a" ) as log_file:
    log_file.write( time.ctime() + " :#----------------------------------------------------------------------------------------------------------------------------------\n" )

sys.exit( 1 )

# ------------------------------------------------------- That's all Folks!!!! ------------------------------------------------
