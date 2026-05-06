#Carriage Calculation is been changed since 1.0.27##############
#Beam Number for Wedge and tray sequence is been updated for non sequenceal beam numbers-1.0.26  -*-
#(15032024) 2.0.13v Dynamic carriage calculation is been implemented as per tamilarans's formula excel sheet
#This implementaion is for SMLC to recalculate the CP time which has  value as '0', implemented in BeamSquenceControlPointSequence section
#IsoWedgeTime calculation is been modified for (final cumulative weight) v1.1.0
#Carriage Calculation condition is been added in the Final carriage position v1.1.5
#Patient Support Angle data is been included in all control points as per data from TPS V1.1.6

# -*- coding: utf-8 -*-

import sys
from builtins import print

import pydicom
from datetime import datetime
import pyodbc
import logging
from pydicom.dataset import Dataset
import codecs
import numpy as np
import math

offlineIP = ""
CCBtreatmentIP = ""
OfflinevalSQL = []
CCBvalSQL = []
machinevalSQL = []
machineDB = ""

def getOfflineData(ID0, ArgList,WorkId_FKey):

    getDB = ID0
    txtfile = ArgList
    readtxtfile=open(txtfile)
    Args=readtxtfile.readlines()

    if(ID0 == 0 or ID0 == 2):
        MachineName = Args[5].strip()
        DeviceNo = Args[6].strip()
        OfflinevalSQL = (Args[7].strip()).split(";")
        CCBvalSQL = []
        RTID = Args[2].strip()##2
        dicom_file = Args[1].strip()##1
        machinevalSQL = (Args[8].strip()).split(";")
        SiteNo=Args[3].strip()##3
        PhaseNo =Args[4].strip()##4

        
    elif(ID0 == 1):
        MachineName = Args[6].strip()
        DeviceNo = Args[7].strip()
        OfflinevalSQL = (Args[8].strip()).split(";")
        CCBvalSQL = (Args[9].strip()).split(";")
        RTID = Args[3].strip()
        dicom_file = Args[1].strip()
        SiteNo=Args[4].strip()
        PhaseNo =Args[5].strip()
    print("Arguments ", OfflinevalSQL)
    print("Patient ID",RTID)
    now = datetime.now()
    fractionNo=1
    Plan_Type=""
    Beam_Type=[]
    listset1=[]
    listset2=[]

    sitedata = str(SiteNo)
    phasedata = str(PhaseNo)
    fractiondata = ("_FG"+str(fractionNo))
    combinedata = sitedata + phasedata + fractiondata
    ss4 = RTID+"_"+ combinedata
    RefIDdata = "S"+ sitedata +"_P"+ phasedata
    RefID = RTID+"_"+ RefIDdata

    # print("RefID",sitedata,phasedata,RefIDdata,RefID)

    # print("DICOM file path: ",dicom_file)
    ds = pydicom.read_file(dicom_file)

    try:
        DeviceSerialNo  = str(ds.quence.DeviceSerialNumber)

        if(DeviceSerialNo == "" or DeviceSerialNo == " "):
            DeviceSerialNo = DeviceNo
        
    except:
        DeviceSerialNo = DeviceNo

##    print("Treatment Machine & DeviceSerialNo:",MachineName, DeviceSerialNo)

    if(OfflinevalSQL[0] == "local"):
        offlineIP = "(local)"
    else:
        offlineIP = OfflinevalSQL[0]

##    print("CCBvalSQL len",len(CCBvalSQL))
    if(len(CCBvalSQL) > 1):
        if(CCBvalSQL[0] == "local"):
            CCBtreatmentIP = "(local)"
        else:
            CCBtreatmentIP = CCBvalSQL[0]

    print("Treatment Machine & DeviceSerialNo:",MachineName,DeviceSerialNo)
    
    con_string = "Driver={SQL Server};SERVER="+offlineIP+";DATABASE="+OfflinevalSQL[1]+";uid="+OfflinevalSQL[2]+";pwd="+OfflinevalSQL[3]+""
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()
    tsql = "SELECT * FROM MachineSettings WHERE ManufacturerModelName = '"+MachineName+"' and DeviceSerialNumber = '"+DeviceSerialNo+"'"
    cursor.execute(tsql)
    row = cursor.fetchone()
    cnxn.close()

    con_string = "Driver={SQL Server};SERVER=" + offlineIP + ";DATABASE=" + OfflinevalSQL[1] + ";uid=" + OfflinevalSQL[2] + ";pwd=" + OfflinevalSQL[3] + ""
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()
    machineSettingsSection1 = "SELECT * FROM MachineSettingsSection1 WHERE ManufacturerModelName = '" + MachineName + "' and DeviceSerialNumber = '" + DeviceSerialNo + "'"
    cursor.execute(machineSettingsSection1)
    row1 = cursor.fetchone()
    cnxn.close()

    print("MachineSettings Database Connected")

    ###################Connection String***********************
        
    if(int(getDB)==1):
        con_string = "Driver={SQL Server};SERVER="+CCBtreatmentIP+";DATABASE="+CCBvalSQL[1]+";uid="+CCBvalSQL[2]+";pwd="+CCBvalSQL[3]+""

    elif(int(getDB)==2):
        if(machinevalSQL[0] == "local"):
            machineDB = "(local)"
        else:
            machineDB = machinevalSQL[0]
        con_string = "Driver={SQL Server};SERVER="+machineDB+";DATABASE="+machinevalSQL[1]+";uid="+machinevalSQL[2]+";pwd="+machinevalSQL[3]+""

    elif(int(getDB)==0):
        if (machinevalSQL[0] == "local"):
            machineDB = "(local)"

        else:
            machineDB = machinevalSQL[0]
        con_string = "Driver={SQL Server};SERVER="+machineDB+";DATABASE="+machinevalSQL[1]+";uid="+machinevalSQL[2]+";pwd="+machinevalSQL[3]+""
        # con_string = "Driver={SQL Server};SERVER=(local);DATABASE=Temp_Treatment;uid=sa;pwd=panacea"
        con_string = "Driver={SQL Server};SERVER="+machineDB+";DATABASE="+machinevalSQL[1]+";uid="+machinevalSQL[2]+";pwd="+machinevalSQL[3]+""
    # print("database_connectio",con_string)
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()

    ###TreatmentMachineSequence###
    TMachie_FKey = []
    try:
        for i in range(0, len(ds.TreatmentMachineSequence)):
            strDeviceSerialNumber = ""
            strManufacturer = ""
            strInstitutionName = ""
            strManufacturerModelName = ""
            strTreatmentMachineName = ""
            try:
                strDeviceSerialNumber = str(ds.TreatmentMachineSequence[i].DeviceSerialNumber)
            except:
                strDeviceSerialNumber = ""

            try:
                strManufacturer = str(ds.TreatmentMachineSequence[i].Manufacturer)
            except:
                strManufacturer = ""

            try:
                strInstitutionName = str(ds.TreatmentMachineSequence[i].InstitutionName)
            except:
                strInstitutionName = ""
            try:
                strManufacturerModelName = str(ds.TreatmentMachineSequence[i].ManufacturerModelName)
            except:
                strManufacturerModelName = ""
            try:
                strTreatmentMachineName = str(ds.TreatmentMachineSequence[i].TreatmentMachineName)
            except:
                strTreatmentMachineName = ""

            SQLCommand = "insert into TreatmentMachineSequences(Manufacturer00080070,InstitutionName00080080,ManufacturerModelName00081090,DeviceSerialNumber00181000,TreatmentMachineName300A00B2," \
                         "WorkRefId)" \
                         "VALUES (?, ?, ?, ?, ?, ?)"
            args = (strManufacturer, \
                    strInstitutionName, \
                    strManufacturerModelName, \
                    strDeviceSerialNumber, \
                    strTreatmentMachineName, \
                    WorkId_FKey)
            cursor.execute(SQLCommand, args)
            TMachie_FKey.append(cursor.execute("select @@IDENTITY from TreatmentMachineSequences").fetchone()[0])
        print("TreatmentMachineSequence updated", i + 1)
        cnxn.commit()
    except Exception as e:
        print("TreatmentMachineSequence error ", i + 1,e)
        pass


    ###SourceSequence###
    Source_FKey = []
    try:
        for i in range(len(ds.SourceSequence)):
            # Initialize variables
            strSourceSerialNumber = ""
            strSourceNumber = ""
            strSourceType = ""
            strSourceIsotopeName = ""
            strSourceIsotopeHalfLife = ""
            strSourceStrengthUnits = ""
            strReferenceAirKermaRate = ""
            strSourceStrengthReferenceDate = ""
            strSourceStrengthReferenceTime = ""
            try:
                strSourceSerialNumber = str(ds.SourceSequence[i].SourceSerialNumber)
            except Exception as e:
                print("An error occurred while processing strSourceSerialNumber:", e)

            try:
                strSourceNumber = str(ds.SourceSequence[i].SourceNumber)
            except Exception as e:
                print("An error occurred while processing strSourceNumber:", e)

            try:
                strSourceType = str(ds.SourceSequence[i].SourceType)
            except Exception as e:
                print("An error occurred while processing strSourceType:", e)

            try:
                strSourceIsotopeName = str(ds.SourceSequence[i].SourceIsotopeName)
            except Exception as e:
                print("An error occurred while processing strSourceIsotopeName:", e)
            try:
                strSourceIsotopeHalfLife = str(ds.SourceSequence[i].SourceIsotopeHalfLife)
            except Exception as e:
                print("An error occurred while processing strSourceIsotopeHalfLife:", e)

            try:
                strSourceStrengthUnits = str(ds.SourceSequence[i].SourceStrengthUnits)
            except Exception as e:
                print("An error occurred while processing strSourceStrengthUnits:", e)
            try:
                strReferenceAirKermaRate = str(ds.SourceSequence[i].ReferenceAirKermaRate)
            except Exception as e:
                print("An error occurred while processing strReferenceAirKermaRate:", e)

            try:
                source_date = ds.SourceSequence[i].SourceStrengthReferenceDate
                if source_date:
                    clean_date = str(source_date).replace('.0', '')
                    strSourceStrengthReferenceDate = datetime.strptime(clean_date, '%Y%m%d').strftime(
                        '%Y-%m-%d')
                else:
                    strSourceStrengthReferenceDate = None
            except Exception as e:
                print("An error occurred while processing SourceStrengthReferenceDate:", e)
            try:
                source_time = ds.SourceSequence[i].SourceStrengthReferenceTime
                if source_time:
                    clean_time = str(source_time).replace('.0', '')
                    strSourceStrengthReferenceTime = datetime.strptime(clean_time, '%H%M%S').strftime(
                        '%H:%M:%S')
                else:
                    strSourceStrengthReferenceTime = None
            except Exception as e:
                print("An error occurred while processing SourceStrengthReferenceTime:", e)

            SQLCommand = "INSERT INTO SourceSequences (SourceSequence300A0210,SourceSerialNumber30080105, SourceNumber300A0212,SourceType300A0214, SourceIsotopeName300A0226,SourceIsotopeHalfLife300A0228,SourceStrengthUnits300A0229,ReferenceAirKermaRate300A022A,SourceStrengthReferenceDate300A022C,SourceStrengthReferenceTime300A022E, WorkRefId,TreatmentMachineRefId) " \
                         "VALUES (?, ?, ?, ?, ?,?,?,?,?,?,?,?)"
            args = ("SourceSequence"+str(i+1),\
            strSourceSerialNumber ,\
            strSourceNumber,\
            strSourceType ,\
            strSourceIsotopeName,\
            strSourceIsotopeHalfLife,\
            strSourceStrengthUnits ,\
            strReferenceAirKermaRate ,\
            strSourceStrengthReferenceDate,\
            strSourceStrengthReferenceTime,\
                WorkId_FKey, \
                TMachie_FKey[i])

            cursor.execute(SQLCommand, args)
            Source_FKey.append(cursor.execute("select @@IDENTITY from SourceSequences").fetchone()[0])
        print("SourceSequences updated", i + 1)
        cnxn.commit()
    except Exception as e:
        print("SourceSequences error ", i + 1, e)
        pass
    ###################################################################


