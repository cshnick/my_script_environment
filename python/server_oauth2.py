__author__ = 'ilia'
import httplib2

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.tools import run
from os.path import expanduser
from apiclient.http import MediaFileUpload

from apiclient import errors
# ...

def retrieve_all_files(service):
  """Retrieve a list of File resources.

  Args:
    service: Drive API service instance.
  Returns:
    List of File resources.
  """
  result = []
  page_token = None
  while True:
    try:
      param = {}
      if page_token:
        param['pageToken'] = page_token
      files = service.files().list(**param).execute()

      result.extend(files['items'])
      page_token = files.get('nextPageToken')
      if not page_token:
        break
    except errors.HttpError, error:
      print 'An error occurred: %s' % error
      break
  return result

def print_files_in_folder(service, folder_id):
  """Print files belonging to a folder.

  Args:
    service: Drive API service instance.
    folder_id: ID of the folder to print files from.
  """
  page_token = None
  while True:
    try:
      param = {}
      if page_token:
        param['pageToken'] = page_token
      children = service.children().list(
          folderId=folder_id, **param).execute()

      for child in children.get('items', []):
        print 'File Id: %s' % child['id']
      page_token = children.get('nextPageToken')
      if not page_token:
        break
    except errors.HttpError, error:
      print 'An error occurred: %s' % error
      break

def insert_file(service, title, description, parent_id, mime_type, filename):
  """Insert new file.

  Args:
    service: Drive API service instance.
    title: Title of the file to insert, including the extension.
    description: Description of the file to insert.
    parent_id: Parent folder's ID.
    mime_type: MIME type of the file to insert.
    filename: Filename of the file to insert.
  Returns:
    Inserted file metadata if successful, None otherwise.
  """
  media_body = MediaFileUpload(filename, mimetype=mime_type, resumable=True)
  body = {
    'title': title,
    'description': description,
    'mimeType': mime_type
  }
  # Set the parent folder.
  if parent_id:
    body['parents'] = [{'id': parent_id}]

  try:
    file = service.files().insert(
        convert=True,
        body=body,
        media_body=media_body).execute()

    # Uncomment the following line to print the File ID
    # print 'File ID: %s' % file['id']

    return file
  except errors.HttpError, error:
    print 'An error occured: %s' % error
    return None

def delete_file(service, file_id):
  """Permanently delete a file, skipping the trash.

  Args:
    service: Drive API service instance.
    file_id: ID of the file to delete.
  """
  try:
    service.files().delete(fileId=file_id).execute()
  except errors.HttpError, error:
    print 'An error occurred: %s' % error

priv_key=None
priv_path = expanduser('~/.ssh/test_googleApi.p12')
key_password='notasecret'
with open(priv_path, 'rb') as f:
    priv_key = f.read()

credentials = SignedJwtAssertionCredentials(
    service_account_name='274199158099-1ce7isbul75jq30n1jeug0825q09hvll@developer.gserviceaccount.com',
    private_key=priv_key,
    key_password=key_password,
    scope = 'https://www.googleapis.com/auth/drive'
)

http = httplib2.Http()
http = credentials.authorize(http)

service = build(serviceName='drive', version='v2', http=http)
delete_file(service, '1JMCcqKqS9g-q_v7wukfPYyfSArI6bLPv3ok_C5uFVaM')

insert_file(service,
            'test_1.csv',
            'Description',
            '0B2wRh5_FiqZ8flhKOUtGTjI3UUdmTnQ0Um1JMThjRlpnY2E1eGtvOWlyQmNIQUY4NDJxTUU',
            'text/csv',
            '/home/ilia/Prognoz/P7/DEV8/build64/bin/2015-06-02-16-14-12/diff.csv'
)

files = service.files().list().execute()
for file in files['items']:
    print "Title: %s" % file[u'title']
    print "\tKind: %s" % file[u'kind']
    print '\tMime: %s' % file['mimeType']
    print '\tId: %s' % file['id']

#print_files_in_folder(service, '0B2wRh5_FiqZ8flhKOUtGTjI3UUdmTnQ0Um1JMThjRlpnY2E1eGtvOWlyQmNIQUY4NDJxTUU') #Prognoz

print "End of application"

