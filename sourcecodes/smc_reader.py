#!/usr/bin/env python
#-*- coding: utf8 -*-
"""
pip install mysql-connector-python
BMH Change log
16-05-2562
Change path test_blood.txt -> /tmp/test_blood.txt
Change path tmp_blood.txt -> /tmp/tmp_blood.txt
"""

import time
import serial
import sys
import os
import io
from time import sleep
import mysql.connector
from mysql.connector import Error

ser = serial.Serial(

    port='/dev/ttyUSB0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=2
)
print( " Initial data..." )
sleep( 0.5 )
mycmd = ' rm -rf /tmp/*.txt '
os.system( mycmd )
sleep( 1 )
mycmd_file = ' touch /tmp/test_blood.txt /tmp/tmp_blood.txt '
os.system( mycmd_file )
sleep( 1 )
counter=0
while 1:
    try:
        x=ser.readline()
        if x != '':
            tmp_x = x.replace('\x1e','|')
            tmp_x = tmp_x.replace('\x02','')
            tmp_x = tmp_x.replace('\x01','')
            tmp_x = tmp_x.replace('\x16','')

            f_x = open("/tmp/xx","w+")
            bp_data = tmp_x.split( '|' )
            bps_0 = bp_data[5]
            bpd_0 = bp_data[7]
            pulse_0 = bp_data[8]
            bp_data_w = ( bps_0+"|"+bpd_0+"|"+pulse_0 )

            f_x.write(bp_data_w)
            f_x.close()

            if bps_0 == '0' or bpd_0 == '0' :
                print ('Status error data not Found!!...0')
            else :
                bps_0 = bps_0.split('S')
                bpd_0 = bpd_0.split('D')
                pulse_0 = pulse_0.split('P')                
                print ("")
                print ( "Systolic:\t" + bps_0[1] + "\tmmHg" )
                print ( "Diastolic:\t" + bpd_0[1] + "\tmmHg" )
                print ( "Pulse:\t\t" + pulse_0[1] + "\tmmHg" )
                print("Receive data from Automatic BP!!")
                counter = 0

            f_vn = open("/tmp/tmp_pt.txt","r")
            f_msg = f_vn.read()
            pt_vn = f_msg[:12]
            f_vn.close()

            if (pt_vn != ""):
                f = open("/tmp/test_blood.txt","w+")
                f.write(x+"\n")
                f.close()
                f_tmp = open("/tmp/tmp_blood.txt","w+")
                #with open("/tmp/test_blood.txt") as f:
                with open("/tmp/xx") as f:
                    for lines in f:
                        ws = lines.split('|')
                        bps = ws[0].split('S')
                        bpd = ws[1].split('D')
                        pulse = ws[2].split('P')

                        # print( bps+bpd+pulse )

                        bps = bps[1]
                        bpd = bpd[1]
                        pulse = pulse[1]
                        f_tmp.write(pt_vn + '|' + bps + '|' + bpd + '|' + pulse )
                        
                        """
                        แทนที่ xxx.xxx.xxx.xxx ด้วย IP Address ของ HOSxP
                        แทนที่ uuu ด้วย user ของฐานข้อมูล HOSxP
                        แทนที่ ppp ด้วย password ของฐานข้อมูล HOSxP
                        แทนที่ ddd ด้วยชื่อของฐานข้อมูล HOSxP
                        """
                        mydb = mysql.connector.connect(
                            host="xxx.xxx.xxx.xxx",
                            user="uuu",
                            passwd="ppp",
                            database="ddd"
                            )

                        mycursor = mydb.cursor()

                        if mydb.is_connected():
                           sql = "UPDATE opdscreen SET bps = %s, bpd = %s, pulse = %s  WHERE vn = %s"
                           sql_count_opdscreen_bp = "SELECT COUNT(opdscreen_bp_id) FROM opdscreen_bp"
                           sql_max_opdscreen_bp_id = "SELECT MAX(opdscreen_bp_id) FROM opdscreen_bp"
                           mycursor.execute( sql_count_opdscreen_bp )
                           count_opdscreen_bp = mycursor.fetchall()
                           for row in count_opdscreen_bp:
                               if ( int(row[0] ) == 0 ):
                                  max_opdscreen_bp_id = 1
                               elif ( int(row[0] ) != 0 ):
                                  mycursor.execute( sql_max_opdscreen_bp_id )
                                  records = mycursor.fetchall()
                                  for row in records:
                                    max_bp_id = int(str(row[0]))
                                    max_opdscreen_bp_id = max_bp_id + 1
                           val = (bps,bpd,pulse,pt_vn)
                           # TM = ชื่อเครื่องวัดความดัน
                           bp_host_name = "TM"
                           sql_Insert_bp = "INSERT INTO opdscreen_bp (opdscreen_bp_id, vn, screen_date, screen_time, staff, bps, bpd, pulse) VALUES (%s, %s, Date(NOW()), Time(NOW()),%s ,%s, %s, %s)"
                           val_bp = (int(max_opdscreen_bp_id), pt_vn, bp_host_name, float(bps), float(bpd), float(pulse))
                           result = mycursor.execute(sql, val)
                           mydb.commit()
                           result = mycursor.execute(sql_Insert_bp, val_bp)
                           mydb.commit()
                           f_delete = ' rm -rf /tmp/*.txt '
                           os.system( f_delete )
                           f_create = ' touch /tmp/test_blood.txt /tmp/tmp_blood.txt '
                           os.system( f_create )
                           print( "\x1b[0;30;47m Send data success..!!\x1b[0m" )
                f_tmp.close()
        counter+=1
        if counter == 1:
            print(" \x1b[2;31;41m               \x1b[0m" )
        elif counter == 2:
            print(" \x1b[2;37;47m               \x1b[0m" )
        elif counter == 3:
            print(" \x1b[2;34;44m               \x1b[0m" )
            print(" \x1b[2;34;44m               \x1b[0m" )
        elif counter == 4:
            print(" \x1b[2;37;47m               \x1b[0m" )
        if counter == 5:
            print(" \x1b[2;31;41m               \x1b[0m" )
            print("")
            counter = 0
    except KeyboardInterrupt:
        f_delete = ' rm -rf /tmp/*.txt '
        os.system( f_delete )
        f_create = ' touch /tmp/test_blood.txt /tmp/tmp_blood.txt '
        os.system( f_create )
        print 'BYE BYE...'
        sys.exit()
    except IOError as e:
        if e.errno == 2:
            #print("Please Pull SMC and Insert again..!")
            print("กรุณาถอดบัตร ปชช. แล้วเสียบใหม่ !!")
            print("")
    except IndexError:
        print( "..No Data.." )
    except Error as myErr:
        print( " Error while connecting to MySQL!.", myErr )
    except:
        print( "..Unknow Status error...[:)")
        f_delete = ' rm -rf /tmp/*.txt '
        os.system( f_delete )
        f_create = ' touch /tmp/test_blood.txt /tmp/tmp_blood.txt '
        os.system( f_create )
