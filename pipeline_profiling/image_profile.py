import os
import time
import json
import urllib.parse
from aqua.aqua import Aqua
import hvac

# get Aqua csp auth into from hashi vault
vault_url = 'http://192.0.2.8:5005'
client = hvac.Client()
client = hvac.Client(url=vault_url, token=os.environ['VAULT_TOKEN'])
data = client.read('jeffsbooks/aqua_csp')['data']
id = data['username']
password = data['password']

profiling_duration = 5 # in seconds
profile_name = 'jeffsbooks_runtime_2'
registry_name = 'GCR'  #friendy name for registry added in Aqua CSP
repository_name = 'us.gcr.io/test-bbfc8/jeffsbooks'
repository_name_encoded = urllib.parse.quote(repository_name, safe='')
aqua_csp_host = '192.0.2.8'
aqua_csp_port = '8080'


aqua = Aqua(id=id, password=password, host=aqua_csp_host, port=aqua_csp_port, using_ssl=False)   #pip install aqua
time.sleep(profiling_duration)    #used as an example. Typically would end after test suites and simulated behaviour.
resp = aqua.end_profiling_session(registry_name, repository_name_encoded)                 #step 1: end profiling session
profile = aqua.get_suggested_profile(registry_name, repository_name_encoded)              #step 2: get suggested profile
profile['name'] = profile_name

profiles = aqua.list_profiles()
operation = 'created'

if profile_name not in [x['name'] for x in profiles['result']]:
    resp = aqua.create_profile(json.dumps(profile))                           #step 3: use suggested profile to create image runtime policy
else:
    operation = 'updated'                                                     # or
    resp = aqua.modify_profile(profile_name, json.dumps(profile))             #step 3: use suggested profile to modify existing image runtime policy

print(f'Profile {profile_name} successfully {operation}.')
resp = aqua.attach_profile(registry_name, repository_name_encoded, profile_name)   #step 4: attach image runtime profile to a repository

if resp.content.decode('utf-8')  == '':
    print(f'Profile {profile_name} successfully attached to {registry_name}/{repository_name}.')
else:
    print(f'Error in attaching profile {profile_name} to {registry_name}/{repository_name}.')