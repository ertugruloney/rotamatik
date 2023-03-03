import sys

from PyQt5 import QtWidgets,QtGui,QtCore
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
import  pandas as pd
import numpy as np
import mysql.connector as mysql



mydb = mysql.connect(
  host="localhost",
  database='rotamatik',
  user="root",
  password="",
  )
mycursor = mydb.cursor()

sql = "SELECT * From eski"
mycursor.execute(sql)
myresult = mycursor.fetchall()
myresult=list(myresult)  
mycursor.close()
DF=[]
for i in myresult:
       dictt={'Başlangıç':i[1],
              'Gidilen':i[2],
              'Sıra':i[3],
              'araç':i[5],
              'rota':i[4]}
       DF.append(dictt)
DF=pd.DataFrame(DF)

DF.to_excel('sonkayitlar.xlsx')