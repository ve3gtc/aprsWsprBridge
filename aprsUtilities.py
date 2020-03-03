#!/usr/bin/python
#==============================================================================================================#
#                                                                                                              #
# aprsUtilies - Python library of utilities for use with posting spots to APRS                                 #
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
from socket import *
import re                        #regex
import datetime
import time
import requests
import json

#==============================================================================================================#
#                                                                                                              #
# aprslib - Python library for working with APRS                                                               #
# Copyright (C) 2013-2014 Rossen Georgiev                                                                      #
#                                                                                                              #
# https://github.com/rossengeorgiev/aprs-python/blob/master/aprslib/passcode.py                                #
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
"""
Contains a function for generating passcode from callsign
"""

def passCode(pcStrCallsign):
    """
    Takes a CALLSIGN and returns passcode
    """
    assert isinstance(pcStrCallsign, str)

    pcStrCallsign = pcStrCallsign.split('-')[0].upper()

    code = 0x73e2
    for i, char in enumerate(pcStrCallsign):
        code ^= ord(char) << (8 if not i % 2 else 0)

    return code & 0x7fff


#==============================================================================================================#
#                                                                                                              #
# - AprsSendPacket(aspStrCallSign, aspStrAprsMessage)                                                 #
#                                                                                                              #
# - aspStrCallSign is the callsign of WHO is posting the spot, NOT the callsign of the ballaoon                #
# - the callsign of balloon is in aspStrAprsMessage                                                            #
#                                                                                                              #
# - sends data to aprs.fi                                                                                      #
#                                                                                                              #
# - http://www.aprs-is.net                                                                                     #
#                                                                                                              #
#==============================================================================================================#
"""
function to upload a data packet to aprs.fi netowrk
"""
#def AprsSendPacket(aspStrCallSign, apsStrAprsMessage):

def AprsSendPacket(aspStrUserCallsign, aspStrBalloonCAllSign, aspStrLatitude, aspStrLongitude, aspStrIcon, aspStrData):

	serverHost = 'second.aprs.net'
	serverPort = 10152

	#==============================================================================================================#
	#                                                                                                              #
	# Very simple RegEx to determine is CallSign string is a valid amateur call sign:                              #
	#                                                                                                              #
	# Determines if the callsign conforms to amateur radio international rules (#A#, #AA#, # A#, A##, or AA#).     #
	#                                                                                                              #
	# Callsign length must be between 3 and 6 characters.                                                          #
	#                                                                                                              #
	# @return true if callsign is compliant                                                                        #
	#                                                                                                              #
	# only continue to upload to APRS if provided callsign is compliant                                            #
	#                                                                                                              #
	#==============================================================================================================#

	if ( re.search('^(?:(?:[1-9][A-Z][A-Z]?)|(?:[A-Z][2-9A-Z]?))[0-9][A-Z]{1,3}$', aspStrUserCallsign) ):

		# Pass - compliant callsign, make log entry
		with open("log.txt", "a") as log_file:
			log_file.write(time.ctime() + ' : ' + aspStrUserCallsign + ' is a compliant callsign \n' )

		intPassCode = passCode(aspStrUserCallsign)

		# create socket & connect to server
		clientSocket = socket(AF_INET, SOCK_STREAM)
		clientSocket.connect((serverHost, serverPort))

		# Aprs log in 'user CallSign pass ' + intPassCode + ' vers "aprsBallloon 0.1" \n'
		strAprsLogIn = 'user ' + aspStrUserCallsign + ' pass ' + str(intPassCode) + ' vers "aprsBalloon 0.1" \n'

		clientSocket.sendto(strAprsLogIn.encode(),(serverHost, serverPort))

		# AprsSendPacket(aspStrUserCallsign, aspStrBalloonCAllSign, aspStrLatitude, aspStrLongitude, aspStrIcon, aspStrData):

		aspStrAprsMessage = aspStrBalloonCAllSign + '>APRS,TCIP*:=' + aspStrLatitude + '/' + aspStrLongitude + aspStrIcon + aspStrData + '\n'

		# log packet to be sent
		with open("log.txt", "a") as log_file:
			log_file.write(time.ctime() + ' : ' + aspStrAprsMessage )

		# send aspStrAprsMessage
		clientSocket.sendto(aspStrAprsMessage.encode(),(serverHost, serverPort))

		# close socket -- must be closed to avoidbuffer overflow
		time.sleep(5)                                                        # 5 sec. delay
		clientSocket.shutdown(0)
		clientSocket.close()

		# log packet sent event
		with open("log.txt", "a") as log_file:
			log_file.write(time.ctime() + " : Packet sent at: "+ time.ctime() + '\n' )

		return None


#==============================================================================================================#
#                                                                                                              #
# latLongToGrid(Latitude, Longitude)                                                                           #
#                                                                                                              #
# - converts decimal latitude and Longitude to six character Maidenhead Grid Square                            #
#                                                                                                              #
# - returns Gridsquare as string                                                                               #
#                                                                                                              #
# - using convention of North + South - West - and East +                                                      #
#                                                                                                              #
#==============================================================================================================#
def latLongToGrid(decLatitude, decLongitude):

	upper = 'ABCDEFGHIJKLMNOPQRSTUVWX'
	lower = 'abcdefghijklmnopqrstuvwx'

	llgLatitude  = decLatitude  + 90
	llgLongitude = decLongitude + 180

	gridSquare = upper[int(llgLongitude/20)]
	gridSquare = "%s%s" % (gridSquare, upper[int(llgLatitude/10)])

	gridSquare = "%s%s" % (gridSquare, str(int((llgLongitude/2)%10)))
	gridSquare = "%s%s" % (gridSquare, str(int(llgLatitude%10)))

	gridSquare = "%s%s" % (gridSquare, lower[int(((llgLongitude - int(llgLongitude)) * 60)/5)])
	gridSquare = "%s%s" % (gridSquare, lower[int(((llgLatitude - int(llgLatitude)) * 60)/2.5)])

	return gridSquare

