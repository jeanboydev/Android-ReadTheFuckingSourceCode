import xml.dom.minidom
import os
from subprocess import call
 
#downloaded source path
rootdir = "D:/Develop/Android/BaseCode/android_source_code/Android5.1.1"
#rootdir = "D:/Develop/Android/BaseCode/android_source_code/sync"
 
#git program path
git = "C:/Develop/Git/bin/git.exe"
 
dom = xml.dom.minidom.parse("D:/Develop/Android/BaseCode/manifest/default.xml")
root = dom.documentElement
 
#prefix = git + " clone https://android.googlesource.com/"
prefix = git + " clone https://aosp.tuna.tsinghua.edu.cn/"
suffix = ".git"  

if not os.path.exists(rootdir):  
    os.mkdir(rootdir)  

for node in root.getElementsByTagName("project"):  
    os.chdir(rootdir)  
    d = node.getAttribute("path")  
    last = d.rfind("/")  
    if last != -1:  
        d = rootdir + "/" + d[:last]  
        if not os.path.exists(d):  
            os.makedirs(d)  
        os.chdir(d)  
    cmd = prefix + node.getAttribute("name") + suffix  
    call(cmd)