###################################################################
    ###ApplicationSetupSequence###
    Application_FKey =[]
    try:
        for i in range(len(ds.ApplicationSetupSequence)):
            strApplicationSetupNumber = ""
            strApplicationSetupType = ""
            # strReferencedSourceNumber = ""
            strTotalReferenceAirKerma = ""

            try:
                strApplicationSetupNumber = str(ds.ApplicationSetupSequence[i].ApplicationSetupNumber)
            except Exception as e:
                print("An error occurred while processing ApplicationSetupNumber:", e)
            # print("strApplicationSetupNumber",strApplicationSetupNumber)
            try:
                strApplicationSetupType = str(ds.ApplicationSetupSequence[i].ApplicationSetupType)
            except Exception as e:
                print("An error occurred while processing ApplicationSetupType:", e)

            try:
                strTotalReferenceAirKerma = str(ds.ApplicationSetupSequence[i].TotalReferenceAirKerma)
            except Exception as e:
                print("An error occurred while processing TotalReferenceAirKerma:", e)

            SQLCommand = "INSERT INTO ApplicationSetupSequences (ApplicationSetupSequence300A0230,ApplicationSetupNumber300A0234, ApplicationSetupType300A0232,  TotalReferenceAirKerma300A0250,TreatmentMachineRefId, WorkRefId,SourceSequenceRefId) " \
                         "VALUES (?,?, ?,  ?, ?, ?,?)"
            args = ("ApplicationSetupSequence "+str(i),\
            strApplicationSetupNumber,\
            strApplicationSetupType, \
            strTotalReferenceAirKerma,\
            TMachie_FKey[0],\
            WorkId_FKey, \
            Source_FKey[0])

            try:
                cursor.execute(SQLCommand, args)
                Application_FKey.append(cursor.execute("select @@IDENTITY from ApplicationSetupSequences").fetchone()[0])
                print("ApplicationSetupSequence updated", i + 1,Application_FKey)
            except Exception as e:
                print("ApplicationSetupSequence Sql update error ", i + 1, e)
        cnxn.commit()
    except Exception as e:
        print("ApplicationSetupSequence error ",i + 1,e)
        pass
    ###################################################################

    ###ChannelSequence######
    channelSeqId_FKeybfbrfb = []

    try:
        for j in range(len(ds.ApplicationSetupSequence)):


            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                # strNoOfControlPoints = ""
                strChannelSequence =""
                strChannelLength = ""
                strChannelNumber = ""
                strChannelTotalTime = ""
                strFinalCumulativeTimeWeight = ""
                strSourceApplicatorStepSize = ""
                strSourceMovementType = ""
                strTransferTubeLength = ""
                strTransferTubeNumber = ""
                strReferencedSourceNumber = ""

                try:
                    strChannelLength = str(ds.ApplicationSetupSequence[j].ChannelSequence[j].ChannelLength)
                except Exception as e:
                    print("An error occurred while processing ChannelLength:", e)
                try:
                    strNumberOfControlPoints = str(ds.ApplicationSetupSequence[j].ChannelSequence[i].NumberOfControlPoints)
                except Exception as e:
                    print("An error occurred while processing strNumberOfControlPoints:", e)
                # try:
                #     strChannelSequence = str(ds.ChannelSequence[i].ChannelSequence)
                # except Exception as e:
                #     print("An error occurred while processing strChannelSequence:", e)
                try:
                    strChannelNumber = str(ds.ApplicationSetupSequence[j].ChannelSequence[i].ChannelNumber)
                except Exception as e:
                    print("An error occurred while processing ChannelNumber:", e)

                try:
                    strChannelTotalTime = str(ds.ApplicationSetupSequence[j].ChannelSequence[i].ChannelTotalTime)
                except Exception as e:
                    print("An error occurred while processing ChannelTotalTime:", e)

                try:
                    strFinalCumulativeTimeWeight = str(ds.ApplicationSetupSequence[j].ChannelSequence[i].FinalCumulativeTimeWeight)
                except Exception as e:
                    print("An error occurred while processing FinalCumulativeTimeWeight:", e)
                try:
                    strSourceApplicatorStepSize = str(ds.ApplicationSetupSequence[j].ChannelSequence[i].SourceApplicatorStepSize)
                except Exception as e:
                    print("An error occurred while processing SourceApplicatorStepSize:", e)

                try:
                    strSourceMovementType = str(ds.ApplicationSetupSequence[j].ChannelSequence[i].SourceMovementType)
                except Exception as e:
                    print("An error occurred while processing SourceMovementType:", e)
                try:
                    strTransferTubeLength = str(ds.ApplicationSetupSequence[j].ChannelSequence[i].TransferTubeLength)
                except Exception as e:
                    print("An error occurred while processing TransferTubeLength:", e)

                try:
                    strTransferTubeNumber = str(ds.ApplicationSetupSequence[j].ChannelSequence[i].TransferTubeNumber)
                except Exception as e:
                    print("An error occurred while processing TransferTubeNumber:", e)
                #
                # try:
                #     strSourceStrengthReferenceTime = str(ds.SourceSequence[i].SourceStrengthReferenceTime)
                # except Exception as e:
                #     print("An error occurred while processing strSourceStrengthReferenceTime:", e)

                truncated_value = math.floor(float(strChannelTotalTime) * 10) / 10
                # print(truncated_value)

                if i < len(TMachie_FKey):
                    prev_machine_key = TMachie_FKey[i]
                machine_key = prev_machine_key

                if i < len(Source_FKey):
                    prev_source_key = Source_FKey[i]
                source_key = prev_source_key

                if i < len(Application_FKey):
                    prev_application_key = Application_FKey[i]
                application_key = prev_application_key

                # print("j",j)
                SQLCommand = "INSERT INTO ChannelSequences ( ChannelSequence300A0280,NoOfControlPoints300A0110,ChannelNumber300A0282,ChannelLength300A0284, ChannelTotalTime300A0286,SourceMovementType300A0288,SourceApplicatorStepSize300A02A0,TransferTubeNumber300A02A2,TransferTubeLength300A02A4,FinalCumulativeTimeWeight300A02C8, WorkRefId,TreatmentMachineRefId,SourceSequenceRefId,ApplicationSetupSequenceRefId) " \
                             "VALUES (?, ?, ?, ?, ?,?,?,?,?,?,?,?,?,?)"
                args = ("ChannelSequence"+str(i+1) , \
                        strNumberOfControlPoints,\
                        strChannelNumber , \
                        strChannelLength, \
                        truncated_value, \
                        strSourceMovementType, \
                        strSourceApplicatorStepSize, \
                        strTransferTubeNumber, \
                        strTransferTubeLength, \
                        strFinalCumulativeTimeWeight , \
                        WorkId_FKey, \
                        machine_key,\
                        source_key,\
                        application_key )
                try:
                    cursor.execute(SQLCommand, args)
                    cnxn.commit()
                except Exception as e:
                    print("Error ChannelSequence error",e)
                # cursor.execute(SQLCommand, args)
                # print("args",args)
                channelSeqId_FKeybfbrfb.append(cursor.execute("select @@IDENTITY from ChannelSequences").fetchone()[0])
            print("ChannelSequence updated", i + 1)
            cnxn.commit()
    except Exception as e:
        print("ChannelSequence error ", i + 1, e)
        pass
    ###################################################################

    FCTimeWeight = []
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                value = ds.ApplicationSetupSequence[j].ChannelSequence[i].FinalCumulativeTimeWeight
                FCTimeWeight.append(value)
    except Exception as e:
        print("TreatmentMachineSequence1 Group ", e)
    print("FCTimeWeight",FCTimeWeight)

    chanelNumber = []
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                for k in range(0, len(ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence)):
                    value = ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence[k].ChannelNumber
                    chanelNumber.append(value)
    except Exception as e:
        print("ControlPointSequence2 Group ", e)

    print("channel number",chanelNumber)

    CTotalTime = []
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                value = ds.ApplicationSetupSequence[j].ChannelSequence[i].ChannelTotalTime
                CTotalTime.append(value)
    except Exception as e:
        print("TreatmentMachineSequence4 Group ", e)

    print("CTotalTimer", CTotalTime)

    CApplicatorStepsize = []
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                value = ds.ApplicationSetupSequence[j].ChannelSequence[i].SourceApplicatorStepSize
                CApplicatorStepsize.append(value)

    except Exception as e:
        print("TreatmentMachineSequence5 Group ", e)

    print("CApplicatorStepsize number", CApplicatorStepsize)
    CLength = []
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                value = ds.ApplicationSetupSequence[j].ChannelSequence[i].ChannelLength
                CLength.append(value)
    except Exception as e:
        print("TreatmentMachineSequence6 Group ", e)
    print("CLength", CLength)

    CTimeWeight = []
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                for k in range(0, len(ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence)):
                    value = ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence[k].CumulativeTimeWeight
                    CTimeWeight.append(value)
    except Exception as e:
        print("ControlPointSequence Group ", e)
    # print("CTimeWeight", CTimeWeight)

    ControlPointRelativePosition = []
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                for k in range(0, len(ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence)):
                    value = ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence[k].ControlPointRelativePosition
                    ControlPointRelativePosition.append(value)

    except Exception as e:
        print("ControlPointSequence Group ", e)

    print("ControlPointRelativePosition",ControlPointRelativePosition)

    channel_weights = {}
    for ch_num, bcp in zip(chanelNumber, CTimeWeight):
        key = str(ch_num)
        if key not in channel_weights:
            channel_weights[key] = []
        channel_weights[key].append(bcp)
    # print("channel_weights",channel_weights)


    FCTimeWeight_values = []
    for i in range(len(chanelNumber)):
        if i == 0:
            stepsize_index = 0
        else:
            if chanelNumber[i] == chanelNumber[i - 1]:
                stepsize_index = stepsize_index
            else:
                stepsize_index = min(stepsize_index + 1, len(FCTimeWeight) - 1)
        FCTimeWeight_values.append(FCTimeWeight[stepsize_index])
    # print("FCTimeWeight_values",FCTimeWeight_values)


    CTimeWeight_values = []
    for i in range(len(chanelNumber)):
        if i == 0:
            stepsize_index = 0
        else:
            if chanelNumber[i] == chanelNumber[i - 1]:
                stepsize_index = stepsize_index
            else:
                stepsize_index = min(stepsize_index + 1, len(CTotalTime) - 1)
        CTimeWeight_values.append(CTotalTime[stepsize_index])

    channel_weights22 = {}
    for ch_num, bcp in zip(chanelNumber, CTimeWeight_values):
        key = str(ch_num)
        if key not in channel_weights22:
            channel_weights22[key] = []
        channel_weights22[key].append(bcp)
    # print("channel_weights22", channel_weights22)



    channel_weights11 = {}

    for ch_num, bcp in zip(chanelNumber, FCTimeWeight_values):
        key = str(ch_num)
        if key not in channel_weights11:
            channel_weights11[key] = []
        channel_weights11[key].append(bcp)
    # print("channel_weights11",channel_weights11)



    CTotalTime_values = []
    for i in range(len(chanelNumber)):
        if i == 0:
            stepsize_index = 0
        else:
            if chanelNumber[i] == chanelNumber[i - 1]:
                stepsize_index = stepsize_index
            else:
                stepsize_index = min(stepsize_index + 1, len(CTotalTime) - 1)
        CTotalTime_values.append(CTotalTime[stepsize_index])


    chanelNumber_value=[]
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                value = ds.ApplicationSetupSequence[j].ChannelSequence[i].ChannelNumber
                chanelNumber_value.append(value)
    except Exception as e:
        print("TreatmentMachineSequence Group ", e)

    # print("chanelNumber_value",chanelNumber_value)

    dwell_time_dict = {}

    chanelNumber_value = [str(ch_num) for ch_num in chanelNumber_value]
    print(chanelNumber_value)
    DWellTime = []
    for ch_num in chanelNumber_value:
        if ch_num in channel_weights:
            CTimeWeight_current = channel_weights[ch_num]
            FCTimeWeight_current =  channel_weights11[ch_num]
            CTotalTime_current =  channel_weights22[ch_num]
            for i in range(len(CTimeWeight_current)):
                try:
                    if CTotalTime_current[i] is None or FCTimeWeight_current[i] is None:
                        List1.append(Dwell_Time_value + "_" + "_" + Given_Value + ":" +
                                     "CTotalTime or FCTimeWeight" + "_channelnumber:" + str(ch_num) + "_CP:" + str(
                            ControlPointIndex[i]) + "_")
                        continue

                    if i > 0 and (CTimeWeight_current[i] is None or CTimeWeight_current[i - 1] is None):
                        List1.append(Dwell_Time_value + "_" + "_" + Given_Value + ":" +
                                     "Missing time weights for channel" + "_" + "channelnumber:" + str(
                            ch_num) + "_CP:" + str(ControlPointIndex[i]) + "_")
                        continue

                    if i == 0:
                        print(CTotalTime_current[i], CTimeWeight_current[i], FCTimeWeight_current[i])
                        DWellTimeValue = (CTotalTime_current[i] * CTimeWeight_current[i]) / FCTimeWeight_current[i]
                    else:
                        DWellTimeValue = (CTotalTime_current[i] *
                                          (CTimeWeight_current[i] - CTimeWeight_current[i - 1])) / FCTimeWeight_current[i]

                    # DWellTimeValue = round(DWellTimeValue, 1)
                    DWellTimeValue = int(DWellTimeValue * 1000) / 1000
                    DWellTime.append(DWellTimeValue)
                    dwell_time_dict[ch_num] = DWellTime
                except Exception as e:
                    print("DWellTime calculation error for channel", ch_num, ":", e)

            # dwell_time_dict[ch_num] = DWellTime

    # print("DWellTime Dictionary:", dwell_time_dict)
    # print("DWellTime", DWellTime)


    DWellTime_list = []

    for key in chanelNumber_value:
        if key in dwell_time_dict:
            DWellTime_list.extend(dwell_time_dict[key])

    # Print the resulting combined list
    # print("Combined List:", DWellTime_list)

    channel_Positions = {}
    channel_Positions_pre = []
    for ch_num, bcp in zip(chanelNumber, ControlPointRelativePosition):
        key = str(ch_num)
        if key not in channel_Positions:
            channel_Positions[key] = []
        channel_Positions[key].append(bcp)

    for key in sorted(channel_Positions, key=int):
        channel_Positions_pre.extend(channel_Positions[key])

    # print(channel_Positions_pre)

    channel_length_values = []
    for i in range(len(chanelNumber)):
        if i == 0:
            stepsize_index = 0
        else:
            if chanelNumber[i] == chanelNumber[i - 1]:
                stepsize_index = stepsize_index
            else:
                stepsize_index = min(stepsize_index + 1, len(CApplicatorStepsize) - 1)
        channel_length_values.append(CLength[stepsize_index])
    # print(channel_length_values)

    DWellPosition = []

    # for ch_num in chanelNumber:
    #     key = str(ch_num)
    #
    #     index = int(key) - 1
    #     if index < len(CLength):
    #         positions = channel_Positions.get(key, [])
    #         if len(positions) > 0:
    #             position_index = len(DWellPosition) % len(positions)
    #             pos = positions[position_index]
    #             DWellPositionValue = CLength[index] - pos
    #             DWellPosition.append(DWellPositionValue)

    DWellPosition = [float(ch_len) - float(ch_pos) for ch_len, ch_pos in
                     zip(channel_length_values, channel_Positions_pre)]
    # print("Updated DWellPosition:", DWellPosition)


    # print("Dwell position",DWellPosition)

    DWellPositionnumber = []
    applicator_stepsize_values = []
    for i in range(len(chanelNumber)):
        if i == 0:
            stepsize_index = 0
        else:
            if chanelNumber[i] == chanelNumber[i - 1]:
                stepsize_index = stepsize_index
            else:
                stepsize_index = min(stepsize_index + 1, len(CApplicatorStepsize) - 1)
        applicator_stepsize_values.append(CApplicatorStepsize[stepsize_index])

    # print("Updated DWellPosition:", ControlPointRelativePosition)
    # print("Dwell position", applicator_stepsize_values)
    # print("chanelNumber",chanelNumber)

    for i in range(len(ControlPointRelativePosition)):
        if i == 0:
            dwell_value = 1
            DWellPositionnumber.append(dwell_value)
            firstvalue = ControlPointRelativePosition[i]
        else:
            if chanelNumber[i] != chanelNumber[i - 1]:
                dwell_value = 1
                DWellPositionnumber.append(dwell_value)
                firstvalue = ControlPointRelativePosition[i]
            elif ControlPointRelativePosition[i] == ControlPointRelativePosition[i - 1]:
                DWellPositionnumber.append(dwell_value)
            else:
                # print("firstvalue",firstvalue)
                dwell_value = (((ControlPointRelativePosition[i] - firstvalue) /
                               applicator_stepsize_values[i]) + 1)

                dwell_value = int(dwell_value)
                DWellPositionnumber.append(dwell_value)
    # print("DWellPositionnumber",DWellPositionnumber)

    ###ControlPointSequence----------------------------------###

    channelSeqId_FKey1 = []
    last_index = 0
    for i in range(len(chanelNumber)):
        if i == 0:
            channel_id = int(channelSeqId_FKeybfbrfb[last_index])
        else:
            if chanelNumber[i] == chanelNumber[i - 1]:
                channel_id = int(channelSeqId_FKeybfbrfb[last_index])
            else:
                last_index += 1
                if last_index < len(channelSeqId_FKeybfbrfb):
                    channel_id = int(channelSeqId_FKeybfbrfb[last_index])
                else:
                    break

        channelSeqId_FKey1.append(int(channel_id))
    # print(channelSeqId_FKey1)

    dwell_time_index = 0
    dwell_position_index=0
    dwell_positionmm_index =0
    channelSeqId_FKey1_index = 0
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                for k in range(0, len(ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence)):
                    strControlPointIndex = ""
                    strControlPointRelativePosition = ""
                    strCumulativeTimeWeight = ""
                    strApplicationSetupNumber = ""
                    strChannelNumber300A0282 = ""

                    try:
                        strControlPointIndex = str(ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence[k].ControlPointIndex)
                    except Exception as e:
                        print("An error occurred while processing strControlPointIndex:", e)
                        strControlPointIndex = ""

                    try:
                        strControlPointRelativePosition = str(ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence[k].ControlPointRelativePosition)
                    except Exception as e:
                        print("An error occurred while processing strControlPointRelativePosition:", e)
                        strControlPointRelativePosition = ""

                    try:
                        strCumulativeTimeWeight = str(ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence[k].CumulativeTimeWeight)
                    except Exception as e:
                        print("An error occurred while processing strCumulativeTimeWeight:", e)
                        strCumulativeTimeWeight = ""
                    try:
                        strApplicationSetupNumber = str(ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence[k].ApplicationSetupNumber)
                    except Exception as e:
                        print("An error occurred while processing strReferenceApplicationSetupNumber:", e)
                        strApplicationSetupNumber = ""
                    try:
                        strChannelNumber300A0282 = str(ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence[k].ChannelNumber)
                    except Exception as e:
                        print("An error occurred while processing strChannelNumber300A0282:", e)
                        strChannelNumber300A0282 = ""

                    if i < len(TMachie_FKey):
                        prev_machine_key = TMachie_FKey[i]
                    machine_key = prev_machine_key

                    if i < len(Source_FKey):
                        prev_source_key = Source_FKey[i]
                    source_key = prev_source_key

                    if i < len(Application_FKey):
                        prev_application_key = Application_FKey[i]
                    application_key = prev_application_key

                    if dwell_time_index < len(DWellTime_list):
                        dwell_time = DWellTime_list[dwell_time_index]
                        dwell_time_index += 1
                    else:
                        dwell_time = None
                    # print("dwell_time",dwell_time)

                    if dwell_position_index < len(DWellPositionnumber):
                        dwell_position = DWellPositionnumber[dwell_position_index]
                        dwell_position_index +=1
                    else:
                        dwell_position = None
                    # print("dwell_position",dwell_position)

                    if dwell_positionmm_index < len(DWellPosition):
                        dwell_position_mm = DWellPosition[dwell_positionmm_index]
                        dwell_positionmm_index +=1
                    else:
                        dwell_position_mm = None
                    # print("dwell_position_mm",dwell_position_mm)

                    if channelSeqId_FKey1_index < len(channelSeqId_FKey1):
                        channelSeqId_FKey1_value = channelSeqId_FKey1[channelSeqId_FKey1_index]
                        channelSeqId_FKey1_index +=1
                    else:
                        channelSeqId_FKey1_value = None
                    # print("dwell_position_mm",dwell_position_mm)


                    SQLCommand = "INSERT INTO BrachyControlPointSequences (BrachyControlPointSequence300A02D0,ChannelNumber300A0282,ControlPointIndex300A0112,ControlPointRelativePosition300A02D2,CumulativeTimeWeight300A02D6,ReferenceApplicationSetupNumber,DwellPositionNumber,DwellTime,DwellPosition_mm,WorkRefId,ChannelSequenceRefId,TreatmentMachineRefId,SourceSequenceRefId," \
                                 "ApplicationSetupSequenceRefId)" \
                                 "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    args = ("BrachyControlPoint" + str(int(strControlPointIndex) + 1), \
                            strChannelNumber300A0282, \
                            strControlPointIndex, \
                            strControlPointRelativePosition, \
                            strCumulativeTimeWeight, \
                            strApplicationSetupNumber, \
                            dwell_position, \
                            dwell_time, \
                            dwell_position_mm, \
                            WorkId_FKey, \
                            channelSeqId_FKey1_value,\
                            machine_key,\
                            source_key,\
                            application_key)
                    # print("SQLCommand updated", SQLCommand)
                    cursor.execute(SQLCommand, args)
                cnxn.commit()
            print("ControlPointSequence updated", i+1)
    except Exception as e:
        print("ControlPointSequence error ", i + 1, e)
        pass

    ###FractionGroupSequence###

    if (0x300a, 0x00b0) in ds:
        beams = len(ds.BeamSequence)
    else:
        beams = 0

    FGList = []
    RefBeamList = []

    # print("Total Number of beams: ",beams)
    try:
        for i in range(0, len(ds.FractionGroupSequence)):
            # curbeam=1
            strFractionGroupNumber = ""
            strFractionGroupSequence = ""
            strNumberOfBeams = ""
            strNumberOfBrachyApplicationSetups = ""
            strNumberOfFractionsPlanned = ""

            try:
                strFractionGroupNumber = str(ds.FractionGroupSequence[i].FractionGroupNumber)
            except:
                strFractionGroupNumber = ""

            try:
                strNumberOfBeams = str(ds.FractionGroupSequence[i].NumberOfBeams)
            except:
                strNumberOfBeams = ""
            try:
                strNumberOfBrachyApplicationSetups = str(
                    ds.FractionGroupSequence[i].NumberOfBrachyApplicationSetups)
            except:
                strNumberOfBrachyApplicationSetups = ""

            try:
                strNumberOfFractionsPlanned = str(ds.FractionGroupSequence[i].NumberOfFractionsPlanned)
            except:
                strNumberOfFractionsPlanned = str(ds.FractionGroupSequence[i].NumberOfFractionsPlanned)

            for j in range(0, (ds.FractionGroupSequence[i].NumberOfBeams)):
                FGList.append(ds.FractionGroupSequence[i].FractionGroupNumber)
                # RefBeamList.append(curbeam)
                # curbeam=curbeam+1

            SQLCommand = "insert into FractionGroupSequences(FractionGroupNumber300A0071,FractionGroupSequence300A0070,NumberOfBeams300A0080," \
                         "NumberOfBrachyApplicationSetups300A00A0,NumberOfFractionsPlanned300A0078,WorkRefId,RTID)" \
                         "VALUES (?, ?, ?, ?, ?, ?, ?)"
            args = (strFractionGroupNumber, \
                    "FractionGroup" + str(i + 1), \
                    strNumberOfBeams, \
                    strNumberOfBrachyApplicationSetups, \
                    strNumberOfFractionsPlanned, \
                    WorkId_FKey, \
                    RTID)
            cursor.execute(SQLCommand, args)
        print("Fraction Group Sequences updated", i + 1)
        cnxn.commit()
    except:
        print("Fraction Group Sequences error", i + 1)
        pass

    ###################################################################
    ###FractionGroupSequenceReferenceBrachyApplicationSetupSequences###

    try:
        for i in range(0, len(ds.FractionGroupSequence)):
            # curbeam=1
            strBrachyApplicationSetupDose = ""
            strReferencedBrachyApplicationSetupNumber = ""

            try:
                strBrachyApplicationSetupDose = str(ds.FractionGroupSequence[i].BrachyApplicationSetupDose)
            except:
                strBrachyApplicationSetupDose = ""

            try:
                strReferencedBrachyApplicationSetupNumber = str(
                    ds.FractionGroupSequence[i].ReferencedBrachyApplicationSetupNumber)
            except:
                strReferencedBrachyApplicationSetupNumber = ""
            # try:
            #     strReferencedBrachyApplicationSetupsSequence = str(
            #         ds.FractionGroupSequence[i].ReferencedBrachyApplicationSetupSequence)
            # except:
            #     strReferencedBrachyApplicationSetupsSequence = ""

            # try:
            #     strReferencedBrachyApplicationSetupsSequenceId = str(ds.FractionGroupSequence[i].ReferencedBrachyApplicationSetupsSequenceId)
            # except Exception as e:
            #     print("An error occurred while processing:",e)
            #     strReferencedBrachyApplicationSetupsSequenceId = str(ds.FractionGroupSequence[i].ReferencedBrachyApplicationSetupsSequenceId)

            # for j in range(0, (ds.FractionGroupSequence[i].NumberOfBeams)):
            #     FGList.append(ds.FractionGroupSequence[i].FractionGroupNumber)
            #     # RefBeamList.append(curbeam)
            #     # curbeam=curbeam+1

            SQLCommand = "insert into FractionGroupSequenceReferenceBrachyApplicationSetupSequences(BrachyApplicationSetupDose300A00A4,ReferencedBrachyApplicationSetupNumber300C000C, ReferencedBrachyApplicationSetupSequence300C000A,ReferencedBrachyApplicationSetupSequenceId," \
                         "WorkRefId)" \
                         "VALUES (?, ?, ?, ?, ?)"
            args = (strBrachyApplicationSetupDose, \
                    strReferencedBrachyApplicationSetupNumber, \
                    "ApplicationSetupSequence" + str(i + 1), \
                    Application_FKey[i], \
                    WorkId_FKey)
            cursor.execute(SQLCommand, args)
        print("FractionGroupSequenceReferenceBrachyApplicationSetupSequences updated", i + 1)
        cnxn.commit()
    except:
        print("FractionGroupSequenceReferenceBrachyApplicationSetupSequences error", i + 1)
        pass
    ###################################################################


    ##DoseReferenceSequences
    try:
        for i in range(0, len(ds.DoseReferenceSequence)):

            strDeliveryMaximumDose = ""
            strDoseReferenceDescription = ""
            strDoseReferenceNumber = ""
            strDoseReferenceSequence = ""
            strDoseReferenceStructureType = ""
            strDoseReferenceType = ""
            strDoseReferenceUID = ""
            strTargetMaximumDose = ""
            strTargetPrescriptionDose = ""

            try:
                strDeliveryMaximumDose = str(ds.DoseReferenceSequence[i].DeliveryMaximumDose)
            except:
                strDeliveryMaximumDose = ""

            try:
                strDoseReferenceDescription = str(ds.DoseReferenceSequence[i].DoseReferenceDescription)
            except:
                strDoseReferenceDescription = ""

            try:
                strDoseReferenceNumber = str(ds.DoseReferenceSequence[i].DoseReferenceNumber)
            except:
                strDoseReferenceNumber = ""

            try:
                strDoseReferenceStructureType = str(ds.DoseReferenceSequence[i].DoseReferenceStructureType)
            except:
                strDoseReferenceStructureType = ""

            try:
                strDoseReferenceType = str(ds.DoseReferenceSequence[i].DoseReferenceType)
            except:
                strDoseReferenceType = ""

            try:
                strDoseReferenceUID = str(ds.DoseReferenceSequence[i].DoseReferenceUID)
            except:
                strDoseReferenceUID = ""

            try:
                strTargetMaximumDose = str(ds.DoseReferenceSequence[i].TargetMaximumDose)
            except:
                strTargetMaximumDose = ""

            try:
                strTargetPrescriptionDose = str(ds.DoseReferenceSequence[i].TargetPrescriptionDose)
            except:
                strTargetPrescriptionDose = ""

            SQLCommand = "insert into DoseReferenceSequences(DeliveryMaximumDose300A0023,DoseReferenceDescription300A0016," \
                         "DoseReferenceNumber300A0012,DoseReferenceSequence300A0010,DoseReferenceStructureType300A0014," \
                         "DoseReferenceType300A0020,DoseReferenceUid300A0013,TargetMaximumDose300A0027,TargetPrescriptionDose300A0026,WorkRefId)" \
                         "VALUES (?, ?, ?, ? , ? , ? , ? , ? , ? , ? )"
            args = (strDeliveryMaximumDose, \
                    strDoseReferenceDescription, \
                    strDoseReferenceNumber, \
                    "DoseReference" + str(i + 1), \
                    strDoseReferenceStructureType, \
                    strDoseReferenceType, \
                    strDoseReferenceUID, \
                    strTargetMaximumDose, \
                    strTargetPrescriptionDose, \
                    WorkId_FKey, \
                    )
            cursor.execute(SQLCommand, args)
        print("DoseReferenceSequences updated", i + 1)
        cnxn.commit()
    except:
        print("DoseReferenceSequences error", i + 1)
        pass

    # ###################################################################

