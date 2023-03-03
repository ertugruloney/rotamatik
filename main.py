import sys
import pyodbc
from PyQt5 import QtWidgets,QtGui,QtCore
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from PyQt5.QtWidgets import *
import  pandas as pd
import numpy as np
import mysql.connector as mysql
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import sys
import googlemaps
from itertools import tee
import pandas as pd
import math 

class rotalama:
    
    
    
    @staticmethod
    def print_solution(data, manager, routing, solution):
   
       result=[]
       total_distance = 0
       total_load = 0
       for vehicle_id in range(data['num_vehicles']):
           route=[]
           index = routing.Start(vehicle_id)
           plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
           route_distance = 0
           route_load = 0
           while not routing.IsEnd(index):
               node_index = manager.IndexToNode(index)
               route_load += data['demands'][node_index]
             
               route.append(node_index)
          
               previous_index = index
               index = solution.Value(routing.NextVar(index))
               route_distance += routing.GetArcCostForVehicle(
                   previous_index, index, vehicle_id)
           result.append(route)
         
           total_distance += route_distance
           total_load += route_load
       return result
    @staticmethod
    def distance_callback(from_index, to_index):
       """Returns the distance between the two nodes."""
       # Convert from routing variable Index to distance matrix NodeIndex.
       from_node = manager.IndexToNode(from_index)
       to_node = manager.IndexToNode(to_index)
       return data['distance_matrix'][from_node][to_node]
    @staticmethod
    def demand_callback(from_index):
       """Returns the demand of the node."""
       # Convert from routing variable Index to demands NodeIndex.
       from_node = manager.IndexToNode(from_index)
       return data['demands'][from_node]
     

