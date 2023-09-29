#Inconsistent

import json
import requests
from pprint import pprint as pp
import pandas as pd
import urllib3
import numpy as np
import certifi
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

http = urllib3.PoolManager(
    cert_reqs="CERT_REQUIRED",
    ca_certs=certifi.where()
)

url = "https://10.19.64.126/api/graphql"
headers = {
    'Authorization': 'Bearer N2QyZTk4ZGYtNDA2Yy00Njk5LTk4ZWItZGYyNTllOTg5NDYxOmZmYjdkZGZjLTAzOGEtNDE5NS04ZmNjLWY4YzM3OGQ1M2Y2Mw=='
}


category = ["Virtual VTEP -------------------- ","Virtual MAC --------------------- ","IP Address Virtual -------------- ","VARP & IP Address Virtual ------- ","VLAN VNI Mappings ---------------","FloodList -----------------------"]
result1 = ["-" for i in range(len(category))]
detail1 = ["" for i in range(len(category))]
result2 = ["-" for i in range(len(category))]
detail2 = ["" for i in range(len(category))]
result3 = ["-" for i in range(len(category))]
detail3 = ["" for i in range(len(category))]
dict1 = {"Category -----------------------":category,'Result -----------------------':result1,'Detail -----------------------':detail1}
dict2 = {"Category -----------------------":category,'Result -----------------------':result2,'Detail -----------------------':detail2}
dict3 = {"Category -----------------------":category,'Result -----------------------':result3,'Detail -----------------------':detail3}
# finaldict={"showtech1":dict1,"showtech2":dict2,"showtech3":dict3}
#df = pd.DataFrame(dict)

def getParsedData(serialNumber, timestamp):
    
    query = """query ($serialNumber:String!,$fileTimeStamp:Time!) {
         showtech(serialNumber:$serialNumber , fileTimestamp:$fileTimeStamp ) 
           { id 
             name
             parsedDataJson}
           }
          """

    variables = {
  			"serialNumber": serialNumber,
  			"fileTimeStamp": timestamp
		}	

    
    response = requests.post(url, json={'query': query, 'variables':variables}, headers=headers, verify=False)

    data=json.loads(response.text)

    ShowtechDict={
    "VirtualVTEP":"",
    "VtepIP":"",
    "FloodList":"",
    "VLANVNIMappings":{},
    "VirtualMAC":"",
    "VirtualRouterAddress":[],
    "IpAddressVirtual":""
    }
    showInterfaceVxlan=data['data']['showtech']['parsedDataJson']['commands']['show_interface_vxlan']
    if showInterfaceVxlan.get('virtual_vtep_address')!=None:
     ShowtechDict['VirtualVTEP']=showInterfaceVxlan['virtual_vtep_address']
    ShowtechDict['VLANVNIMappings']=showInterfaceVxlan['vlan_vni_mappings']
    ShowtechDict['FloodList']=showInterfaceVxlan['headend_replication_flood_vtep_list']
    ShowtechDict['VtepIP']=showInterfaceVxlan['source_interface']['address']

    ShowIpVirtualRouterVRFAll=data['data']['showtech']['parsedDataJson']['commands']['show_ip_virtual_router_vrf_all']
    ShowtechDict['VirtualMAC']=ShowIpVirtualRouterVRFAll['mac_address']
    if ShowIpVirtualRouterVRFAll.get('virtual_ip_address')!=None:
        ShowtechDict['VirtualRouterAddressl']=ShowIpVirtualRouterVRFAll['virtual_ip_address']
 

    ShowRunningConfig=data['data']['showtech']['parsedDataJson']['commands']['show_running_config']['interfaces']['list']
    if ShowRunningConfig.get('Vlan200')!=None:
       txt=ShowRunningConfig['Vlan200'][0]
       txt=txt.split()
       ShowtechDict['IpAddressVirtual']=txt[3]

    ShowRunningConfig=data['data']['showtech']['parsedDataJson']['commands']['show_running_config']
    ShowtechDict['Hostname']=ShowRunningConfig['hostname']
    return ShowtechDict
   




showtechs = { 'st1': {'serial_number': '43DB57052B47A4DBDEF8184A20114CC3', 'timestamp': '2023-04-10T08:12:20Z'},
				'st2': {'serial_number': 'A77A5D79984D54D9B4B374BA38DFB318', 'timestamp': '2023-04-10T08:13:33Z'},  
                'st3': {'serial_number': '2B0804742EBF64ACE5070D7D2819C3F9', 'timestamp': '2023-04-10T07:40:02Z'}

}