def RTPlanTagChangeKrystal(ID0,ArgList):

    # print("Temp DB data writing")
##    print("temp arguments",ID0,RTtagTextpath,dicom_file,RTID,Site,Phase,MachineName,DeviceNo,offlinesettingDB,otherDB)

    txtfile = ArgList
    readtxtfile=open(txtfile)
    Args=readtxtfile.readlines()

##    print("Args",Args[0])
    
    loc = Args[0].strip()
    with codecs.open(loc, 'r', encoding='utf8') as file:
        lines = file.readlines()
    # print("Print File",lines)

    # print(loc)
    # wb=open(loc)
    # line=[]
    # lines=wb.readlines()
    specificCharecterSet = Args[10].strip().replace('\n','')
##    print("RTtagTextpath",lines)
    line = lines[0].split(',')
    lineins=line[1].strip().replace('\n','')

    line = lines[1].split(',')
    linever=line[1].strip().replace('\n','')

    line = lines[2].split(',')
    linebir=line[1].strip().replace('\n','')

    line = lines[3].split(',')
    lineoth=line[1].strip().replace('\n','')
    
    line = lines[4].split(',')
    linemanu1=line[1].strip().replace('\n','')

    line = lines[5].split(',')
    lineins1=line[1].strip().replace('\n','')
    
    line = lines[6].split(',')
    linemachine=line[1].strip().replace('\n','')

    line = lines[7].split(',')
    lineseri1=line[1].strip().replace('\n','')

    line = lines[8].split(',')
    linetoln=line[1].strip().replace('\n','')
    
    line = lines[9].split(',')
    lineimg=line[1].strip().replace('\n','')

    line = lines[10].split(',')
    lineimg1=line[1].strip().replace('\n','')
    
    line = lines[11].split(',')
    lineimg2=line[1].strip().replace('\n','')
    
