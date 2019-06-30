#!/usr/bin/env python
'''
pip install mysql-connector-python
BMH Change log
16-05-2562
Change path test_blood.txt -> /tmp/test_blood.txt
Change path tmp_blood.txt -> /tmp/tmp_blood.txt
'''

import time
import serial
import sys
import os
import mysql.connector
import io
from time import sleep

ser = serial.Serial(

    port='/dev/ttyUSB0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=2
)
sleep( 1 )
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
        '''
        Remove Byte code in String
        '''
            tmp_x = x.replace('\x1e','|')
            tmp_x = tmp_x.replace('\x02','')
            tmp_x = tmp_x.replace('\x01','')
            tmp_x = tmp_x.replace('\x16','')

            f_x = open("/tmp/xx","w+")
            # print(tmp_x)
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
                print ( bps_0[1] + '|' + bpd_0[1] + '|' + pulse_0[1] )
                print("+Receive data.... OK")
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
                        bps = bps[1]
                        bpd = bpd[1]
                        pulse = pulse[1]
                        f_tmp.write(pt_vn + '|' + bps + '|' + bpd + '|' + pulse )
                        '''
                        Config connection to HIS and Replicate server.
                        '''
                        iphost = ""
                        uid = ""
                        pw = ""
                        db = ""
                        p = "" # Port
			iphost_rep = ""
			uid_rep = ""
			pw_rep = ""
			db_rep = ""
			p_rep = ""
			'''
			; Config master HIS Server
			'''
                        mydb = mysql.connector.connect(
                            host=iphost,
                            user=uid,
                            passwd=pw,
                            database=db,
                            port=p
                            )
			'''
			; Config replicate HIS Server.
			'''
                        mydb_rep = mysql.connector.connect(
                            host=iphost_rep,
                            user=uid_rep,
                            passwd=pw_rep,
                            database=db_rep,
                            port=p_rep
                            )
			
                        mycursor = mydb.cursor()
			mycursor_rep = mydb_rep.cursor()
                        if mydb.is_connected():
                          sql = "UPDATE opdscreen SET bps = %s, bpd = %s, pulse = %s  WHERE vn = %s"
                          sql_max_opdscreen_bp_id = "SELECT MAX(opdscreen_bp_id) FROM opdscreen_bp"
                          mycursor.execute(sql_max_opdscreen_bp_id)
                          records = mycursor.fetchall()
                          for row in records:                          
                            max_bp_id = int(row[0])
                          max_opdscreen_bp_id = max_bp_id + 1
                          val = (bps,bpd,pulse,pt_vn)
                          bp_host_name = "TM" # Create Staff
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
    except KeyboardInterrupt:
        f_delete = ' rm -rf /tmp/*.txt '
        os.system( f_delete )
        f_create = ' touch /tmp/test_blood.txt /tmp/tmp_blood.txt '
        os.system( f_create )
        print 'BYE BYE...'
        sys.exit()
    except IOError as e:
        print( e.errno )
        if e.errno == 2:
            print("Please Pull OUT SMC and Insert again..!")
            print("")
    except:
        print( "Unknow Status error...!!")
        f_delete = ' rm -rf /tmp/*.txt '
        os.system( f_delete )
        f_create = ' touch /tmp/test_blood.txt /tmp/tmp_blood.txt '
        os.system( f_create )
