# -*- coding: utf-8 -*-
"""
Created on Thu Aug 02 18:13:07 2018

@author: zhou
"""
import ui_correct
import time
import sys,os  
from PyQt4 import QtGui,QtCore
from PyQt4 import Qwt5
import xlrd
import xlsxwriter as xw 
import scipy.io as sio
from scipy import interpolate
import numpy as np
import math


        
class CorrectDlg(QtGui.QDialog, ui_correct.Ui_Dialog): 
    def __init__(self, parent=None): 
        super(CorrectDlg, self).__init__(parent) 
        self.setupUi(self) 
        self.connect(self.pushButton,QtCore.SIGNAL('clicked()'),self.read_data)
        self.connect(self.pushButton_2,QtCore.SIGNAL('clicked()'),self.add_data)
        self.connect(self.pushButton_3,QtCore.SIGNAL('clicked()'),self.del_data)
        self.connect(self.pushButton_4,QtCore.SIGNAL('clicked()'),self.done_data)
        self.connect(self.pushButton_5,QtCore.SIGNAL('clicked()'),self.plot_data)        

        self.tableWidget.setHorizontalHeaderLabels(['depth(cm)','data','age(ka)'])

    #read file 'a.mat' and 'eventlog.mat'
    def read_matd(self):
        data_a=sio.loadmat('a.mat')
        elog=sio.loadmat('eventlog.mat')
        depnum=elog['eventlog']['depnum'][0][0]
        agedata=elog['eventlog']['agedata'][0][0]
        fname=elog['eventlog']['fname'][0][0][0]
        data=data_a['a']
        return data,depnum,agedata,fname   
        
        #save file 'a.mat' adn 'eventlog.mat'
    def save_matd(self,data,depnum,agedata,fname):
        dt=np.dtype([('depnum','O'),('agedata','O'),('fname','O')])
        a=np.array([(depnum,agedata,fname)],dtype=dt)
        sio.savemat('eventlog.mat',{'eventlog':a})
        sio.savemat('a.mat',{'a':data})  
        
    #connect define    
    def read_data(self):
        fname1=self.lineEdit.text()
        tname1=self.lineEdit_2.text()
        wdname1=xlrd.open_workbook(fname1.encode('utf8').decode('utf8'))
        tables=wdname1.sheet_by_name(tname1.encode('utf8').decode('utf8'))
        nrows=tables.nrows
        data_new=[]
        for i in range(nrows):
            data_new.append(tables.row_values(i)[:2])
            if isinstance(data_new[0][0],unicode):
                del data_new[0]
                nrows=nrows-1
            else:
                pass
            data_newar=np.array(data_new)        
    
        if os.path.exists('a.mat') and os.path.exists('eventlog.mat'):
            [da,dp,age,fn]=self.read_matd()
            if len(dp)>0:
                dp=dp[0]
                age=age[0]
            else:
                pass
        
            if fname1==fn:
                data_fin=da
            #plot tx1     listWidget
                if len(dp)>0:
                    self.listWidget.clear()
                    for i in range(0,len(dp)): 
                        dp_plot=np.asscalar(dp[i])
                        self.listWidget.addItem('%d' % dp_plot)                        
                else:
                    pass
            elif fname1!=fn:
                age_fin=np.array([-1]*nrows)    
                data_fin=np.column_stack((data_newar,age_fin))
                dp_creat=np.array([])
                age_creat=np.array([])
                self.save_matd(data_fin,dp_creat,age_creat,fname1)
            else:
                print u'error-unknown file name '
                pass
        else:
            dp_creat=np.array([])
            age_creat=np.array([])
            fn_creat=fname1
            dt=np.dtype([('depnum','O'),('agedata','O'),('fname','O')])
            evenlog_creat=np.array([(dp_creat,age_creat,fn_creat)],dtype=dt)
            sio.savemat('eventlog.mat',{'eventlog':evenlog_creat})
        
            age_fin=np.array([-1]*nrows)
            data_fin=np.column_stack((data_newar,age_fin))
            sio.savemat('a.mat',{'a':data_fin})
    
        #plot tx2   tableWidget
        #self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(len(data_fin))
        self.tableWidget.clear()   
        self.tableWidget.setHorizontalHeaderLabels(['depth(cm)','data','age(ka)'])#add
        for i in range(len(data_fin)):
            for j in range(3):
                cmt='%f' % data_fin[i,j]
                self.newItem=QtGui.QTableWidgetItem(cmt)
                self.tableWidget.setItem(i,j,self.newItem)
        
        
    
    def add_data(self):
        depth_temp1=int(self.lineEdit_3.text())#depthnumber
        age_temp1=float(self.lineEdit_4.text())
        [da,dp,age,fn]=self.read_matd()
        if len(dp)>0:
            dp=dp[0]
            age=age[0]
        else:
            dp=np.array([])
            age=np.array([])
            

        if depth_temp1 not in dp:
            if depth_temp1<len(da)+1 and depth_temp1>0:#check depth number is over range
                age_new1=np.append(age,age_temp1)
                depnum_new1=np.append(dp,depth_temp1)
                #sort for depnum and age
                sort_ax=np.argsort(depnum_new1)
                sort_point=np.argwhere(sort_ax>(len(depnum_new1)-2))[0][0]
                age_new=np.append(age_new1[0:sort_point],age_temp1)
                age_new=np.append(age_new,age_new1[sort_point:len(depnum_new1)-1])
                depnum_new=np.sort(depnum_new1)
            else:
                age_new=age
                depnum_new=dp
                print u'error- depth number over range'   
                pass
        else:
            age_new=age
            depnum_new=dp

        
        #change da
        if len(depnum_new)>1:
            for i in range(0,len(depnum_new)-1):
                kn=(age_new[i+1]-age_new[i])/(da[depnum_new[i+1]-1][0]-da[depnum_new[i]-1][0])# y=kx+b
                #k=np.ones(depnum_new[i+1]-depnum_new[i])*kn
                da[depnum_new[i]-1:depnum_new[i+1],2]=(da[depnum_new[i]-1:depnum_new[i+1],0]-da[depnum_new[i]-1][0])*kn+age[i]
        else:
            pass
    
        #save mat
        self.save_matd(da,depnum_new,age_new,fn)   
    
        #plot tx1 tx2 ->listWidget tableWidget
        self.listWidget.clear()
        for i in range(0,len(depnum_new)): 
            dp_plot=np.asscalar(depnum_new[i])
            self.listWidget.addItem('%d' % dp_plot)    
            
        self.tableWidget.setRowCount(len(da))
        self.tableWidget.clear()        
        for i in range(len(da)):
            for j in range(3):
                cmt='%f' % da[i,j]
                self.newItem=QtGui.QTableWidgetItem(cmt)
                self.tableWidget.setItem(i,j,self.newItem)
            
    def del_data(self):
        depth_temp2=int(self.lineEdit_3.text())#depthnumber
        #age_temp2=float(self.lineEdit_4.text())
        [da,dp,age,fn]=self.read_matd()
        if len(dp)>0:
            dp=dp[0]
            age=age[0]
        else:
            dp=np.array([])
            age=np.array([])
            
        if depth_temp2 in dp:
            if depth_temp2<len(da)+1 and depth_temp2>0:
                dpwhere=np.where(dp==depth_temp2)
                dp_new=np.delete(dp,dpwhere)
                age_new=np.delete(age,dpwhere)
            else:
                print u'error- depth number over range'     
                pass
        else:
            age_new=age
            dp_new=dp
        
        #save mat
        self.save_matd(da,dp_new,age_new,fn)   
        
        #plot listWidget
        self.listWidget.clear()
        for i in range(0,len(dp_new)): 
            dp_plot=np.asscalar(dp_new[i])
            self.listWidget.addItem('%d' % dp_plot)  
        
    def done_data(self):
        [da,dp,age,fn]=self.read_matd()
        if len(dp)>0:
            dp=dp[0]
            age=age[0]
        else:
            dp=np.array([])
            age=np.array([])
        
        if len(dp)>1:
            #check first and end of the depth number ,clear all the -1 in data
            if min(dp)!=1:  
                k0=(age[1]-age[0])/(da[dp[1]-1][0]-da[dp[0]-1][0])
                start_age=age[0]-(da[dp[0],0]-da[0,0])*k0
                dp=np.insert(dp,0,1)
                age=np.insert(age,0,start_age)
            else:
                pass
            
            if max(dp)!=len(da):
                k_end=(age[len(dp)-1]-age[len(dp)-2])/(da[dp[len(dp)-1]-1][0]-da[dp[len(dp)-2]-1][0])
                end_age=(da[len(da)-1,0]-da[dp[len(dp)-1]-1][0])*k_end+age[len(dp)-1]
                dp=np.insert(dp,len(dp),len(da))
                age=np.insert(age,len(age),end_age)
            else:
                pass
                                
            # change da ,calculate k
            kout=np.array([])
            for i in range(0,len(dp)-1):
                kn=(age[i+1]-age[i])/(da[dp[i+1]-1][0]-da[dp[i]-1][0])# y=kx+b
                da[dp[i]-1:dp[i+1],2]=(da[dp[i]-1:dp[i+1],0]-da[dp[i]-1][0])*kn+age[i]
                # sedimentation rate records output
                k=np.ones(dp[i+1]-dp[i])*kn
                kout=np.concatenate((kout,k))
            kout=np.append(kout,kn)
        else:
            print u'error- depth number is empty'
            pass
        #save mat
        self.save_matd(da,dp,age,fn)      
        
        # write excel file :revise :interp_tomac
        #workbook=xw.Workbook(np.asscalar(fn).encode('utf8'))
        workbook=xw.Workbook('output.xlsx')
        revise_sheet=workbook.add_worksheet('revise')
        revise_sheet.write(0,0,u'depth(cm)')
        revise_sheet.write(0,1,u'data')
        revise_sheet.write(0,2,u'age(ky)')
        revise_sheet.write(0,3,u'data(cm)')
        revise_sheet.write(0,4,u'rate(cm/ky)')
        for i in range(len(da)):
            da_plot0=np.asscalar(da[i,0])
            da_plot1=np.asscalar(da[i,1])
            da_plot2=np.asscalar(da[i,2])
            kout_plot4=np.asscalar(kout[i])
            revise_sheet.write(i+1,0,da_plot0)
            revise_sheet.write(i+1,1,da_plot1)
            revise_sheet.write(i+1,2,da_plot2)
            revise_sheet.write(i+1,3,da_plot1)
            revise_sheet.write(i+1,4,kout_plot4)
        
        #if not increasing sequence
        check_increasing=0
        sort_point=np.argsort(age)
        right_sort=np.arange(0,len(age),1)
        check_TF=sort_point==right_sort
        if True in check_TF:
            check_increasing=1
        else:
            pass
        
        if check_increasing==1:
            damin=int(math.ceil(min(da[:,2])))
            damax=int(max(da[:,2]))
            interp_x=np.arange(damin,damax,1)
            f=interpolate.interp1d(da[:,2],da[:,1],kind='linear')  
            interp_y=f(interp_x)
            
            tomac_sheet=workbook.add_worksheet('interp_tomac')
            for i in range(len(interp_x)):
                ix_plot=np.asscalar(interp_x[i])
                iy_plot=np.asscalar(interp_y[i])
                tomac_sheet.write(i,0,ix_plot)
                tomac_sheet.write(i,1,iy_plot)
        else:
            pass
                
        workbook.close()
        
        # write log.txt
        title_num='number'
        title_age='age(ky)'
        title_depth='depth(cm)'
        end_cutoff='-----------------------------'
        f=open('log.txt','a+')
        f.write('%s \r\n' % np.asscalar(fn).encode('utf8'))
        f.write('%s \r\n' % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        f.write('%s\t%s\t%s \r\n' % (title_num,title_age,title_depth) )
        for i in range(0,len(dp)):
            f.write('%d\t%f\t%f \r\n' % (np.asscalar(dp[i]),np.asscalar(age[i]),np.asscalar(da[dp[i]-1][0])) )
        f.write('%s \r\n' % end_cutoff)
        f.close()
        
        #plot listWidget and tableWidget
        self.listWidget.clear()
        for i in range(0,len(dp)): 
            dp_plot=np.asscalar(dp[i])
            self.listWidget.addItem('%d' % dp_plot)    
            
        self.tableWidget.setRowCount(len(da))
        self.tableWidget.clear()      
        self.tableWidget.setHorizontalHeaderLabels(['depth(cm)','data','age(ka)'])
        for i in range(len(da)):
            for j in range(3):
                cmt='%f' % da[i,j]
                self.newItem=QtGui.QTableWidgetItem(cmt)
                self.tableWidget.setItem(i,j,self.newItem)
        
    def plot_data(self):
        [da,dp,age,fn]=self.read_matd()
        if len(dp)>0:
            dp=dp[0]
            age=age[0]
        else:
            dp=np.array([])
            age=np.array([]) 
            
        kout=np.array([])    
        if len(dp)>1:
            # add check the range
            if min(dp)!=1:  #dp[0]!=1 or dp[0]>1
                k0=(age[1]-age[0])/(da[dp[1]-1][0]-da[dp[0]-1][0])
                start_age=age[0]-(da[dp[0],0]-da[0,0])*k0
                dp=np.insert(dp,0,1)
                age=np.insert(age,0,start_age)
            else:
                pass
            
            if max(dp)!=len(da):    #dp[len(dp)-1]!=len(da) or dp[len(dp)-1]<len(da)
                k_end=(age[len(dp)-1]-age[len(dp)-2])/(da[dp[len(dp)-1]-1][0]-da[dp[len(dp)-2]-1][0])
                end_age=(da[len(da)-1,0]-da[dp[len(dp)-1]-1][0])*k_end+age[len(dp)-1]
                dp=np.insert(dp,len(dp),len(da))
                age=np.insert(age,len(age),end_age)
            else:
                pass  
            
            # change da ,calculate k
            for i in range(0,len(dp)-1):
                kn=(age[i+1]-age[i])/(da[dp[i+1]-1][0]-da[dp[i]-1][0])# y=kx+b
                da[dp[i]-1:dp[i+1],2]=(da[dp[i]-1:dp[i+1],0]-da[dp[i]-1][0])*kn+age[i]
                # sedimentation rate records output
                k=np.ones(dp[i+1]-dp[i])*kn
                kout=np.concatenate((kout,k))  
        else:
            pass
        
        #plot
        self.qwtPlot.clear()
        y1=da[:,0]    # ues the depth as y-axis
        #y1=da[:,3]    # use the age as y-axis
        #x=kout
        self.qwtPlot.setAxisTitle(self.qwtPlot.yLeft,'depth(cm)')
        curve =Qwt5.QwtPlotCurve()
        curve.setData(kout,y1)
        curve.attach(self.qwtPlot)
        self.qwtPlot.replot()
        
    

        
if __name__ == '__main__':  
    app=0
    app = QtGui.QApplication(sys.argv) 
    dialog = CorrectDlg() 
    dialog.show() 
    app.exec_() 