#     line = lines[12].split(',')
#     linesetup=line[1].strip().replace('\n','')
#
#     line = lines[13].split(',')
#     linesettech=line[1].strip().replace('\n','')
#
#     line = lines[14].split(',')
#     linetole0=line[1].strip().replace('\n','')
#
#     line = lines[15].split(',')
#     linetole1=line[1].strip().replace('\n','')
#
#     line = lines[16].split(',')
#     linetole2=line[1].strip().replace('\n','')
#
#     line = lines[17].split(',')
#     linetole3=line[1].strip().replace('\n','')
#
#     line = lines[18].split(',')
#     linetole4=line[1].strip().replace('\n','')
#
#     line = lines[19].split(',')
#     linetole5=line[1].strip().replace('\n','')
#
#     line = lines[20].split(',')
#     linetole6=line[1].strip().replace('\n','')
#
#     line = lines[21].split(',')
#     linetole7=line[1].strip().replace('\n','')
#
#     line = lines[22].split(',')
#     linetole8=line[1].strip().replace('\n','')
#
#     line = lines[23].split(',')
#     linetole9=line[1].strip().replace('\n','')
#
#     line = lines[24].split(',')
#     linetole10=line[1].strip().replace('\n','')
#
# ##    print("writeeeeeeeeeeeee", linemanu1,lineins1,linemachine,lineseri1)
#
#     line = lines[25].split(',')
#
# ##    print("line",line)
#
#     linetole11a=line[1].strip().replace('\n','')
#     linetole11b=line[2].strip().replace('\n','')
#     linetole11c=line[3].strip().replace('\n','')
#     linetole11d=line[4].strip().replace('\n','')
#
# ##    print("line",line)

    line = lines[12].split(',')
    studyiid=line[1].strip().replace('\n','')

    ds = pydicom.read_file(Args[1].strip())

    try:
        patientId = 'D:/tempfile/RTPLAN/PatientId.txt'
        patinetIdFile = open(patientId, "w")
        patinetIdFile.write(ds.PatientID)
        patinetIdFile.close()
    except:
        print("Error in writing the Patient ID text file")

