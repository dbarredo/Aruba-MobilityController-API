import requests
import urllib3
urllib3.disable_warnings()
from datetime import datetime
import stdiomask




def checkssid():

   try:
      inputip = input("\nEnter the IP of Controller: ")
      inputuser = input("Username: ")
      inputpass = stdiomask.getpass(prompt = 'Password: ')



      login = f"https://{inputip}:4343/v1/api/login"
      logout = f"https://{inputip}:4343/v1/api/logout"
      baseurl = f"https://{inputip}:4343/v1/"
      credentials = f"username={inputuser}&password={inputpass}"
      session = requests.session()
      response = session.post(login, data=credentials, verify=False, timeout=2)#login to controller via restconf
      cookie = response.json()['_global_result']['UIDARUBA']#GET the UIDARUBA only

      if response.status_code == 200:
         print(f"\nLast login: " + str(datetime.now()) + " " + f"from {inputip}")
         getapgroup = session.get(baseurl + 'configuration/object/ap_group?config_path=%2Fmm&UIDARUBA={}'.format(cookie),verify=False,
                                data=credentials) #get all of the ap group with parameters
         group = getapgroup.json()['_data']['ap_group']
         for grp in group:
             spliceapgrp = grp['profile-name']
             try:
               showapgroup = session.get(baseurl + 'configuration/showcommand?command=show+ap-group+{}&UIDARUBA={}'.format(spliceapgrp, cookie),verify=False,
                                         data=credentials)#get all of the ap group parameters with virtual ap
               showallvirtualap = showapgroup.json()['AP group {}'.format(spliceapgrp)][0:][:-21] #splice only the virtual ap's
               print("-" * 50)
               print('\n')
               print('AP Group : ' + spliceapgrp)
               for e in showallvirtualap:
                   virtualap_profile = e['Value']
                   if virtualap_profile == "N/A":
                      print('SSID : No ESSID')
                   else:
                       getallssid = session.get(baseurl + 'configuration/showcommand?command=show+wlan+virtual-ap+{}&UIDARUBA={}'.format(virtualap_profile,cookie),verify=False,
                                                data=credentials)#get all of the SSID profile with parameters
                       show_ssid_profile = getallssid.json()['Virtual AP profile {}'.format(virtualap_profile)][6]
                       ssid_variable = show_ssid_profile['Value']
                       ssid_profile_parameters = session.get(baseurl + 'configuration/showcommand?command=show+wlan+ssid-profile+{}&UIDARUBA={}'.format(ssid_variable, cookie),verify=False,
                                       data=credentials)#show ssid profile with parameters
                       show_ESSID = ssid_profile_parameters.json()['SSID Profile {}'.format(ssid_variable)][1]['Value']#splice to get only ESSID
                       print('SSID : ' + show_ESSID)
             except:
                 print("\t")
         print("-" * 50)



      else:
         print("UNAUTHORIZED USER")


      session.post(logout, timeout=2, verify=False)
      print("Logout Successful !")
      again()


   except requests.exceptions.ConnectionError:
    print("\nCould not connect to the controller")
    again()
   except SyntaxError:
    print("\nIncorrect Username or Password")
    again()


def again():
    repeat_again = input("\nDo you want to continue? \n Please type 'Y' for yes or 'N' for No : ")
    if repeat_again.upper() == 'Y':
        checkssid()
    elif repeat_again.upper() == 'N':
        print("\n\nThank you See you Later!")
    else:
        again()

checkssid()
