__author__ = 'ilia'

from os.path import expanduser
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import Credentials
import json
from apiclient.discovery import build
import httplib2
from oauth2client.file import Storage
import argparse
from oauth2client import tools


cred_json=None
with open('./cred.json', 'r') as f:
    cred_json = json.load(f)

credentials = Credentials.from_json(cred_json)



secret_file_name = 'client_secret_274199158099-8uujipsmpu6bbo7nu09kasff9u0cpie5.apps.googleusercontent.com.json'
flow = flow_from_clientsecrets(expanduser('~') + '/.google/' + secret_file_name,
                               'https://www.googleapis.com/auth/drive',
                               'urn:ietf:wg:oauth:2.0:oob')

storage = Storage('./cred.json')
storage.put(credentials)

parser = argparse.ArgumentParser(parents=[tools.argparser])
flags = parser.parse_args()

credentials = tools.run_flow(flow, storage, flags)

auth_uri = flow.step1_get_authorize_url()
print 'auth uri: %s' % auth_uri
code = raw_input("Enter the code:\n")
credentials = flow.step2_exchange(code)

with open('./cred.json', 'w') as f:
    f.write(credentials.to_json())

http = httplib2.Http()
http = credentials.authorize(http)

service = build('drive', 'v3', http=http)

print "Program finished"