data1=getParsedData(showtechs['st1']['serial_number'], showtechs['st1']['timestamp'])
data2=getParsedData(showtechs['st2']['serial_number'], showtechs['st2']['timestamp'])
data3=getParsedData(showtechs['st3']['serial_number'], showtechs['st3']['timestamp'])

# print(data1['VLANVNIMappings'], data1['Hostname'])
# print(data2['VLANVNIMappings'], data2['Hostname'])
# print(data3['VLANVNIMappings'], data3['Hostname'])

# print("\nVLAN to VNI Mappings\n")


Showtech1VLANVNIMapping={
    'Static':data1['VLANVNIMappings']['static'],
    'Dynamic':data1['VLANVNIMappings']['dynamic']

}


print("\nPlease find the output files generated in your local directory")
# print("\nVLAN VNI\n")

for i in data1['VLANVNIMappings']:
    if i in data2['VLANVNIMappings']:
        if i in data3['VLANVNIMappings']:
            if data1['VLANVNIMappings'][i]!=data2['VLANVNIMappings'][i]!=data3['VLANVNIMappings']:
                # print(i)
                # print("Warning: VNI mappings corresponding to VLAN", data2['VLANVNIMappings'][i], "is inconsistent across the three hosts.")
                detail1[4]="VNI mappings corresponding to VLAN", data1['VLANVNIMappings'][i], "is inconsistent across the VTEPs."
                detail2[4]="VNI mappings corresponding to VLAN", data2['VLANVNIMappings'][i], "is inconsistent across the VTEPs."
                detail3[4]="VNI mappings corresponding to VLAN", data3['VLANVNIMappings'][i], "is inconsistent across the VTEPs."
                result1[4]="WARN ----------"
                result2[4]="WARN ----------"
                result3[4]="WARN ----------"

        else:
            detail3[4]="Vlan", i, "is missing"
            result3[4]="WARN"
    else:
        detail2[4]="Vlan", i, "is missing"
        result2[4]="WARN"


isPresent=True
if data1['VirtualVTEP']=="" :
   detail1[0]="Virtual VTEP is not configured on hostname "+ data1['Hostname']
   isPresent=False
   result1[0]='WARN -------------'


if data2['VirtualVTEP']=="":
    detail2[0]="Virtual VTEP is not configured on hostname " + data2['Hostname']
    isPresent=False
    result2[0]='WARN -------------'

if data3['VirtualVTEP']=="":
    detail3[0]="Virtual VTEP is not configured on hostname " + data3['Hostname']
    isPresent=False
    result3[0]='WARN -------------'


isPresent=True
if data1['VirtualMAC']==None :
   detail1[1]="Virtual MAC is not configured on hostname "+ data1['Hostname']
   isPresent=False
   result1[1]="WARN -------------"


if data2['VirtualMAC']==None:
   detail2[1]="Virtual MAC is not configured on hostname " + data2['Hostname']
   isPresent=False
   result2[1]='WARN -------------'


if data3['VirtualMAC']==None:
    detail3[1]="Virtual MAC is not configured on hostname "+ data3['Hostname']
    isPresent=False
    result3[1]='WARN -------------'

if isPresent:
    if data1['VirtualMAC']==data2['VirtualMAC']==data3['VirtualMAC']:
        detail1[1]="Virtual MACs are configured correctly"
        detail2[1]="Virtual MACs are configured correctly"
        detail2[1]="Virtual MACs are configured correctly"
        result1[1]="OK"
        result2[1]="OK"
        result3[1]="OK"

    else:
        detail1[1]="Virtual MACs are inconsistent\n"
        detail2[1]="Virtual MACs are inconsistent\n"
        detail3[1]="Virtual MACs are inconsistent\n"


#IP Address Virtual

isPresent=True
if data1['IpAddressVirtual']=="":
    detail1[2]="IP Address Virtual is not configured on hostname "+ data1['Hostname']
    result1[2]="WARN --------"
    isPresent=False

print(data2['IpAddressVirtual'])
if len(data2['IpAddressVirtual'])==0:
    detail2[2]="IP Address Virtual is not configured on hostname " + data2['Hostname']
    result2[2]="WARN -------------"
    isPresent=False
 
if data3['IpAddressVirtual']=="":
    detail3[2]="IP Address Virtual is not configured on hostname  "+ data3['Hostname']
    result3[2]="WARN --------"
    isPresent=False

