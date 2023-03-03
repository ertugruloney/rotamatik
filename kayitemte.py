import sys

from PyQt5 import QtWidgets,QtGui,QtCore
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
import  pandas as pd
import numpy as np
import mysql.connector as mysql
DF=pd.read_excel('DF.xlsx')
DF=DF.iloc[:,1:]
df=DF.values.tolist()

dsasd=2
try:
    mydb = mysql.connect(
      host="localhost",
      database='rotamatik',
      user="root",
      password="",
      )
    mycursor = mydb.cursor()
    
    sql = "SELECT rota_id From eski"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    myresult=list(myresult)  
    mycursor.close()
    rota_id=myresult[-1][0]+1
    asdsa=2
    mydb = mysql.connect(
      host="localhost",
      database='rotamatik',
      user="root",
      password="",
      )
    mycursor = mydb.cursor()
    
    count=0
    for i in df:
        sql="INSERT INTO eski(baslangic,gidilen,sira,rota_id,arac_id) VALUES(%s,%s,%s,%s,%s)"
        mycursor.execute(sql,(i[0],i[1],count,rota_id,i[3],))
        count+=1
       
       
    mycursor.close()
    mydb.commit()  

except:
    
    mydb = mysql.connect(
      host="localhost",
      database='rotamatik',
      user="root",
      password="",
      )
    mycursor = mydb.cursor()
    rota_id=0
    count=0
    for i in df:
        sql="INSERT INTO eski(baslangic,gidilen,sira,rota_id,arac_id) VALUES(%s,%s,%s,%s,%s)"
        mycursor.execute(sql,(i[0],i[1],count,rota_id,i[3],))
        count+=1
       
   
    mycursor.close()
    mydb.commit()            
if len(myresult)==0:
    mydb = mysql.connect(
      host="localhost",
      database='rotamatik',
      user="root",
      password="",
      )
    mycursor = mydb.cursor()
    rota_id=0
    count=0
    for i in df:
        sql="INSERT INTO eski(baslangic,gidilen,sira,rota_id,arac_id) VALUES(%s,%s,%s,%s,%s)"
        mycursor.execute(sql,(i[0],i[1],count,rota_id,i[3],))
        count+=1
       
   
    mycursor.close()
    mydb.commit()   
   