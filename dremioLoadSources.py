#!/usr/bin/env python3
#
#
# Name         : dremioLoadSources.py
# Description  : Script to create an arbitrary number of sources and spaces
# Author       : Dremio
# Date         : Aug 17, 2020
# Version      : 1.0
# Notes        : 
#
# CHANGE LOG   :
#  Version 1.1 :
#          Date: 
#   Description: 
#

import sys
import os.path
import requests
import json
import argparse

# Configuration
debug = True
api_timeout = 60

# API endpoints
endpoint = "http://52.224.25.81:9047"
server_status = '/apiv2/server_status'
login_url = '/apiv2/login'
catalog_url = '/api/v3/catalog/'
userName = 'admin'
password = 'admin123'

def create(count):
	headers = {"Content-Type": "application/json"}
	payload = '{"userName": "' + userName + '","password": "' + password + '"}'
	response = requests.request("POST", endpoint + login_url, data=payload, headers=headers, timeout=api_timeout, verify=False)
	if response.status_code != 200:
		raise RuntimeError("Authentication error." + str(response.status_code))
	authtoken = '_dremio' + response.json()['token']

	#print("Token: " + authtoken)
	
	for index in range(int(count)):
		# Create Blob Source
		blobSourceName = 'pwcblobsource' + str(index)
		blobSourceJson = {
			"entityType": "source",
			"config": {
				"accountName": "manojstorageaccount1",
				"accessKey": "BqGtuvDOKRPLKuAdAQIGBTU5KI4EIHMEsS4v+z27FtLIk+8XDpbmHIziHYqYPnZKc2LmhQw3iGwgG0zNZ5BfDg=="
			},
			"type": "AZURE_STORAGE",
			"name": blobSourceName
		}

		sourcePayload = json.dumps(blobSourceJson)
		headers = {"Content-Type": "application/json", "Authorization": authtoken}
		response = requests.request("POST", endpoint + catalog_url, data=sourcePayload, headers=headers, timeout=api_timeout, verify=False)
		if response.status_code != 200:
			raise RuntimeError("API Error " + str(response.status_code) + " - " + str(response.reason))

		# Create ADLSv2 Source
		adlsSourceName = 'pwcadlssource' + str(index)
		adlsSourceJson = {
			"entityType": "source",
			"config": {
				"accountName": "manojstorageaccount2",
				"accessKey": "OB5jCoj1MFIrcc+K7XiIRU/vcpS7irelg3LjnoylV3QeMm+o9Gl6PjmBtRVTcIddHw/bX1ylAafnxU37q/xM1Q=="
			},
			"type": "AZURE_STORAGE",
			"name": adlsSourceName
		}

		sourcePayload = json.dumps(adlsSourceJson)
		headers = {"Content-Type": "application/json", "Authorization": authtoken}
		response = requests.request("POST", endpoint + catalog_url, data=sourcePayload, headers=headers, timeout=api_timeout, verify=False)
		if response.status_code != 200:
			raise RuntimeError("API Error " + str(response.status_code) + " - " + str(response.reason))

		# Create Space
		spaceName = 'pwcspace' + str(index)
		spaceJson ={
			"entityType": "space",
			"name": spaceName
		}
		spacePayload = json.dumps(spaceJson)
		headers = {"Content-Type": "application/json", "Authorization": authtoken}
		response = requests.request("POST", endpoint + catalog_url, data=spacePayload, headers=headers, timeout=api_timeout, verify=False)
		if response.status_code != 200:
			raise RuntimeError("API Error " + str(response.status_code) + " - " + str(response.reason))

def delete():
	headers = {"Content-Type": "application/json"}
	payload = '{"userName": "' + userName + '","password": "' + password + '"}'
	response = requests.request("POST", endpoint + login_url, data=payload, headers=headers, timeout=api_timeout, verify=False)
	if response.status_code != 200:
		raise RuntimeError("Authentication error." + str(response.status_code))
	authtoken = '_dremio' + response.json()['token']


	# Get Catalog
	headers = {"Content-Type": "application/json", "Authorization": authtoken}
	response = requests.request("GET", endpoint + catalog_url, headers=headers, timeout=api_timeout, verify=False)
	containers = response.json()['data']

	for container in containers:
		if container['containerType'] == 'SOURCE' or container['containerType'] == 'SPACE':
			endPoint = endpoint + catalog_url + container['id']
			response = requests.request("DELETE", endPoint, headers=headers, timeout=api_timeout, verify=False)
			if response.status_code != 200 and response.status_code != 204:
				print("API Error " + str(response.status_code) + " - " + str(response.reason))
			

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--create", help="Create Sources and Spaces", action='store', dest="count")
	parser.add_argument("-d", "--delete", help="Delete Sources and Spaces", action='store_true')
	args = parser.parse_args()

	if (args.delete):
		delete()
	elif (args.count):
		create(args.count)
	else:
		parser.error('No action requested, add --create or --delete')
	