#==============================================================================================================#
#                                                                                                              #
# gridToLatLong(GridSquare)                                                                                    #
#                                                                                                              #
# - converts 4, or 6, charcater Maidenhead Grid Square to decimal Latitude and Longitude                       #
#                                                                                                              #
# - returns Latitude/Longitude as string                                                                       #
#                                                                                                              #
# - using convention of North + South - West - and East +                                                      #
#                                                                                                              #
#==============================================================================================================#
def gridToLatLong(gllGridSquare):

	if not isValidGridSquare(gllGridSquare):
		return "errorInvalidGrid"

	gllGridSquare = gllGridSquare.upper()

	gllLongitude = -180 + ( ((ord(gllGridSquare[0]) - ord('A') ) * 20) + (int(gllGridSquare[2]) * 2 ) )
	gllLatitude  =  -90 + ( ((ord(gllGridSquare[1]) - ord('A') ) * 10) + (int(gllGridSquare[3]) ) )

	if len(gllGridSquare) > 4 :
		gllLongitude = gllLongitude + ( float( (ord(gllGridSquare[4]) - ord('A') ) * 5)   / 60 )
		gllLatitude  =  gllLatitude + ( float( (ord(gllGridSquare[5]) - ord('A') ) * 2.5) / 60 )

	if len(gllGridSquare) == 8 :
		gllLongitude = gllLongitude + ( ( float(int(gllGridSquare[6])) * .5  ) / 60 )
		gllLatitude  = gllLatitude  + ( ( float(int(gllGridSquare[7])) * .25 ) / 60 )

	return "%s %s" % (gllLatitude,gllLongitude)

#==============================================================================================================#
#                                                                                                              #
# isValidGridSquare(GridSqure)                                                                                 #
#                                                                                                              #
# - determines if GridSquare is a valid 4, 6, or 8 charcater Maidenhead Grid Square                            #
#                                                                                                              #
# - returns TRUE or FALSE                                                                                      #
#                                                                                                              #
# - Grid Square pattern is one of 4, 6 or 8 characters and numbers in one of the following                     #
#   patterns:                                                                                                  #
#              [A-R][A-R][0-9][0-9]                                                                            #
#              [A-R][A-R][0-9][0-9][a-x][a-x]                                                                  #
#              [A-R][A-R][0-9][0-9][a-x][a-x][0-9][0-9]                                                        #
#                                                                                                              #
# - convention is that the first pair of letters is upper case and the second set of                           #
#   letters is lower case but in reality Maidenhead Grid Squares are case insensitive                          #
#                                                                                                              #
#==============================================================================================================#
def isValidGridSquare(GridSquare):

	GridSquare = GridSquare.upper()

	if len(GridSquare) == 4 :
		if re.match( '^[A-R][A-R][0-9][0-9]$', GridSquare):
			return True
		else:
			return False

	elif len(GridSquare) == 6 :
		if re.match( '^[A-R][A-R][0-9][0-9][A-X][A-X]$', GridSquare):
			return True
		else:
			return False

	elif len(GridSquare) == 8 :
		if re.match( '^[A-R][A-R][0-9][0-9][A-X][A-X][0-9][0-9]$', GridSquare):
			return True
		else:
			return False

	else:
		return False

#==============================================================================================================#
#                                                                                                              #
# toDegreesMinutes(value,type)                                                                                 #
#                                                                                                              #
# - converts decimal degress to degrees minutes                                                                #
#                                                                                                              #
#==============================================================================================================#
def toDegreesMinutes(value,type):
	"""
        Converts a DD.dddd value into DDMM.mm Notation.

        Pass value as double
        type = {Latitude or Longitude} as string

        returns a string as DDMM.mmDirection

        modified from http://anothergisblog.blogspot.ca/2011/11/convert-decimal-degree-to-degrees.html
	"""
	try:
		value = float(value)
	except:
		#print '\nERROR: Could not convert %s to float.' %(type(value))

		with open("log.txt", "a") as log_file:
			log_file.write(time.ctime() + ' : could not convert ' + str(value) + ' to float\n')

		return 0

	degrees = int(value)
	minutes = abs( (value - int(value) ) * 60.0)

	quadrant = ""
	if type == "Longitude":
		if degrees <= 0:
			quadrant = "W"
		elif degrees > 0:
			quadrant = "E"
		else:
			quadrant = ""
	elif type == "Latitude":
		if degrees < 0:
			quadrant = "S"
		elif degrees >= 0:
			quadrant = "N"
		else:
			quadrant = ""

	if type == "Longitude":
		degreesMinutes = str('{:0>3d}'.format(abs(degrees))) + str('{:05.2f}'.format(minutes)) + "" + quadrant

	elif type == "Latitude":
		degreesMinutes = str('{:0>2d}'.format(abs(degrees))) + str('{:05.2f}'.format(minutes)) + "" + quadrant

	return degreesMinutes
