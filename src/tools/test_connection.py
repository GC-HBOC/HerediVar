import requests
from requests.auth import HTTPProxyAuth
import urllib3
import logging
import os

logging.basicConfig(level=logging.DEBUG)

payload = {
        "client_id": "HerediVar_Frontend",
        "client_secret": "JXXO04px1bDIx28dji9dqZrrOkt2Cas4",
        "grant_type": "password",
        "username": "testuser",
        "password": "12345",
        "Content-Type": "application/x-www-form-urlencoded"
    }
http = "http://srv023.img.med.uni-tuebingen.de:8080/realms/HerediVar/protocol/openid-connect/token"
#proxies = {
#    "http": "http://ahdoebm1:DaSteigtdieStimmung03!@httpproxy.zit.med.uni-tuebingen.de:88"
#}
#response = requests.post(http, data=payload, proxies=proxies)
#print(response)
#print(response.request.url)
#print(response.request.body)
##print(response.request.headers)





s = requests.Session()

proxies = {
  "http": "http://httpproxy.zit.med.uni-tuebingen.de:88",
  "https": "http://httpproxy.zit.med.uni-tuebingen.de:88"
}

auth = HTTPProxyAuth("ahdoebm1", os.environ.get('HTTP_PROXY_PW'))

s.proxies = proxies
s.auth = auth        # Set authorization parameters globally

#response = s.post(http, data=payload)
#response = s.get('http://srv023.img.med.uni-tuebingen.de:8080/realms/HerediVar/.well-known/openid-configuration')
#print(response)
#print(response.request.url)
#print(response.request.body)
#print(response.request.headers)

ext_ip = requests.get('http://checkip.dyndns.org')
print(ext_ip)

response = requests.get('http://srv023.img.med.uni-tuebingen.de:8080/realms/HerediVar/.well-known/openid-configuration')


#curl -d "client_id=app-authz-vanilla" -d "client_secret=5kgLB3Q42BfvqHcg7YsGMGES6S3D1LmW" -d "username=testuser" -d "password=12345" -d "grant_type=password" "http://localhost:8080/realms/quickstart/protocol/openid-connect/token"

#a = a.json()
#print(a['access_token'])

#test access_token
#http2 = 'http://127.0.0.1:8080/admin/realms/HerediVar/events'
#header = {
#    'Authorization': "Bearer " + a['access_token']
#}
#b = requests.request("GET", http2, headers=header)
#b = b.json()