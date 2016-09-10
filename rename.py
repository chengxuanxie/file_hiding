#coding:utf-8
import os 
import sqlite3
import shutil
import glob
import pickle
from os import renames

destdir= 'Q:'
srcdir='Q:'
type_list=['rmvb','avi','mp4','wmv','Avi','mkv']
database_name=srcdir+'\\movie_name.sqlite'

print('desdir: '+destdir)
print('srcdir: '+srcdir)

'''return a list containing all the files in file_dir'''
def all_file(file_dir):
    file_list=[]
    name_list=os.listdir(file_dir)
    for each_f in name_list:
        if os.path.isfile(os.path.join(file_dir,each_f)):
            file_list.append(os.path.join(file_dir,each_f))
        elif os.path.isdir(os.path.join(file_dir,each_f)):
            newdir=os.path.join(file_dir,each_f)
            file_list.extend(all_file(newdir))
    return file_list 

'''return a list containing all the files of some certain types'''
def select_type(file_list,type_list):
    selected_list=[]
    for each_file in file_list:
        if each_file.split('.')[-1] in type_list:
            selected_list.append(each_file)
    return selected_list

def print_list(a_list):
    for each_l in a_list:
        print(each_l)

'''创建一个数据库，名称为SQLname的值，包含一个名为namelist的表'''
def createSQL(SQLname):
    if os.path.exists(SQLname)==False:        
        connection =sqlite3.connect(SQLname)
        cursor=connection.cursor()
        cursor.execute("""CREATE TABLE namelist(id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,name TEXT UNIQUE NOT NULL,fakename TEXT UNIQUE NOT NULL)""")
        cursor.execute("""CREATE TABLE fakelist(fake_id INTERGER NOT NULL,fake_name TEXT UNIQUE NOT NULL,FOREIGN KEY (fake_id) REFERENCES namelist)""")
        connection.commit()
        connection.close()
 
'''将检测到的新文件名和路径添加到数据库database_name中，为防止重复添加，在插入时检测该名字是否已经存在，若不存在则插入数据'''   
def write_to_SQL(selected_list,name_list_fromDB):
    connection=sqlite3.connect(database_name)
    cursor=connection.cursor()
    for each_name in selected_list:
        name=each_name
        fakename=each_name+'.dat'
        if name not in name_list_fromDB:
            cursor.execute("INSERT INTO namelist (name,fakename) VALUES(?,?)",(name,fakename))
    connection.commit() 
    connection.close()  
 
'''将改名的新名字与id组成的元组存入数据库中'''
def write_to_fakenamelist(newname_tuples,fakelist_fromeDB):
    connection=sqlite3.connect(database_name)
    cursor=connection.cursor()
    for each_tuple in newname_tuples:
        if each_tuple[1] not in fakelist_fromeDB:
            cursor.execute("INSERT INTO fakelist (fake_id,fake_name) VALUES(?,?)",each_tuple)
    connection.commit() 
    connection.close() 
   
      
'''调取数据库中的名称列表，返回一个列表，存放着数据库中已存储的所有文件名称'''
def get_name_list_fromDB():
    connection=sqlite3.connect(database_name)
    cursor=connection.cursor()
    
    results=cursor.execute("""SELECT name FROM namelist""")
    result_list=results.fetchall()
    name_list_fromDB=[row[0] for row in result_list]
    connection.commit
    connection.close()
    return name_list_fromDB

'''返回已存所有假文件名列表'''
def get_fakename_list_fromDB():
    connection=sqlite3.connect(database_name)
    cursor=connection.cursor()
    
    results=cursor.execute("""SELECT fake_name FROM fakelist""")
    result_list=results.fetchall()
    fakename_list_fromDB=[row[0] for row in result_list]
    connection.commit
    connection.close()
    return fakename_list_fromDB
    

'''以id获取名称  返回名称'''
def get_name_fromeDB(ID):
    connection=sqlite3.connect(database_name)
    cursor=connection.cursor()
    result=cursor.execute("""SELECT name FROM namelist WHERE id=?""",(ID,))
    name_fromDB=result.fetchone()
    connection.commit()
    connection.close()
    return name_fromDB[0]

'''以名称获取id 返回id'''
def get_id_fromDB(NAME):
    connection=sqlite3.connect(database_name)
    cursor=connection.cursor()
    result=cursor.execute("""SELECT id FROM namelist WHERE name=?""",(NAME,))
    id_fromDB=result.fetchone()
    connection.commit()
    connection.close()
    return id_fromDB[0]

def get_fakeid_fromDB(NAME):
    connection=sqlite3.connect(database_name)
    cursor=connection.cursor()
    result=cursor.execute("""SELECT fake_id FROM fakelist WHERE fake_name=?""",(NAME,))
    fake_id_fromDB=result.fetchone()
    connection.commit()
    connection.close()
    return fake_id_fromDB[0]

'''从名称中分离出路径'''
def path_from_name(name):
    nameend=name.split('\\')[-1]
    path=name.replace(nameend,'')
    return path

'''由id生产新名称并重命名,返回包含新名称及其对应的id的元组列表'''
def rename_with_id(selected_list):
    newname_tuples=[]
    for each_name in selected_list:
        name=each_name
        path=path_from_name(name)
        id=get_id_fromDB(name)
        newname=path+str(id)+'#dat.dat'
        newname_tuples.append((id,newname))
        os.rename(name,newname) 
    return newname_tuples 

def recover_name(fakelist_fromeDB):
    for each_fakename in fakelist_fromeDB:
        id=get_fakeid_fromDB(each_fakename)
        name=get_name_fromeDB(id)
        os.rename(each_fakename,name)


'''main'''
selected_list=select_type(all_file(srcdir),type_list)
print_list(selected_list)

createSQL(database_name)#创建一个数据库名称为database_name的值

name_list_fromDB=get_name_list_fromDB()#从数据库中调取已有的名称

write_to_SQL(selected_list,name_list_fromDB)#将新名称存入namelist表中

rename_result=rename_with_id(selected_list)#改名

print(rename_result)
fakelist_fromeDB=get_fakename_list_fromDB()
write_to_fakenamelist(rename_result,fakelist_fromeDB)#将fakename存入fakelist表中

fakelist_fromeDB=get_fakename_list_fromDB()

com=input('do you want to remame all the movies (y/n y to rename N to recover)')

if com not in ['y','Y'] and com in ['n','N']:
    recover_name(fakelist_fromeDB)#恢复名称

'''test'''

#fid=get_fakeid_fromDB('Q:test\新建文件夹\4#dat.dat')
#print(fid)

'''print(fakelist_fromeDB)
print(get_fakeid_fromDB(fakelist_fromeDB[1]))'''
#print(get_id_fromDB(name_list_fromDB[0]))