##    print (dicom_file)

##    ds.InstitutionName = lineins
    ds.SoftwareVersions = linever
    ds.StudyID = studyiid
    ds.add_new([0x0010,0x0032], 'TM', linebir)
    ds.add_new([0x0010,0x1000], 'LO', lineoth)

# Updating the Specific Charecter Set from Dicom2SQL Argument file
    ds.SpecificCharacterSet = str(specificCharecterSet)

##    print (linetole11a,linetole11b,linetole11c,linetole11d)

    # if (0x300a,0x0040) in ds:
    #     print("Tolerance Table Sequence present")
    # else:
    #     print("Tolerance Table Sequence not present")
    #     ds.add_new([0x300a,0x0040], 'SQ', '')
    #     ds.ToleranceTableSequence=[Dataset()]
    #     ds.ToleranceTableSequence[0].add_new([0x300a,0x0042],'IS',linetole0)
    #     ds.ToleranceTableSequence[0].add_new([0x300a,0x0043],'SH',linetole1)
    #     ds.ToleranceTableSequence[0].add_new([0x300a,0x0044],'DS',linetole2)
    #     ds.ToleranceTableSequence[0].add_new([0x300a,0x0046],'DS',linetole3)
    #     ds.ToleranceTableSequence[0].add_new([0x300a,0x004c],'DS',linetole4)
    #     ds.ToleranceTableSequence[0].add_new([0x300a,0x004f],'FL',float(linetole5))
    #     ds.ToleranceTableSequence[0].add_new([0x300a,0x0050],'FL',float(linetole6))
    #     ds.ToleranceTableSequence[0].add_new([0x300a,0x0051],'DS',linetole7)
    #     ds.ToleranceTableSequence[0].add_new([0x300a,0x0052],'DS',linetole8)
    #     ds.ToleranceTableSequence[0].add_new([0x300a,0x0053],'DS',linetole9)
    #
    #     ds.ToleranceTableSequence[0].add_new([0x300a,0x0048],'SQ', '')
    #     ds.ToleranceTableSequence[0].BeamLimitingDeviceToleranceSequence=[Dataset(),Dataset(),Dataset(),Dataset(),Dataset()]
    #     ds.ToleranceTableSequence[0].BeamLimitingDeviceToleranceSequence[0].add_new([0x300a, 0x004a], 'DS', linetole11a)
    #     ds.ToleranceTableSequence[0].BeamLimitingDeviceToleranceSequence[0].add_new([0x300a, 0x00b8], 'CS', 'X')
    #
    #     ds.ToleranceTableSequence[0].BeamLimitingDeviceToleranceSequence[1].add_new ([0x300a,0x004a],'DS',linetole11a)
    #     ds.ToleranceTableSequence[0].BeamLimitingDeviceToleranceSequence[1].add_new([0x300a,0x00b8],'CS','ASYMX')
    #
    #     ds.ToleranceTableSequence[0].BeamLimitingDeviceToleranceSequence[2].add_new([0x300a, 0x004a], 'DS', linetole11b)
    #     ds.ToleranceTableSequence[0].BeamLimitingDeviceToleranceSequence[2].add_new([0x300a, 0x00b8], 'CS', 'Y')
    #
    #     ds.ToleranceTableSequence[0].BeamLimitingDeviceToleranceSequence[3].add_new ([0x300a,0x004a],'DS',linetole11b)
    #     ds.ToleranceTableSequence[0].BeamLimitingDeviceToleranceSequence[3].add_new([0x300a,0x00b8],'CS','ASYMY')
    #
    # ##    if(ds.BeamSequence[0].PrimaryFluenceModeSequence[0].FluenceMode == 'STANDARD'):
    #     ds.ToleranceTableSequence[0].BeamLimitingDeviceToleranceSequence[4].add_new ([0x300a,0x004a],'DS',linetole11c)
    #     ds.ToleranceTableSequence[0].BeamLimitingDeviceToleranceSequence[4].add_new([0x300a,0x00b8],'CS','MLCX')
    #


    ds.save_as(Args[1].strip())
    dicomfileReading(ID0,ArgList)
    

def CTfileReading(ID1,ArgList):

    txtfile = ArgList
    readtxtfile=open(txtfile)
    Args=readtxtfile.readlines()
    CTFile = Args[0].strip()
    print("CTFile", CTFile)
    RTStructfile = Args[2].strip()
    dicom_file = Args[1].strip()
    RTID = Args[3].strip()
    Site = Args[4].strip()
    Phase = Args[5].strip()
    
    print("Treatment DB writing")