if isPresent:
     if data1['IpAddressVirtual']==data2['IpAddressVirtual']==data3['IpAddressVirtual']:
        detail1[2]="IP Address Virtual is configured correctly"
        detail2[2]="IP Address Virtual is configured correctly"
        detail3[2]="IP Address Virtual is configured correctly"
        result1[2]="OK"
        result2[2]="OK"
        result3[2]="OK"


#VLAN VNI

# for i in data1['VLANVNIMappings']:
#     if i in data2['VLANVNIMappings']:
#         if i in data3['VLANVNIMappings']:
#             if data1['VLANVNIMappings'][i]!=data2['VLANVNIMappings'][i]!=data3['VLANVNIMappings']:
#                 # print("VNI mappings corresponding to VLAN", i, "is inconsistent across the hosts.")
#     #     else:
#     #         print("Vlan", i, "is missing from Hostname 3")
#     # else:
#     #     print("Vlan", i, "is missing from Hostname 2") 



if len(data1['VirtualRouterAddress'])!=0 and data1['IpAddressVirtual']!='':
    result1[3]="WARN"
    detail1[3]="Warning: Both VirtualRouterAddress and IpAddressVirtual are configured on",data1['Hostname']
if len(data2['VirtualRouterAddress'])!=0 and data2['IpAddressVirtual']!='':
    result2[3]="WARN"
    detail2[3]="Warning: Both VirtualRouterAddress and IpAddressVirtual are configured on" , data2['Hostname']
if len(data3['VirtualRouterAddress'])!=0 and data3['IpAddressVirtual']!='':
    result3[3]="WARN"
    detail3[3]="Warning: Both VirtualRouterAddress and IpAddressVirtual are configured on" ,data3['Hostname']





#Floodlist
for i in data1['FloodList']:
    data1['FloodList'][i].append(data1['VtepIP'])
    data1['FloodList'][i].sort()
    if i in data2['FloodList']:
          data2['FloodList'][i].append(data2['VtepIP'])
          data2['FloodList'][i].sort()
          if i in data3['FloodList']:
             data3['FloodList'][i].append(data3['VtepIP'])
             data3['FloodList'][i].sort()
             if data1['FloodList'][i]!=data2['FloodList'][i]:
                detail1[5]="FloodList is inconsistent across the VTEPs ", data1['FloodList'][i]
                detail2[5]="FloodList is inconsistent across the VTEPs " , data2['FloodList'][i]
                result1[5]="WARN ---------"
                result2[5]="WARN ---------"
            #  else:
            # #    print("OK for",data1['FloodList'][i])
             if data2['FloodList'][i]!=data3['FloodList'][i]:
                detail3[5]="FloodList is inconsistent across the VTEPs ", data3['FloodList'][i]
                detail2[5]="FloodList is inconsistent across the VTEPs " , data2['FloodList'][i]
                result3[5]="WARN ---------"
                result2[5]="WARN ---------"
            #  else:
            #     #  print("OK for",data2['FloodList'][i])
             if data1['FloodList'][i]!=data3['FloodList'][i]:
                  detail3[5]="FloodList is inconsistent across the VTEPs ", data3['FloodList'][i]
                  detail1[5]="FloodList is inconsistent across the VTEPs " , data1['FloodList'][i]
                  result3[5]="WARN ---------"
                  result1[5]="WARN ---------"
            #  else:
            #     #  print("OK for",data3['FloodList'][i])
              


for i in range(len(category)):
    if result1[i]=='-':
     result1[i]="OK"
for i in range(len(category)):
    if result2[i]=='-':
     result2[i]="OK"
for i in range(len(category)):
    if result3[i]=='-':
     result3[i]="OK"


# print(result1)
# print(detail1)
# print(result2)
# print(detail2)
# print(result3)
# print(detail3)


df1=pd.DataFrame(dict1)
df1.Name=data1['Hostname']
df2=pd.DataFrame(dict2)
df2.Name=data2['Hostname']
df3=pd.DataFrame(dict3)
df3.Name=data3['Hostname']
list_of_dfs=[df1,df2,df3]
with open('/Users/diya.sabu/Desktop/vxlanproject/file2.csv','a') as f:
    for df in list_of_dfs:
        f.write("HostName: "+df.Name)
        f.write("\n")
        df.to_csv(f)
        f.write("\n")


floodlistresult=[]