class tablescreen(QDialog):
    
    switch_window = QtCore.pyqtSignal()
    def __init__(self,kapasite,nokta):
        super().__init__()
        self.kapasite=kapasite
        self.nokta=nokta
        self.init_ui()

        
    def init_ui(self):
       self.aciklama=QtWidgets.QLabel('Yeni Rota Bilgileri')
       self.olusturmaB = QtWidgets.QPushButton("rota oluştur")
       self.olusturmaB.clicked.connect(self.rota)
       self.table=QtWidgets.QTableWidget() 
       self.table.setRowCount(self.nokta)
       self.table.setColumnCount(4)
       self.table.setHorizontalHeaderLabels(["Durak ismi","X","Y","Kişi sayısı"])
       self.table.horizontalHeader().setStretchLastSection(True)
       
       self.table.horizontalHeader().setSectionResizeMode(
           QHeaderView.Stretch)
       v_box=QtWidgets.QVBoxLayout()
       v_box.addWidget(self.aciklama)
       v_box.addWidget(self.table)
       v_box.addWidget(self.olusturmaB)
    
       v_box.addStretch()
       
       self.setLayout(v_box)
       
       self.setGeometry(500,500,500,50)
    
    def create_data_model(self):
          Data=[]
          ID=[]
          a=self.table
          for i in range(self.nokta):
              data=[]
              for j in range(4):
                  item=self.table.item(i,j).text()
                  data.append(item)
              Data.append(data)
              ID.append(i)
              print(Data)
          
          Data2=[]
          for i in range(len(Data)):
              data2=[]
              for j in range(4):
               if j==3:
                   data2.append(int(Data[i][j]))
               if j>0 and j<3:
                   data2.append(float(Data[i][j]))
               if j<1:
                   data2.append(Data[i][j])
                   
              Data2.append(data2)    
              
          
          API_key = ''#enter Google Maps API key
          gmaps = googlemaps.Client(key=API_key)
          
          time_list = []
          distance_list = []
          origin_id_list = []
          destination_id_list = []
          df2=pd.DataFrame(Data2,columns=['isim','latitude','longitude','Kişi'])
          df3=pd.DataFrame(ID,columns=(['ID']))
          df = pd.concat([df3, df2], axis=1)
          for (i1, row1) in df.iterrows():
         
            LatOrigin = row1['latitude']
            LongOrigin = row1['longitude']
            origin = (LatOrigin, LongOrigin)
            origin_id = row1['ID'] 
            for (i2, row2) in  df.iterrows():
            
             LatDestination = row2['latitude']
             LongDestination = row2['longitude']
             destination_id = row2['ID']
             destination = (LatDestination, LongDestination)
             #google masp api mesafe
             result = gmaps.distance_matrix(origin, destination, mode = 'driving')
             result_distance = result["rows"][0]["elements"][0]["distance"]["value"]
             result_time = result["rows"][0]["elements"][0]["duration"]["value"]
             time_list.append(result_time)
             distance_list.append(result_distance)
             origin_id_list.append(origin_id)
             destination_id_list.append(destination_id)
          """

          la=df['latitude'].values.tolist()
          lo=df['longitude'].values.tolist()
          response = gmaps.distance_matrix([str(la[0]) + " " + str(lo[0])], [str(la[1]) + " " + str(lo[1])])['rows'][0]['elements'][0]
          """
          #%%
          output = pd.DataFrame(distance_list, columns = ['Distance in meter'])
          output['duration in seconds'] = time_list
          output['origin_id'] = origin_id_list
          output['destination_id'] = destination_id_list  
          output=output.values.tolist()
          ds=np.zeros([self.nokta,self.nokta])
          for i in output:
              ds[i[2]][i[3]]=i[0]
          ds=ds.tolist()
          data = {}
          data['distance_matrix'] =ds
          data['demands'] = df['Kişi'].values.tolist()
         
          numV=math.ceil(sum(df['Kişi'].values.tolist())/self.kapasite)
          data['num_vehicles'] =  numV
          data['vehicle_capacities'] = [self.kapasite for i in range(numV)]
          data['depot'] = 0
          return data,df['isim'].values.tolist(),ds, df['Kişi'].values.tolist()
    def main(self):
          """Solve the CVRP problem."""
          # Instantiate the data problem.
          data,names,ds,kisi = self.create_data_model()
          Rotalama=rotalama()
          # Create the routing index manager.
          manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                                 data['num_vehicles'], data['depot'])

          # Create Routing Model.
          routing = pywrapcp.RoutingModel(manager)


          # Create and register a transit callback.
          def distance_callback(from_index, to_index):
              """Returns the distance between the two nodes."""
              # Convert from routing variable Index to distance matrix NodeIndex.
              from_node = manager.IndexToNode(from_index)
              to_node = manager.IndexToNode(to_index)
              return data['distance_matrix'][from_node][to_node]

          transit_callback_index = routing.RegisterTransitCallback(distance_callback)

          # Define cost of each arc.
          routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)


          # Add Capacity constraint.
          def demand_callback(from_index):
              """Returns the demand of the node."""
              # Convert from routing variable Index to demands NodeIndex.
              from_node = manager.IndexToNode(from_index)
              return data['demands'][from_node]

          demand_callback_index = routing.RegisterUnaryTransitCallback(
              demand_callback)
          routing.AddDimensionWithVehicleCapacity(
              demand_callback_index,
              0,  # null capacity slack
              data['vehicle_capacities'],  # vehicle maximum capacities
              True,  # start cumul to zero
              'Capacity')

          # Setting first solution heuristic.
          search_parameters = pywrapcp.DefaultRoutingSearchParameters()
          search_parameters.first_solution_strategy = (
              routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
          search_parameters.local_search_metaheuristic = (
              routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
          search_parameters.time_limit.FromSeconds(1)

          # Solve the problem.
          solution = routing.SolveWithParameters(search_parameters)

          # Print solution on console.
          if solution:
              result=Rotalama.print_solution(data, manager, routing, solution)
          return result,names,ds,kisi

    
    def rota(self):
      
  
   
   
        result,names,ds,kisi=self.main()
       
   
        
       
        DF=[]
        for count,i in enumerate(result):
           for j in range(1,len(i)):
              dictt={'Başlangıç':names[i[j-1]],
                     'Bitiş':names[i[j]],
                     'araç':count+1,
                     'mesafe':ds[i[j-1]][i[j]],
                     'kişi':kisi[i[j]],
                     }
              DF.append(dictt)
       
        DF=pd.DataFrame(DF)   
        DF.to_excel('sonuç.xlsx')
      
        
        df=DF.values.tolist()
    
    
        try:
           mydb = pyodbc.connect('Driver={SQL Server};'
                                 'Server=DESKTOP-DPMGSTQ\SQLEXPRESS;'
                                 'Database=rotamatik;'
                                 'Trusted_Connection=yes;')

           mycursor = mydb.cursor()
           sql = "SELECT rota_id From eski"
           mycursor.execute(sql)
           myresult = mycursor.fetchall()
           myresult=list(myresult)  
           mycursor.close()
           rota_id=myresult[-1][0]+1
           mydb = pyodbc.connect('Driver={SQL Server};'
                                 'Server=DESKTOP-DPMGSTQ\SQLEXPRESS;'
                                 'Database=rotamatik;'
                                 'Trusted_Connection=yes;')

           mycursor = mydb.cursor()
  
        
           
           count=0
           for i in df:
               sql='''INSERT INTO eski (baslangic,gidilen,sira,rota_id,arac_id) VALUES (?,?,?,?,?)'''
               data=[i[0],i[1],count,rota_id,i[2]]
               mycursor.execute(sql,data)
               mydb.commit()  
               count+=1
              
              
           mycursor.close()
            
           self.close()    
        except:
           
           mydb = pyodbc.connect('Driver={SQL Server};'
                                 'Server=DESKTOP-DPMGSTQ\SQLEXPRESS;'
                                 'Database=rotamatik;'
                                 'Trusted_Connection=yes;')

           mycursor = mydb.cursor()
           rota_id=0
           count=0
           for i in df:
               sql='''INSERT INTO eski (baslangic,gidilen,sira,rota_id,arac_id) VALUES (?,?,?,?,?)'''
               data=[i[0],i[1],count,rota_id,i[2]]
               mycursor.execute(sql,data)
               mydb.commit()  
               count+=1
               
          
           mycursor.close()
                   
        if len(myresult)==0:
           mydb = pyodbc.connect('Driver={SQL Server};'
                                 'Server=DESKTOP-DPMGSTQ\SQLEXPRESS;'
                                 'Database=rotamatik;'
                                 'Trusted_Connection=yes;')

           mycursor = mydb.cursor()
           rota_id=0
           count=0
           for i in df:
               sql="INSERT INTO eski(baslangic,gidilen,sira,rota_id,arac_id) VALUES(%s,%s,%s,%s,%s)"
               mycursor.execute(sql,(i[0],i[1],count,rota_id,i[3],))
               count+=1
              
          
           mycursor.close()
           mydb.commit()   
           self.close()   
class runscreen(QDialog):
    switch_window = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.init_ui()

        
    def init_ui(self):
  
      
        self.lineEdit_kapasite =QtWidgets.QLineEdit()
        self.lineEdit_kapasite.setPlaceholderText('araç kapasitesini giriniz:')
        self.lineEdit_nokta =QtWidgets.QLineEdit()
        self.lineEdit_nokta.setPlaceholderText('başlangıçda dahil nokta sayısını giriniz:')
        self.olusturmaB = QtWidgets.QPushButton("noktaları oluştur")
        self.olusturmaB.clicked.connect(self.tablegitme)
        v_box=QtWidgets.QVBoxLayout()
        
        v_box.addWidget(self.lineEdit_kapasite)
        v_box.addWidget(self.lineEdit_nokta)
        v_box.addWidget(self.olusturmaB)
        v_box.addStretch()
        
        self.setLayout(v_box)
        
        self.setGeometry(200,300,300,300)
    def tablegitme(self):
        a=int(self.lineEdit_kapasite.text())
        b=int(self.lineEdit_nokta.text())
        self.w=tablescreen(a,b)
        self.w.show()
        self.close()
    
        
    
class firstscreen(QDialog):
    switch_window = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        
    def init_ui(self):
        
   
        self.gorme = QtWidgets.QPushButton("Kayıtları Görme")
        self.gorme.clicked.connect(self.gormeF)
        self.olusturmaB = QtWidgets.QPushButton("yeni rota oluşturma")
        self.olusturmaB.clicked.connect(self.olusturma)
        
        
        v_box=QtWidgets.QVBoxLayout()

        v_box.addWidget(self.gorme)
        v_box.addWidget(self.olusturmaB)
        v_box.addStretch()
        
        self.setLayout(v_box)
        
        self.setGeometry(300,310,200,100)
    def gormeF(self):
        try:
            mydb = pyodbc.connect('Driver={SQL Server};'
                                  'Server=DESKTOP-DPMGSTQ\SQLEXPRESS;'
                                  'Database=rotamatik;'
                                  'Trusted_Connection=yes;')

            mycursor = mydb.cursor()
            
            sql = "SELECT * From eski"
            tabele=pd.read_sql(sql, mydb) 
           

            
            tabele.to_excel('sonkayitlar.xlsx')
            QtWidgets.QMessageBox.about(self, "Eski Kayıtlar", "Eski rotlara excel olarak kayıt edilmiştir")
        except:
            
            QtWidgets.QMessageBox.about(self, "Eski Kayıtlar", "Kayıt mevcut değildir")
    def olusturma(self):
        self.w=runscreen()
        self.w.show()
#kayıt olma ekranı
class kayitolmaW(QDialog):
    switch_window = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        self.setWindowTitle('Login')
    def init_ui(self):
        self.lineEdit_username =QtWidgets.QLineEdit()
        self.lineEdit_username.setPlaceholderText('Kullanıcı adını Giriniz')
        self.lineEdit_isim =QtWidgets.QLineEdit()
        self.lineEdit_isim.setPlaceholderText('adınızı giriniz')
        self.lineEdit_soyad =QtWidgets.QLineEdit()
        self.lineEdit_soyad.setPlaceholderText('soyadınızı girin')
        self.lineEdit_sifre =QtWidgets.QLineEdit()
        self.lineEdit_sifre.setPlaceholderText('şifreyi giriniz')
        self.kayit = QtWidgets.QPushButton("Kayıt Olma")
        self.kayit.clicked.connect(self.kayitetme)
        self.geri = QtWidgets.QPushButton("Geri")
        self.geri.clicked.connect(self.geri_gitme)
        
        
        v_box=QtWidgets.QVBoxLayout()
        v_box.addWidget(self.lineEdit_username)
        v_box.addWidget(self.lineEdit_isim)
        v_box.addWidget(self.lineEdit_soyad)
        v_box.addWidget(self.lineEdit_sifre)
        v_box.addWidget(self.geri)
        v_box.addWidget(self.kayit)
        v_box.addStretch()
        
        self.setLayout(v_box)
        
        self.setGeometry(300,310,300,300)
        
    def kayitetme(self):
        a=self.lineEdit_username.text()
       
        try:
            mydb = pyodbc.connect('Driver={SQL Server};'
                                  'Server=DESKTOP-DPMGSTQ\SQLEXPRESS;'
                                  'Database=rotamatik;'
                                  'Trusted_Connection=yes;')

            mycursor = mydb.cursor()
            sql = "SELECT * From kayitlilar where username='%s'"%(self.lineEdit_username.text())
            tabele=pd.read_sql(sql, mydb) 
            username=tabele.iloc[0,1]
          
            mycursor.close()
            if usernam==(self.lineEdit_username.text()):
          
                QtWidgets.QMessageBox.about(self, "Kayıt olma hatası", "Kullanıcı adı kullanılmış")
            else:
                 mydb = pyodbc.connect('Driver={SQL Server};'
                                       'Server=DESKTOP-DPMGSTQ\SQLEXPRESS;'
                                       'Database=rotamatik;'
                                       'Trusted_Connection=yes;')
                
                 mycursor = mydb.cursor()
                 sorgulist=[]
                 sorgulist.append(self.lineEdit_username.text())
                 
                 sorgulist.append(self.lineEdit_isim.text())
                 sorgulist.append(self.lineEdit_soyad.text())
                 sorgulist.append(self.lineEdit_sifre.text())
                 
                 durum=0
                 for i in sorgulist:
                     if len(i)==0:
                         durum=1
                         QtWidgets.QMessageBox.about(self, "Kayıt olma hatası", "lütfen girilen bilgileri kontrol edin")
                         break
                 if durum==0:
                     
                     
                     sql="INSERT INTO kayitlilar (isim,soyad,username,sifre) VALUES(?,?,?,?)"
                     data=[self.lineEdit_isim.text(),self.lineEdit_soyad.text(),self.lineEdit_username.text(),self.lineEdit_sifre.text()]
                     mycursor.execute(sql,data)
                                                                                                               
                    
                     mycursor.close()
                     mydb.commit()
                     self.w=Pencere()
                     self.w.show()
                     self.close()                
        except:
            a=self.lineEdit_username.text()
            mydb = pyodbc.connect('Driver={SQL Server};'
                                  'Server=DESKTOP-DPMGSTQ\SQLEXPRESS;'
                                  'Database=rotamatik;'
                                  'Trusted_Connection=yes;')

            mycursor = mydb.cursor()
            sorgulist=[]
            sorgulist.append(self.lineEdit_username.text())
            
            sorgulist.append(self.lineEdit_isim.text())
            sorgulist.append(self.lineEdit_soyad.text())
            sorgulist.append(self.lineEdit_sifre.text())
            
            durum=0
            for i in sorgulist:
                if len(i)==0:
                    durum=1
                    QtWidgets.QMessageBox.about(self, "Kayıt olma hatası", "lütfen girilen bilgileri kontrol edin")
                    break
            if durum==0:
                
                
                sql="INSERT INTO kayitlilar (isim,soyad,username,sifre) VALUES(?,?,?,?)"
                data=[self.lineEdit_isim.text(),self.lineEdit_soyad.text(),self.lineEdit_username.text(),self.lineEdit_sifre.text()]
                mycursor.execute(sql,data)
                                                                                                          
               
                mycursor.close()
                mydb.commit()
                self.w=Pencere()
                self.w.show()
                self.close()
                
    def geri_gitme(self):
                self.w=Pencere()
                self.w.show()
                self.close()
#main pencere
class Pencere (QtWidgets.QMainWindow):
    switch_window = QtCore.pyqtSignal(str)
    
    def __init__(self):

        super().__init__()
        self.setWindowTitle('Main Window')
        self.sub_window=kayitolmaW()
        
   
       



       
        self.table=QtWidgets.QTableWidget() 
        self.lineEdit_username =QtWidgets.QLineEdit()
        self.lineEdit_username.setPlaceholderText('Kullanıcı adını Giriniz')
       
        self.lineEdit_sifre=QtWidgets.QLineEdit()
        self.lineEdit_sifre.setPlaceholderText('Şifrenizi Giriniz')
        self.butoncalistir = QtWidgets.QPushButton("Giriş")
        self.butoncalistir.setIcon(QtGui.QIcon("calistir.png"))
        self.butoncalistir.clicked.connect(self.check_password)
        self.butonkaydet = QtWidgets.QPushButton("Kayıt Olma")
        self.butonkaydet.setIcon(QtGui.QIcon("kaydet.png"))
        self.butonkaydet.clicked.connect(self.loginsecreen)
        
    
      
 
        h_box2 = QtWidgets.QHBoxLayout()
    
        
        h_box2.addWidget(self.butoncalistir)
        h_box2.addWidget(self.butonkaydet)
       

   
        

        v_box=QtWidgets.QVBoxLayout()
        v_box.addWidget(self.lineEdit_username)
        v_box.addWidget(self.lineEdit_sifre)
       
        
        v_box.addStretch()
        v_box.addLayout(h_box2)
        w = QtWidgets.QWidget()
        w.setLayout(v_box)
        self.setCentralWidget(w)
        self.setGeometry(100,110,100,100)
        
      
       
      
    def check_password (self):
        sql = "SELECT * From kayitlilar where username='%s'"%(self.lineEdit_username.text())
        mydb = pyodbc.connect('Driver={SQL Server};'
                              'Server=DESKTOP-DPMGSTQ\SQLEXPRESS;'
                              'Database=rotamatik;'
                              'Trusted_Connection=yes;')

        adsa=2
        try:
            tabele=pd.read_sql(sql, mydb) 
            password=tabele.iloc[0,4]
          
            if password!=self.lineEdit_sifre.text():
                QtWidgets.QMessageBox.about(self, "Giriş Hatası", "Şifreyi kontrol edin")
                
            else:
                
                self.F=firstscreen()
                self.F.show()
                self.close()
        except:
            QtWidgets.QMessageBox.about(self, "Giriş Hatası", "Lütfen kullanıcı adını kontrol edin")

 

            
        
    def loginsecreen(self):
        
        self.sub_window.show()
        self.close()
        
        
        
app = QtWidgets.QApplication(sys.argv)
pencere = Pencere()
pencere.show()
sys.exit(app.exec_())