##    print("main arguments",ID1,CTFile,dicom_file,RTStructfile,RTID,Site,Phase,MachineName,DeviceNo,offlinesettingDB,CCBsettingDB)
    OfflinevalSQL = (Args[8].strip()).split(";")
    print("OfflinevalSQL",OfflinevalSQL)

    if(OfflinevalSQL[0] == "local"):
        offlineIP = "(local)"
    else:
        offlineIP = OfflinevalSQL[0]

    CCBvalSQL = (Args[9].strip()).split(";")

    if(CCBvalSQL[0] == "local"):
        CCBtreatmentIP = "(local)"
    else:
        CCBtreatmentIP = CCBvalSQL[0]

    # print("CCBvalSQL",CCBvalSQL,CCBtreatmentIP)
        
    strCTSeriesInstanceUID_0020000E = ""
    strRTSTRUCTReferenceSeriesInstanceUID = ""

    if(CTFile != "NULL"):
        ds1 = pydicom.read_file(CTFile)
        try:
            strCTSeriesInstanceUID_0020000E = str(ds1.SeriesInstanceUID)
        except:
            strCTSeriesInstanceUID_0020000E = ""

    if(RTStructfile != "NULL"):
        ds2 = pydicom.read_file(RTStructfile)
        try:
            strRTSTRUCTReferenceSeriesInstanceUID = str(ds2.SeriesInstanceUID)
        except:
            strRTSTRUCTReferenceSeriesInstanceUID = ""
            
    ds = pydicom.read_file(dicom_file)

    con_string = "Driver={SQL Server};SERVER="+CCBtreatmentIP+";DATABASE="+CCBvalSQL[1]+";uid="+CCBvalSQL[2]+";pwd="+CCBvalSQL[3]+""
##    con_string = "Driver={SQL Server};SERVER=(local);DATABASE=CCB_Treatment;uid=sa;pwd=panacea"
    cnxn = pyodbc.connect(con_string)
    cursor = cnxn.cursor()

    now = datetime.now()
    

    try:
        strAccessionNumber_00080050 = str(ds.AccessionNumber)
    except:
        strAccessionNumber_00080050 = ""

   
    try:
        strApprovalStatus_300E0002 = str(ds.ApprovalStatus)
    except:
        strApprovalStatus_300E0002 = ""

   
    try:
        strDeviceSerialNumber_00181000= str(ds.DeviceSerialNumber)
    except:
        strDeviceSerialNumber_00181000 = ""

  
    try:
        strFrameOfReferenceUID_00200052 = str(ds.FrameOfReferenceUID)
    except:
        strFrameOfReferenceUID_00200052 = ""

   
    try:
        strManufacturer_00080070 = str(ds.Manufacturer)
    except:
        strManufacturer_00080070 = ""

   
    try:
        strManufacturerModelName00081090 = str(ds.ManufacturerModelName)
    except:
        strManufacturerModelName00081090 = ""

   
    try:
        strModality_00080060 = str(ds.Modality)
    except:
        strModality_00080060 = ""

    
    try:
        strOperatorName_00081070 = str(ds.OperatorsName)
    except:
        strOperatorName_00081070 = ""

    
    try:
        strOtherPatientID_00101000 = str(ds.OtherPatientIDs)
    except:
        strOtherPatientID_00101000 = ""

 
    try:
        strPatientID_00100020 = str(ds.PatientID)
    except:
        strPatientID_00100020 = ""

    
    try:
        strPatientName_00100010 = str(ds.PatientName)
    except:
        strPatientName_00100010 = ""

  
    try:
        strPatientSex_00100040 = str(ds.PatientSex)
    except:
        strPatientSex_00100040 = ""

   
    try:
        strPlanIntent_300A000A =  str(ds.PlanIntent)
    except:
        strPlanIntent_300A000A =  ""

    
    try:
        strPositionReferenceIndicator_00201040 = str(ds.PositionReferenceIndicator)
    except:
        strPositionReferenceIndicator_00201040 = ""

   
    try:
        strReferringPhysicianName_00080090 = str(ds.ReferringPhysicianName)
    except:
        strReferringPhysicianName_00080090 = ""
    
   
    try:
        strReviewerName_300E0008 = str(ds.ReviewerName)
    except:
        strReviewerName_300E0008 = ""
   
    try:
        strRTPlanGeometry_300A000C = str(ds.RTPlanGeometry)
    except:
        strRTPlanGeometry_300A000C = ""

   
    try:
        strRTPlanLabel_300A0002 = str(ds.RTPlanLabel)
    except:
        strRTPlanLabel_300A0002 = ""

    
    try:
        strRTPlanName_300A0003 = str(ds.RTPlanName)
    except:
        strRTPlanName_300A0003 = ""

    
    try:
        strSeriesDescription_0008103E = str(ds.SeriesDescription)
    except:
        strSeriesDescription_0008103E = ""

    
    try:
        strSeriesInstanceUID_0020000E = str(ds.SeriesInstanceUID)
    except:
        strSeriesInstanceUID_0020000E = ""

   
    try:
        strSeriesNumber_00200011 = str(ds.SeriesNumber)
    except:
        strSeriesNumber_00200011 = ""


    try:
        strSoftwareVersion_00181020 = str(ds.SoftwareVersions)
    except:
        strSoftwareVersion_00181020 = ""
    
    try:
        strSOPClassUID_00080016 = str(ds.SOPClassUID)
    except:
        strSOPClassUID_00080016 = ""

  
    try:
        strSOPInstanceUID_00080018 = str(ds.SOPInstanceUID)
    except:
        strSOPInstanceUID_00080018 = ""

   
    try:
        strSpecificCharacterSet_00080005 = str(ds.SpecificCharacterSet)
    except:
        strSpecificCharacterSet_00080005 = ""
        
  
    try:
        strStationName_00081010 = str(ds.StationName)
    except:
        strStationName_00081010 = ""

   
    try:
        strAccessionNumber_00080050 = str(ds.AccessionNumber)
    except:
        strAccessionNumber_00080050 = ""

  
    try:
        strApprovalStatus_300E0002 = str(ds.ApprovalStatus)
    except:
        strApprovalStatus_300E0002 = ""

    try:
        strDeviceSerialNumber_00181000= str(ds.DeviceSerialNumber)
    except:
        strDeviceSerialNumber_00181000 = ""

    try:
        strFrameOfReferenceUID_00200052 = str(ds.FrameOfReferenceUID)
    except:
        strFrameOfReferenceUID_00200052 = ""

  
    try:
        strManufacturer_00080070 = str(ds.Manufacturer)
    except:
        strManufacturer_00080070 = ""

   
    try:
        strManufacturerModelName00081090 = str(ds.ManufacturerModelName)
    except:
        strManufacturerModelName00081090 = ""

   
    try:
        strModality_00080060 = str(ds.Modality)
    except:
        strModality_00080060 = ""

    
    try:
        strOperatorName_00081070 = str(ds.OperatorsName)
    except:
        strOperatorName_00081070 = ""

    
    try:
        strOtherPatientID_00101000 = str(ds.OtherPatientIDs)
    except:
        strOtherPatientID_00101000 = ""

    
    try:
        strPatientID_00100020 = str(ds.PatientID)
    except:
        strPatientID_00100020 = ""

   
    try:
        strPatientName_00100010 = str(ds.PatientName)
    except:
        strPatientName_00100010 = ""

  
    try:
        strPatientSex_00100040 = str(ds.PatientSex)
    except:
        strPatientSex_00100040 = ""

    
    try:
        strPlanIntent_300A000A =  str(ds.PlanIntent)
    except:
        strPlanIntent_300A000A =  ""

   
    try:
        strPositionReferenceIndicator_00201040 = str(ds.PositionReferenceIndicator)
    except:
        strPositionReferenceIndicator_00201040 = ""

   
    try:
        strReferringPhysicianName_00080090 = str(ds.ReferringPhysicianName)
    except:
        strReferringPhysicianName_00080090 = ""

    
    try:
        strReviewerName_300E0008 = str(ds.ReviewerName)
    except:
        strReviewerName_300E0008 = ""
   
    try:
        strRTPlanGeometry_300A000C = str(ds.RTPlanGeometry)
    except:
        strRTPlanGeometry_300A000C = ""

  
    try:
        strRTPlanLabel_300A0002 = str(ds.RTPlanLabel)
    except:
        strRTPlanLabel_300A0002 = ""

 
    try:
        strRTPlanName_300A0003 = str(ds.RTPlanName)
    except:
        strRTPlanName_300A0003 = ""

  
    try:
        strSeriesDescription_0008103E = str(ds.SeriesDescription)
    except:
        strSeriesDescription_0008103E = ""

    try:
        strSeriesInstanceUID_0020000E = str(ds.SeriesInstanceUID)
    except:
        strSeriesInstanceUID_0020000E = ""

    try:
        strSeriesNumber_00200011 = str(ds.SeriesNumber)
    except:
        strSeriesNumber_00200011 = ""


    try:
        strSoftwareVersion_00181020 = str(ds.SoftwareVersions)
    except:
        strSoftwareVersion_00181020 = ""
    
    try:
        strSOPClassUID_00080016 = str(ds.SOPClassUID)
    except:
        strSOPClassUID_00080016 = ""

    
    try:
        strSOPInstanceUID_00080018 = str(ds.SOPInstanceUID)
    except:
        strSOPInstanceUID_00080018 = ""

    
    try:
        strSpecificCharacterSet_00080005 = str(ds.SpecificCharacterSet)
    except:
        strSpecificCharacterSet_00080005 = ""


    try:
        strStationName_00081010 = str(ds.StationName)
    except:
        strStationName_00081010 = ""

    try:
        strStudyDescription_00081030 = str(ds.StudyDescription)
    except:
        strStudyDescription_00081030 = ""

   
    try:
        strStudyID_00200010 = str(ds.StudyID)
    except:
        strStudyID_00200010 = ""
   
    try:
        strStudyInstanceUID_0020000D = str(ds.StudyInstanceUID)
    except:
        strStudyInstanceUID_0020000D = ""


    try:

        l =len(ds.InstanceCreationTime)
        if l>6:
            iTime = datetime.strptime(ds.InstanceCreationTime,'%H%M%S.%f').time()
        else:
            iTime = datetime.strptime(ds.InstanceCreationTime,'%H%M%S').time()

        iDate = datetime.strptime(ds.InstanceCreationDate,'%Y%m%d').date()

        InstanceDateTime = datetime.combine(iDate,iTime)
    except:
        InstanceDateTime = ""
        

    try:
        
        l =len(ds.PatientBirthTime)
        if l>6:
            bTime = datetime.strptime(ds.PatientBirthTime,'%H%M%S.%f').time()
        else:
            bTime = datetime.strptime(ds.PatientBirthTime,'%H%M%S').time()

        bDate = datetime.strptime(ds.PatientBirthDate,'%Y%m%d').date()
        

        BirthDateTime = datetime.combine(bDate,bTime)
    except:
        BirthDateTime = " "


    try:
    
        l =len(ds.ReviewTime)
        if l>6:
            RTime = datetime.strptime(ds.ReviewTime,'%H%M%S.%f').time()
        else:
            RTime = datetime.strptime(ds.ReviewTime,'%H%M%S').time()
            

        RDate = datetime.strptime(ds.ReviewDate,'%Y%m%d').date()

        ReviewDateTime = datetime.combine(RDate,RTime)
    except:
        
        ReviewDateTime = ""

    try:

        l =len(ds.RTPlanTime)
        if l>6:
            RPTime = datetime.strptime(ds.RTPlanTime,'%H%M%S.%f').time()
        else:
            RPTime = datetime.strptime(ds.RTPlanTime,'%H%M%S').time()

        RPDate = datetime.strptime(ds.RTPlanDate,'%Y%m%d').date()

        RPlanDateTime = datetime.combine(RPDate,RPTime)
    except:
        RPlanDateTime = ""

    try:

        l =len(ds.StudyTime)
        if l>6:
            STime = datetime.strptime(ds.StudyTime,'%H%M%S.%f').time()
        else:
            STime = datetime.strptime(ds.StudyTime,'%H%M%S').time()

        SDate = datetime.strptime(ds.StudyDate,'%Y%m%d').date()

        StudyDateTime = datetime.combine(SDate,STime)
    except:
        
        StudyDateTime = ""

    print("PhaseNo",Phase,PhaseNo)

    SQLCommand = "insert into Works(IsWorkCompleted,AccessionNumber00080050,ApprovalStatus300E0002"\
                ",DeviceSerialNumber00181000,FrameOfReferenceUid00200052,InstanceCreationDateTime0008001200080013,"\
                "Manufacturer00080070,ManufacturerModelName00081090,Modality00080060,"\
                "OperatorName00081070,OtherPatientId00101000,PatientBirthDateTime0010003000100032,"\
                "PatientId00100020,PatientName00100010,PatientSex00100040,"\
                "PlanIntent300A000A,PositionReferenceIndicator00201040,ProfilePicture,ReferringPhysicianName00080090,"\
                "ReviewDateTime300E0004300E0005,ReviewerName300E0008,RtPlanDateTime300A0006300A0007,RtPlanGeometry300A000C,"\
                "RtPlanLabel300A0002,RtPlanName300A0003,SeriesDescription0008103E,SeriesInstanceUid0020000E,SeriesNumber00200011,"\
                "SoftwareVersion00181020,SopClassUid00080016,SopInstanceUid00080018,SpecificCharacterSet00080005,StationName00081010,"\
                "StudyDateTime0008002000080030,StudyDescription00081030,StudyId00200010,StudyInstanceUid0020000D,CTReferenceSeriesInstanceUID,Date,RTID,"\
                "SiteRefId,PhaseNo,RTSTRUCTReferenceSeriesInstanceUID,TreatmentVerificationStatus3008002C)"\
                "VALUES (?, ? , ?, ?, ?, ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ?, ? , ? , ? , ? , ? , ?, ?, ?, ? ,?, ?, ?, ?, ?, ?, ?, ?,?,?,?,?,?)"
    
    args1= ('false',\
        strAccessionNumber_00080050,\
        strApprovalStatus_300E0002,\
        strDeviceSerialNumber_00181000,\
        strFrameOfReferenceUID_00200052,
        InstanceDateTime,\
        strManufacturer_00080070,\
        strManufacturerModelName00081090,\
        strModality_00080060,
        strOperatorName_00081070,\
        strOtherPatientID_00101000,\
        BirthDateTime,\
        strPatientID_00100020,\
        strPatientName_00100010,\
        strPatientSex_00100040,\
        strPlanIntent_300A000A,\
        strPositionReferenceIndicator_00201040,\
        -1,\
        strReferringPhysicianName_00080090,\
        ReviewDateTime,\
        strReviewerName_300E0008,\
        RPlanDateTime,\
        strRTPlanGeometry_300A000C,\
        strRTPlanLabel_300A0002,\
        strRTPlanName_300A0003,\
        strSeriesDescription_0008103E,\
        strSeriesInstanceUID_0020000E,\
        strSeriesNumber_00200011,\
        strSoftwareVersion_00181020,\
        strSOPClassUID_00080016,\
        strSOPInstanceUID_00080018,\
        strSpecificCharacterSet_00080005,\
        strStationName_00081010,\
        StudyDateTime,\
        strStudyDescription_00081030,\
        strStudyID_00200010,\
        strStudyInstanceUID_0020000D,\
        strCTSeriesInstanceUID_0020000E,\
        now,\
        RTID,\
	    Site,\
        Phase,\
        strRTSTRUCTReferenceSeriesInstanceUID,\
        ' '\
        )
    
    cursor.execute(SQLCommand,args1)
    cnxn.commit()
    print("Works table data written")
    WorkId_FKey = cursor.execute("select @@IDENTITY from Works").fetchone()[0]    
    cnxn.close()
    getOfflineData(1,ArgList,WorkId_FKey)
    print("CTfileReading completed")


