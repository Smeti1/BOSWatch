#!/usr/bin/python
# -*- coding: cp1252 -*-

import logging
import time #timestamp for doublealarm
import re #Regex for validation

from includes import globals  # Global variables


def decode(freq, decoded):
	timestamp = int(time.time())#Get Timestamp                  
		
	#FMS Decoder Section    
	#check FMS: -> check CRC -> validate -> check double alarm -> log
	if "FMS:" in decoded:   
		logging.debug("recieved FMS")
			
		fms_service = decoded[19]       #Organisation
		fms_country = decoded[36]       #Bundesland
		fms_location = decoded[65:67]   #Ort
		fms_vehicle = decoded[72:76]    #Fahrzeug
		fms_status = decoded[84]        #Status
		fms_direction = decoded[101]    #Richtung
		fms_tsi = decoded[114:117]      #Taktische Kruzinformation
			
		if "CRC correct" in decoded: #check CRC is correct  
			fms_id = fms_service+fms_country+fms_location+fms_vehicle+fms_status+fms_direction #build FMS id
			if re.search("[0-9a-f]{8}[0-9a-f]{1}[01]{1}", fms_id): #if FMS is valid
				if fms_id == globals.fms_id_old and timestamp < globals.fms_time_old + globals.config.getint("BOSWatch", "fms_double_ignore_time"): #check for double alarm
					logging.info("FMS double alarm: %s within %s second(s)", globals.fms_id_old, timestamp-globals.fms_time_old)
					globals.fms_time_old = timestamp #in case of double alarm, fms_double_ignore_time set new
				else:
					logging.info("FMS:%s Status:%s Richtung:%s TKI:%s", fms_id[0:8], fms_status, fms_direction, fms_tsi)
					data = {"fms":fms_id[0:8], "status":fms_status, "direction":fms_direction, "tsi":fms_tsi}
					from includes import pluginHandler
					pluginHandler.throwAlarm("FMS",freq,data)
					
					globals.fms_id_old = fms_id #save last id
					globals.fms_time_old = timestamp #save last time	
			else:
				logging.warning("No valid FMS: %s", fms_id)    
		else:
			logging.warning("FMS CRC incorrect")
				

	#ZVEI Decoder Section
	#check ZVEI: -> validate -> check double alarm -> log     
	if "ZVEI2:" in decoded:
		logging.debug("recieved ZVEI")			
		from includes.decoders import zvei
		zvei.decode(freq, decoded)
		
	#POCSAG Decoder Section
	#check POCSAG -> validate -> check double alarm -> log      
	if "POCSAG" in decoded:
		logging.debug("recieved POCSAG")				
		from includes.decoders import poc
		poc.decode(freq, decoded)