# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 22:21:46 2020

@author: Administrator
"""

# -*- coding: utf-8 -*-
"""
Created on Tue May 28 19:23:19 2019
将图片按照表格框线交叉点分割成子图片（传入图片路径）
@author: hx
"""
 
import cv2
import numpy as np
import pytesseract
import os
from PIL import Image
import csv
from image_to_string import *

#filename= 'test.jpg'
def save_to_csv(resultfile,header_list,result):#写入列表
    try:       
        if os.path.exists(resultfile):                
            pass
        else:
           with open(resultfile, "a",newline='',encoding='gbk',errors='ignore') as csvfile:                  
               writer = csv.writer(csvfile)
               writer.writerow(header_list)
        with open(resultfile, "a",newline='',encoding='gbk',errors='ignore') as csvfile:                  
           writer = csv.writer(csvfile)
           #result.append(get_timestr())
           writer.writerow(result)
           #print('    正在写入csv文件中.....')
    except Exception as e:            
        print("写入问题"+str(e))
        #value="写入问题"+str(e)+',请关闭重新搜索抓取'
        #scr2.insert(tk.INSERT, get_timestr()+"—"+ value + '\n')
           
def get_list_xy(filename):
    #image = cv2.imread(filename, 1)    
    image = cv2.imdecode(np.fromfile(filename, dtype=np.uint8), 1)
    #灰度图片
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #二值化
    binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, -5)
    #ret,binary = cv2.threshold(~gray, 127, 255, cv2.THRESH_BINARY)
    #cv2.imshow("二值化图片1：", binary) #展示图片
    #cv2.waitKey(0)
     
    rows,cols=binary.shape
    scale = 40
    #识别横线
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(cols//scale,1))
    eroded = cv2.erode(binary,kernel,iterations = 1)
    #cv2.imshow("Eroded Image",eroded)
    dilatedcol = cv2.dilate(eroded,kernel,iterations = 1)
    #cv2.imshow("表格横线展示2：",dilatedcol)
    #cv2.waitKey(0)
     
    #识别竖线
    scale = 20
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(1,rows//scale))
    eroded = cv2.erode(binary,kernel,iterations = 1)
    dilatedrow = cv2.dilate(eroded,kernel,iterations = 1)
    #cv2.imshow("表格竖线展示3：",dilatedrow)
    #cv2.waitKey(0)
     
    #标识交点
    bitwiseAnd = cv2.bitwise_and(dilatedcol,dilatedrow)
    #cv2.imshow("表格交点展示4：",bitwiseAnd)
    #cv2.waitKey(0)
    # cv2.imwrite("my.png",bitwiseAnd) #将二值像素点生成图片保存
     
    #标识表格
    merge = cv2.add(dilatedcol,dilatedrow)
    #cv2.imshow("表格整体展示5：",merge)
    #cv2.waitKey(0)
     
     
    #两张图片进行减法运算，去掉表格框线
    merge2 = cv2.subtract(binary,merge)
    #cv2.imshow("图片去掉表格框线展示6：",merge2)
    #cv2.waitKey(0)
     
    #识别黑白图中的白色交叉点，将横纵坐标取出
    ys,xs = np.where(bitwiseAnd>0)
    
    '''
    print(ys)
    print("----------------")
    print(xs)
    ''' 
    mylisty=[] #纵坐标
    mylistx=[] #横坐标
     
    #通过排序，获取跳变的x和y的值，说明是交点，否则交点会有好多像素值值相近，我只取相近值的最后一点
    #这个10的跳变不是固定的，根据不同的图片会有微调，基本上为单元格表格的高度（y坐标跳变）和长度（x坐标跳变）
    i = 0
    myxs=np.sort(xs)
    for i in range(len(myxs)-1):
        if(myxs[i+1]-myxs[i]>10):
            if myxs[i]>0:
                mylistx.append(myxs[i]-2)
            else:
                mylistx.append(myxs[i])
        i=i+1
    mylistx.append(myxs[i]) #要将最后一个点加入
     
     
    i = 0
    myys=np.sort(ys)
    #print(np.sort(ys))
    for i in range(len(myys)-1):
        if(myys[i+1]-myys[i]>10):
            if myys[i]>0:
                mylisty.append(myys[i]-2)
            else:
                mylisty.append(myys[i])
        i=i+1
    mylisty.append(myys[i]) #要将最后一个点加入     
    print('mylisty',mylisty)
    print('mylistx',mylistx)
    
    return mylisty,mylistx

def point_detect(picture,xs,ys):#判断是否有连续 一块黑色区域，如果有 那就返回1
    #picture = Image.open(filename)
    #w=picture.size[0]
    #h=picture.size[1]
    rgb=picture.load()
    
    xs=int(xs)
    ys=int(ys)
    #print(type(rgb[xs,ys]))    
    num1=0 #上
    for y in range(-10,0):
        try:
            for step_x in range(-2,2):
                rgb=picture.load()[xs+step_x, ys+y]
                #print(xs+step_x, ys+y)
                #print(rgb)
                try:
                    if rgb[0]<20 and rgb[1]<20 and rgb[2]<20:                
                        num1=num1+1
                        break
                    else:
                        pass
                except:
                    if rgb<20:                
                        num1=num1+1
                        break
                    else:
                        pass
        except Exception as e:
            #print(str(e))
            pass

    num2=0 #下
    for y in range(0,10):
        try:
            for step_x in range(-2,2):
                rgb=picture.load()[xs+step_x, ys+y]
                try:
                    if rgb[0]<20 and rgb[1]<20 and rgb[2]<20:                
                        num2=num2+1
                        break
                    else:
                        pass
                except:
                    if rgb<20:                
                        num2=num2+1
                        break
                    else:
                        pass
        except:
            pass


    num3=0 #左
    for x in range(-10,0):
        try:
            for step_y in range(-2,2):
                rgb=picture.load()[xs+x, ys+step_y]
                try:
                    if rgb[0]<20 and rgb[1]<20 and rgb[2]<20:                
                        num3=num3+1
                        break
                    else:
                        pass
                except:
                    if rgb<20:                
                        num3=num3+1
                        break
                    else:
                        pass
        except:
            pass

    num4=0 #右
    for x in range(0,10):
        try:
            for step_y in range(-2,2):
                rgb=picture.load()[xs+x, ys+step_y]
                try:
                    if rgb[0]<20 and rgb[1]<20 and rgb[2]<20:                
                        num4=num4+1
                        break
                    else:
                        pass
                except:
                    if rgb<20:                
                        num4=num4+1
                        break
                    else:
                        pass
        except:
            pass
    
    #print(num1,num2,num3,num4)
    return [num1,num2,num3,num4]

def cut_recognize(filename,mylisty,mylistx):       
    #循环y坐标，x坐标分割表格
    paras=['name','part1','part2','a1','a2','a4','a5','a6','a7','a3','a8','','b1','b2','b3','b4','b5','c0','c1','c2','c3','c4','c5','d0','d1','d2','d3','d4','d5']
    #image=cv2.imread(filename, 1)
    image = cv2.imdecode(np.fromfile(filename, dtype=np.uint8), 1)
    picture = image
    picture = Image.open(filename)
    num = 0
    list = [] 
    for i in range(len(mylisty)-1):
        for j in range(len(mylistx)-1):
            try:                
                #在分割时，第一个参数为y坐标，第二个参数为x坐标
                break_flag=0
                for ii in range(i+1,len(mylisty)):                    
                    for jj in range(j+1,len(mylistx)):
                        if mylisty[ii]-mylisty[i]<(mylisty[-1]/2):                  
                            ROI = image[mylisty[i]+2:mylisty[ii]-2,mylistx[j]+3:mylistx[jj]-3] #减去3的原因是由于我缩小ROI范围
                            temp1=point_detect(picture,mylistx[j],mylisty[i]) # 1 ,2 ,3,4 四个顶点
                            temp2=point_detect(picture,mylistx[jj],mylisty[i]) # 1 ,2 ,3,4 四个顶点
                            temp3=point_detect(picture,mylistx[jj],mylisty[ii]) # 1 ,2 ,3,4 四个顶点
                            temp4=point_detect(picture,mylistx[j],mylisty[ii]) # 1 ,2 ,3,4 四个顶点
                            '''
                            print(mylistx[j],mylisty[i])
                            print(mylistx[jj],mylisty[i])
                            print(mylistx[jj],mylisty[ii])
                            print(mylistx[j],mylisty[ii])
                            print(temp1,temp2,temp3,temp3)
                            print("++++++++++++++++++++")
                            #return break_flag
                            '''
                            p=5 #点数
                            if (temp1[1]>p and temp1[3]>p) and (temp2[2]>p and temp2[1]>p) and (temp3[0]>p and temp3[2]>p) and (temp4[0]>p and temp4[3]>p):                
                                
                                #cv2.imshow("分割后子图片展示：",ROI)
                                #cv2.waitKey(0)
                                save_path_detail = './cut/'
                                if os.path.exists(save_path_detail):
                                    pass
                                else:
                                    os.mkdir(save_path_detail)
                                img_path = save_path_detail + '/' + str(num)+'.tif'                            
                                cv2.imwrite(img_path, ROI) 
                              
                                #pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\tesseract.exe'
                                
                                text1 = image_to_string(paras[num], img_path) 
                                #text2 = ''.join([char for char in text2 if char not in special_char_list])
                                #text1=text1.strip()
                                print('识别分割子图片信息为：'+str(num)+': '+text1)                            
                                #save_to_csv("result.csv",['filename','id','content'],[filename,paras[num],text1])
                                num=num+1
                                list.append(text1)
                                
                                break_flag=1
                                break
                    if break_flag==1:
                        break
            except Exception as e:
                print(str(e))
                pass
            
    return list

def file_name(file_dir):# 获取指定路径下的文件名，并返回列表
    L=[]   
    for root, dirs, files in os.walk(file_dir):  
        for file in files:  
            if os.path.splitext(file)[1] == '.jpg' or os.path.splitext(file)[1] == '.png' or os.path.splitext(file)[1] == '.tif':  
                L.append(os.path.join(root, file))  
    return L 


'''Convert a batch of specific type of PDF tables to a 2D list of string.

   Args:
       filepath: The path to the PDF batch.
   
   Returns:
       list: the first dimension stores the number of the PDF files, the second dimension stores the number of the tuples of each PDF.
'''
def pdf_to_string(filepath):
    filelist=file_name(filepath)
    print("即将识别 %d 张图片" %(len(filelist)))
    print(filelist)
    list = []
    
    for filename in filelist:
        mylisty,mylistx=get_list_xy(filename)
        string = cut_recognize(filename,mylisty,mylistx)
        list.append(string)
        
    return list

'''
if __name__=='__main__':
    filepath=r'E:\work\OCR表格'
    main(filepath)
'''    