def   dicomfileReading(ID0,ArgList):
##    dicomfile,RTID,Site,Phase,MachineName,DeviceNo,offlinesettingDB,otherDB
    txtfile = ArgList
    readtxtfile=open(txtfile)
    Args=readtxtfile.readlines()
    
    now = datetime.now()
    ds=pydicom.read_file(Args[1].strip())

    dblist = Args[7].strip()
    OfflinevalSQL = dblist.split(";")
##    print("OfflinevalSQL",OfflinevalSQL)

    if(OfflinevalSQL[0] == "local"):
        offlineIP = "(local)"
    else:
        offlineIP = OfflinevalSQL[0]

    if(Args[8].strip() != "NULL"):
        machinevalSQL = (Args[8].strip()).split(";")
##        print("machineDB",machinevalSQL)

        if(machinevalSQL[0] == "local"):
            machineDB = "(local)"
        else:
            machineDB = machinevalSQL[0]

    if(ID0 == "0"):
        # con_string = "Driver={SQL Server};SERVER=(local);DATABASE=Temp_Treatment;uid=sa;pwd=panacea"
        con_string = "Driver={SQL Server};SERVER="+machineDB+";DATABASE="+machinevalSQL[1]+";uid="+machinevalSQL[2]+";pwd="+machinevalSQL[3]+""
        cnxn = pyodbc.connect(con_string)
        cursor = cnxn.cursor()
    elif(ID0 == "2"):
        con_string = "Driver={SQL Server};SERVER="+machineDB+";DATABASE="+machinevalSQL[1]+";uid="+machinevalSQL[2]+";pwd="+machinevalSQL[3]+""
        cnxn = pyodbc.connect(con_string)
        cursor = cnxn.cursor()
    print("Connection String:", con_string)

    try:
        strAccessionNumber_00080050 = str(ds.AccessionNumber)
    except:
        strAccessionNumber_00080050 = ""

    try:
        strApprovalStatus_300E0002 = str(ds.ApprovalStatus)
    except:
        strApprovalStatus_300E0002 = ""

   
    try:
        strDeviceSerialNumber_00181000= str(ds.DeviceSerialNumber)
    except:
        strDeviceSerialNumber_00181000 = ""

  
    try:
        strFrameOfReferenceUID_00200052 = str(ds.FrameOfReferenceUID)
    except:
        strFrameOfReferenceUID_00200052 = ""

    
   
    try:
        strManufacturer_00080070 = str(ds.Manufacturer)
    except:
        strManufacturer_00080070 = ""
        
   
    try:
        strManufacturerModelName00081090 = str(ds.ManufacturerModelName)
    except:
        strManufacturerModelName00081090 = ""

   
    try:
        strModality_00080060 = str(ds.Modality)
    except:
        strModality_00080060 = ""

    
    try:
        strOperatorName_00081070 = str(ds.OperatorsName)
    except:
        strOperatorName_00081070 = ""

    
    # try:
    #     strOtherPatientID_00101000 = str(ds.OtherPatientIDs)
    # except:
    #     strOtherPatientID_00101000 = ""

   
    try:
        strPatientID_00100020 = str(ds.PatientID)
    except:
        strPatientID_00100020 = ""



    
    try:
        strPatientName_00100010 = str(ds.PatientName)
    except:
        strPatientName_00100010 = ""

  
    try:
        strPatientSex_00100040 = str(ds.PatientSex)
    except:
        strPatientSex_00100040 = ""

   
    try:
        strPlanIntent_300A000A =  str(ds.PlanIntent)
    except:
        strPlanIntent_300A000A =  ""

    
    try:
        strPositionReferenceIndicator_00201040 = str(ds.PositionReferenceIndicator)
    except:
        strPositionReferenceIndicator_00201040 = ""

   
    try:
        strReferringPhysicianName_00080090 = str(ds.ReferringPhysicianName)
    except:
        strReferringPhysicianName_00080090 = ""

   
    try:
        strReviewerName_300E0008 = str(ds.ReviewerName)
    except:
        strReviewerName_300E0008 = ""
   
    try:
        strRTPlanGeometry_300A000C = str(ds.RTPlanGeometry)
    except:
        strRTPlanGeometry_300A000C = ""

   
    try:
        strRTPlanLabel_300A0002 = str(ds.RTPlanLabel)
    except:
        strRTPlanLabel_300A0002 = ""

    
    try:
        strRTPlanName_300A0003 = str(ds.RTPlanName)
    except:
        strRTPlanName_300A0003 = ""

    try:
        strSeriesDescription_0008103E = str(ds.SeriesDescription)
    except:
        strSeriesDescription_0008103E = ""
    try:
        strSeriesInstanceUID_0020000E = str(ds.SeriesInstanceUID)
    except:
        strSeriesInstanceUID_0020000E = ""

   
    try:
        strSeriesNumber_00200011 = str(ds.SeriesNumber)
    except:
        strSeriesNumber_00200011 = ""


    try:
        strSoftwareVersion_00181020 = str(ds.SoftwareVersions)
    except:
        strSoftwareVersion_00181020 = ""
    
    try:
        strSOPClassUID_00080016 = str(ds.SOPClassUID)
    except:
        strSOPClassUID_00080016 = ""

  
    try:
        strSOPInstanceUID_00080018 = str(ds.SOPInstanceUID)
    except:
        strSOPInstanceUID_00080018 = ""

   
    try:
        strSpecificCharacterSet_00080005 = str(ds.SpecificCharacterSet)
    except:
        strSpecificCharacterSet_00080005 = ""
        
  
    try:
        strStationName_00081010 = str(ds.StationName)
    except:
        strStationName_00081010 = ""


    try:
        strStudyDescription_00081030 = str(ds.StudyDescription)
    except:
        strStudyDescription_00081030 = ""

   
    try:
        strStudyID_00200010 = str(ds.StudyID)

    except:
        strStudyID_00200010 = ""

    #strStudyID_00200010 = "Head_1"
   
    try:
        strStudyInstanceUID_0020000D = str(ds.StudyInstanceUID)
    except:
        strStudyInstanceUID_0020000D = ""


    # try:
    #     strCTSeriesInstanceUID_0020000E = str(ds.SeriesInstanceUID)
    # except:
    #     strCTSeriesInstanceUID_0020000E = ""
    #
    # print("strCTSeriesInstanceUID_0020000E", strCTSeriesInstanceUID_0020000E)

    try:
        l =len(ds.InstanceCreationTime)
        if l>6:
            iTime = datetime.strptime(ds.InstanceCreationTime,'%H%M%S.%f').time()
        else:
            iTime = datetime.strptime(ds.InstanceCreationTime,'%H%M%S').time()

        iDate = datetime.strptime(ds.InstanceCreationDate,'%Y%m%d').date()

        InstanceDateTime = datetime.combine(iDate,iTime)
    except:
        InstanceDateTime = ""
        

    try:
        l =len(ds.PatientBirthTime)
        if l>6:
            bTime = datetime.strptime(ds.PatientBirthTime,'%H%M%S.%f').time()
        else:
            bTime = datetime.strptime(ds.PatientBirthTime,'%H%M%S').time()

        bDate = datetime.strptime(ds.PatientBirthDate,'%Y%m%d').date()

        BirthDateTime = datetime.combine(bDate,bTime)
    except:
        BirthDateTime = " "


    try:
        l =len(ds.ReviewTime)
        if l>6:
            RTime = datetime.strptime(ds.ReviewTime,'%H%M%S.%f').time()
        else:
            RTime = datetime.strptime(ds.ReviewTime,'%H%M%S').time()
            

        RDate = datetime.strptime(ds.ReviewDate,'%Y%m%d').date()

        ReviewDateTime = datetime.combine(RDate,RTime)
    except:        
        ReviewDateTime = ""

    try:
        l =len(ds.RTPlanTime)
        if l>6:
            RPTime = datetime.strptime(ds.RTPlanTime,'%H%M%S.%f').time()
        else:
            RPTime = datetime.strptime(ds.RTPlanTime,'%H%M%S').time()

        RPDate = datetime.strptime(ds.RTPlanDate,'%Y%m%d').date()

        RPlanDateTime = datetime.combine(RPDate,RPTime)
    except:
        RPlanDateTime = ""

    try:
        l =len(ds.StudyTime)
        if l>6:
            STime = datetime.strptime(ds.StudyTime,'%H%M%S.%f').time()
        else:
            STime = datetime.strptime(ds.StudyTime,'%H%M%S').time()

        SDate = datetime.strptime(ds.StudyDate,'%Y%m%d').date()

        StudyDateTime = datetime.combine(SDate,STime)
    except:
        StudyDateTime = ""

    try:
        strTreatmentSite = str(ds.TreatmentSite)
    except:
        strTreatmentSite =""

    # print("strTreatmentSite",strTreatmentSite)

    strBrachyTreatmentTechnique = str(ds.BrachyTreatmentTechnique)
    strBrachyTreatmentType  = str (ds.BrachyTreatmentType)

    SQLCommand = "insert into Works(IsWorkCompleted,AccessionNumber00080050,ApprovalStatus300E0002"\
                      ",DeviceSerialNumber00181000,FrameOfReferenceUid00200052,InstanceCreationDateTime0008001200080013,"\
                      "Manufacturer00080070,ManufacturerModelName00081090,Modality00080060,"\
                      "OperatorName00081070,PatientBirthDateTime0010003000100032,"\
                      "PatientId00100020,PatientName00100010,PatientSex00100040,"\
                      "PlanIntent300A000A,PositionReferenceIndicator00201040,ProfilePicture,ReferringPhysicianName00080090,"\
                      "ReviewDateTime300E0004300E0005,ReviewerName300E0008,RtPlanDateTime300A0006300A0007,RtPlanGeometry300A000C,"\
                      "RtPlanLabel300A0002,RtPlanName300A0003,SeriesDescription0008103E,SeriesInstanceUid0020000E,SeriesNumber00200011,"\
                      "SoftwareVersion00181020,SopClassUid00080016,SopInstanceUid00080018,SpecificCharacterSet00080005,StationName00081010,"\
                      "StudyDateTime0008002000080030,StudyDescription00081030,StudyId00200010,StudyInstanceUid0020000D,CTReferenceSeriesInstanceUID,Date,RTID,TreatmentSite30100077,PhaseNo,"\
                      "NoOfSlices,RTSTRUCTReferenceSeriesInstanceUID,TreatmentVerificationStatus3008002C,BrachyTreatmentTechnique,BrachyTreatmentType)"\
                      "VALUES (?, ?, ?, ?, ?, ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ? , ?, ? , ?  , ? , ? , ?, ?, ?, ? ,?, ?, ?, ?, ?, ?, ?,?,?,?,?,?,?,?,?,?)"
    args1= ('false',\
        strAccessionNumber_00080050,\
        strApprovalStatus_300E0002,\
        strDeviceSerialNumber_00181000,\
        strFrameOfReferenceUID_00200052,
        InstanceDateTime,\
        strManufacturer_00080070,\
        strManufacturerModelName00081090,\
        strModality_00080060,
        strOperatorName_00081070,\
        # strOtherPatientID_00101000,\
        BirthDateTime,\
        strPatientID_00100020,\
        strPatientName_00100010,\
        strPatientSex_00100040,\
        strPlanIntent_300A000A,\
        strPositionReferenceIndicator_00201040,\
        -1,\
        strReferringPhysicianName_00080090,\
        ReviewDateTime,\
        strReviewerName_300E0008,\
        RPlanDateTime,\
        strRTPlanGeometry_300A000C,\
        strRTPlanLabel_300A0002,\
        strRTPlanName_300A0003,\
        strSeriesDescription_0008103E,\
        strSeriesInstanceUID_0020000E,\
        strSeriesNumber_00200011,\
        strSoftwareVersion_00181020,\
        strSOPClassUID_00080016,\
        strSOPInstanceUID_00080018,\
        strSpecificCharacterSet_00080005,\
        strStationName_00081010,\
        StudyDateTime,\
        strStudyDescription_00081030,\
        strStudyID_00200010,\
        strStudyInstanceUID_0020000D,\
        ' ',\
        now,\
	    Args[2].strip(), \
        Args[3].strip(),\
        Args[4].strip(), \
        ' ',\
        '',\
        "Apporved",\
        strBrachyTreatmentTechnique,\
        strBrachyTreatmentType\
        )
    # print("SQL Command:", SQLCommand)
    # print("Parameters:", args1)



    print("Works Table update")

    cursor.execute(SQLCommand, args1)
    cnxn.commit()
    WorkId_FKey = cursor.execute("select @@IDENTITY from Works").fetchone()[0]
    print("WorkId_FKey", WorkId_FKey)
    cnxn.close()
    
    if(ID0 == "0"):
        getOfflineData(0,ArgList,WorkId_FKey)
    elif(ID0 == "2"):
        getOfflineData(2,ArgList,WorkId_FKey)

