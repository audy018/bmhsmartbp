#! /usr/bin/env python
#-*- coding: utf8 -*-
'''
BMH change log
16-05-2562
Change path write tmp_pt.txt to /tmp/tmp_pt.txt
:: Please install package below. Before run code
apt-get install pcscd python-pyscard
apt-get install python-mysqldb
apt-get install python-mysql.connector
'''
"""
Sample script that monitors smartcard insertion/removal.

__author__ = "http://www.gemalto.com"

Copyright 2001-2012 gemalto
Author: Jean-Daniel Aussel, mailto:jean-daniel.aussel@gemalto.com

This file is part of pyscard.

pyscard is free software; you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 2.1 of the License, or
(at your option) any later version.

pyscard is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with pyscard; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
from __future__ import print_function
from time import sleep

from smartcard.CardMonitoring import CardMonitor, CardObserver

from smartcard.CardConnection import CardConnection
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.util import toHexString, toBytes
from smartcard.System import readers
import binascii
import mysql.connector
import serial
import os
import subprocess

# a simple card observer that prints inserted/removed cards
class PrintObserver(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards
    """

    def update(self, observable, actions):
        (addedcards, removedcards) = actions
        for card in addedcards:
            cardtype = AnyCardType()
            cardrequest = CardRequest( timeout=1, cardType=cardtype )
            cardservice = cardrequest.waitforcard()
            cardservice.connection.connect()

            # print("+Inserted: ", toHexString(card.atr))
            SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08]
            THAI_ID_CARD = [0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]
            REQ_CID = [0x80, 0xb0, 0x00, 0x04, 0x02, 0x00, 0x0d]
            REQ_THAI_NAME = [0x80, 0xb0, 0x00, 0x11, 0x02, 0x00, 0x64]
            REQ_ENG_NAME = [0x80, 0xb0, 0x00, 0x75, 0x02, 0x00, 0x64]
            REQ_GENDER = [0x80, 0xb0, 0x00, 0xE1, 0x02, 0x00, 0x01]
            REQ_DOB = [0x80, 0xb0, 0x00, 0xD9, 0x02, 0x00, 0x08]
            REQ_ADDRESS = [0x80, 0xb0, 0x15, 0x79, 0x02, 0x00, 0x64]
            REQ_ISSUE_EXPIRE = [0x80, 0xb0, 0x01, 0x67, 0x02, 0x00, 0x12]
            DATA = [REQ_CID]
            
            apdu=SELECT+THAI_ID_CARD

            response, sw1, sw2 = cardservice.connection.transmit( apdu )
            for d in DATA:
                response, sw1, sw2 = cardservice.connection.transmit( d )
                if sw1 == 0x61:
                    GET_RESPONSE = [0X00, 0XC0, 0x00, 0x00 ]
                    apdu = GET_RESPONSE + [sw2]
                response, sw1, sw2 = cardservice.connection.transmit( apdu )
                result = ''
                for i in response:
                    result = result+chr(i)
            '''
            Show CID Color.
            '''
            print( "CID :: \x1b[6;30;47m", result ,"\x1b[0m"+" "+"\x1b[2;30;43m[OK]\x1b[0m" )
            # Insert data to HIS below here
            iphost = ""
            db = ""
            uid = ""
            pw = ""
            p = ""
            from mysql.connector import Error
            try:
                connection = mysql.connector.connect(host=iphost,
                                                    database=db,
                                                    user=uid,
                                                    password=pw,
                                                    port=p)
                if connection.is_connected():
                    db_Info = connection.get_server_info()
                    #print("Connected to HOSxP", db_Info)
                    sqlQuery = ("select hn from patient where cid = %(cid)s ")
                    cursor = connection.cursor()
                    cursor.execute(sqlQuery, { 'cid': result })
                    records = cursor.fetchall()
                    for row in records:
                        if(row[0] != ""):
                            sqlOVST = ("Select count(vn) From ovst Where vstdate between Date(NOW()) and Date(NOW()) And hn = %(hn)s ")
                            hn = row[0]
                            cursor = connection.cursor()
                            cursor.execute(sqlOVST, { 'hn': hn })
                            r = cursor.fetchall()
                            for rOVST in r:
                                count_vn = rOVST[0]
                                cursor.close()
                                if(count_vn == 0):
                                    #Insert code for HOSxP.
                                    print("")
                                    print("\x1b[0;30;41m[X]\x1b[0mVN Not found-กรุณาติดต่อแผนกเวชระเบียน !!\n")
                                    f = open("/tmp/tmp_pt.txt","w")
                                    f.close()
                                if(count_vn != 0):
                                    sqlvn = ("Select vn From ovst Where vstdate between Date(NOW()) and Date(NOW()) And hn = %(hn)s ")
                                    cursor = connection.cursor()
                                    cursor.execute(sqlvn, { 'hn': hn })
                                    r = cursor.fetchall()
                                    for pt_vn in r:
                                        print(pt_vn[0].strip(' ')+'|'.strip(' '))
                                        f = open("/tmp/tmp_pt.txt","w+")
                                        f.write(pt_vn[0]+'|')
                                        f.close()
            except Error as e :
                print("Can't Connect HOSxP.",e)
            finally:
              #Closing database connection.
            	# Close Connection HOSxP
                if(connection.is_connected()):
                    connection.close()
                    # print("MySQL connection is closed")
                    print( " \x1b[1;37;41m                               \x1b[0m" )
                    print( " \x1b[1;37;41m !! อย่าลืมดึงบัตร ปชช. ออก /:) !! \x1b[0m" )
                    print( " \x1b[1;37;41m                               \x1b[0m" )
        for card in removedcards:
            #print("-Removed: ", toHexString(card.atr))
            # print("Bye Bye...!:)")
            myCmd = ' clear '
            os.system( myCmd )
            #print("================")
            print( " \x1b[0;30;41m \x1b[0m"+"\x1b[6;30;42m                              \x1b[0m" )
            print( " \x1b[0;30;41m \x1b[0m"+"\x1b[6;30;42m    :: กรุณาเสียบบัตร ปชช.::     \x1b[0m" )
            print( " \x1b[0;30;41m \x1b[0m"+"\x1b[6;30;42m                              \x1b[0m" )

if __name__ == '__main__':
    # print("Insert or remove a smartcard in the system.")
    # print("This program will exit in 1 Day = 86400 seconds")
    # print("")
    print( " \x1b[1;30;42m                              \x1b[0m"+"\x1b[3;30;44m \x1b[0m" )
    print( " \x1b[6;30;42m     :: กรุณาเสียบบัตร ปชช.::    \x1b[0m"+"\x1b[3;30;44m \x1b[0m" )
    print( " \x1b[1;30;42m                              \x1b[0m"+"\x1b[3;30;44m \x1b[0m" )
    #print("================")
    cardmonitor = CardMonitor()
    cardobserver = PrintObserver()
    cardmonitor.addObserver(cardobserver)

    sleep(86400)

    # don't forget to remove observer, or the
    # monitor will poll forever...
    cardmonitor.deleteObserver(cardobserver)

    import sys
    if 'win32' == sys.platform:
        print('press Enter to continue')
        sys.stdin.read(1)