with open("/Users/diya.sabu/Desktop/vxlanproject/filefloodlist.txt","w") as floodlistresultfile:

    h1=data1['FloodList']['100']
    # print(h1)
    h2=data1['FloodList']['200']
    # h1.append(data1['VtepIP'])
    # h2.append(data1['VtepIP'])
    h1.sort()
    h2.sort()
    # print(h1)
    # print(h2)

    floodlistresult.append(str("Floodlist for "+str(data1['Hostname']) +"\n"+str(data1['FloodList'])))

    h1=data2['FloodList']['100']
    #h1.append(data2['VtepIP'])
    h1.sort()

    floodlistresult.append(str("Floodlist for "+str(data2['Hostname'])+"\n"+str( data2['FloodList'])))

    h1=data3['FloodList']['100']
    h2=data3['FloodList']['200']
    # h1.append(data3['VtepIP'])
    # h2.append(data3['VtepIP'])
    h1.sort()
    h2.sort()

    floodlistresult.append(str("Floodlist for "+str(data3['Hostname'])+"\n"+str(data3['FloodList'])+"\n"))


    # Compare list1 and list2
    # floodlistresult.append("FloodList missing in L1 when compared with L2")
    # for key in data2['FloodList'].keys():
    #     if key in data1['FloodList']:
    #         # print("YES")
    #         for item in data2['FloodList'][key]:
    #             # print(item)
    #             if item not in data1['FloodList'][key]:
    #                 # print("YESS")
    #                 floodlistresult.append(str("Vlan: {key}, Vtep IP: {item}"))
    #     else:
    #         for item in data2['FloodList'][key]:
    #             floodlistresult.append(f"Vlan: {key}, Vtep IP: {item}")

    # Compare list1 and list3
    floodlistresult.append("FloodList missing in L1 when compared with L3::")
    for key in data3['FloodList'].keys():
        if key in data1['FloodList']:
            for item in data3['FloodList'][key]:
                if item not in data1['FloodList'][key]:
                    floodlistresult.append(f"Vlan: {key}, Vtep IP: {item}")
        else:
            for item in data3['FloodList'][key]:
                floodlistresult.append(f"Vlan: {key}, Vtep IP: {item}")

    # Compare list2 and list1
    floodlistresult.append("FloodList missing in L2 when compared with L1:")
    for key in data1['FloodList'].keys():
        if key in data2['FloodList']:
            for item in data1['FloodList'][key]:
                if item not in data2['FloodList'][key]:
                    floodlistresult.append(f"Vlan: {key}, Vtep IP: {item}")
        else:
            for item in data1['FloodList'][key]:
                floodlistresult.append(f"Vlan: {key}, Vtep IP: {item}")

    # Compare list2 and list3
    floodlistresult.append("FloodList missing in L2 when compared with L3:")
    for key in data3['FloodList'].keys():
        if key in data2['FloodList']:
            for item in data3['FloodList'][key]:
                if item not in data2['FloodList'][key]:
                    floodlistresult.append(f"Vlan: {key}, Vtep IP: {item}")
        else:
            for item in data3['FloodList'][key]:
                floodlistresult.append(f"Vlan: {key}, Vtep IP: {item}")

    # Compare list3 and list1
    # floodlistresult.append("FloodList missing in L3 when compared with L1:")
    # for key in data1['FloodList'].keys():
    #     if key in data3['FloodList']:
    #         for item in data1['FloodList'][key]:
    #             if item not in data3['FloodList'][key]:
    #                 floodlistresult.append(f"Vlan: {key}, Vtep IP: {item}")
    #     else:
    #         for item in data1['FloodList'][key]:
    #             floodlistresult.append(f"Vlan: {key}, Vtep IP: {item}")

    # # Compare list3 and list2
    # floodlistresult.append("FloodList missing in L3 when compared with L2:")
    # for key in data2['FloodList'].keys():
    #     if key in data3['FloodList']:
    #         for item in data2['FloodList'][key]:
    #             if item not in data3['FloodList'][key]:
    #                 floodlistresult.append(f"Vlan: {key}, Vtep IP: {item}")
    #     else:
    #         for item in data2['FloodList'][key]:
    #             floodlistresult.append("Vlan: {key} + Vtep IP: {item}")

# print(floodlistresult)

with open('/Users/diya.sabu/Desktop/vxlanproject/floodlist_detail2.txt','a') as f:
   for i in floodlistresult:
       f.write(i)
       f.write("\n")

       