if __name__ == "__main__":
   if len(sys.argv)>1:
      if sys.argv[1]=="0":
          RTPlanTagChangeKrystal(sys.argv[1],sys.argv[2])
      elif sys.argv[1]=="1":        
          CTfileReading(sys.argv[1],sys.argv[2])
      elif sys.argv[1]=="2":         
          RTPlanTagChangeKrystal(sys.argv[1],sys.argv[2])

# ArgumentList = "D:\\tempfile_hdr\\DicomToSQLArgumentsFile.txt"
# RTPlanTagChangeKrystal("0",ArgumentList)
# RTPlanTagChangeKrystal("2",ArgumentList)
# CTfileReading("1",ArgumentList)
############Carriage Calculation is been changed sicce 1.0.24##############
#######################################################################################################################################
##RTPlanTagChangeKrystal("0",RTtagTextpath,dicom_file,RTID,"1","1",TreatmentMachine,DeviceNo,offlinesettingDB,"NULL") - arguments: Id, txtpath, dicompath, Rtid, site, phase, machine, deviceno, offline setting DB path, NULL
##RTPlanTagChangeKrystal("2",RTtagTextpath,dicom_file,RTID,"1","1",TreatmentMachine,DeviceNo,offlinesettingDB,MachineqaDB) - arguments: Id, CTpath, dicompath, RTstructpath, Rtid, site, phase, machine, deviceno, offline setting DB path, CCB treatment DB path
##CTfileReading("1",CTfile,dicom_file,RTStruct,RTID,"1","1",TreatmentMachine,DeviceNo,offlinesettingDB,CCBsettingDB) - arguments: Id, txtpath, dicompath, Rtid, site, phase, machine, deviceno, offline setting DB path, MachineQA DB path
