#Krystal 4.0.0 onwords, Dicom Validation 2.0.12
#Dose Rate validation is been included from MachineSettingsSection1 table, Data1 and Data2 (min and max) column for 30FF filter and Data3 and Data4 column for 16FF filter
#Field Size (Only Jaws) validation is been included from MachineSettingsSection2 table, Data1 and Data2 (X1 min and X1max), Data3 and Data4 (X2 min and X2max) column,
#Data5 and Data6 (Y1 min and Y1max), Data7 and Data8 (Y2 min and Y2max) column for 16FF
#Krystal 4.0.0 onwords, Dicom Validation 2.0.13
#MLC Carriage details radded in the Language translator DB

import pydicom
from datetime import datetime
import os
import os.path
import sys
import numpy
import numpy as np
import csv
import pyodbc
import logging
import time
import codecs

from hashlib import md5
from base64 import b64decode
from base64 import b64encode



def validate_dicom(ArgList):

    ##dicompath,Treatmentmachine,Deviceno,patientID
    print("Inside the Funct", ArgList)

    txtfile = ArgList
    readtxtfile = open(txtfile)
    Args = readtxtfile.readlines()

    dicompath = Args[0].strip()
    print("dicompath", dicompath)
    ds = pydicom.read_file(dicompath)

    ##    print("oooooo",ds.PatientID)
    ##    RTID = ds.PatientID
    RTID = Args[3].strip()
    Treatmentmachine = Args[1].strip()
    Deviceno = Args[2].strip()

    print("RTID",RTID)
    print("Treatmentmachine & Deviceno",Treatmentmachine,Deviceno)
    List1 = []
    List2 = []

    Time = 'Time'
    Given_Value = 'Given Value'
    Required_Value = 'Required Value'
    to = 'to'
    Beam = 'Beam'
    Control_Point = 'Control Point'
    Approve_Status = 'Approve Status'
    Patient_Sex = 'Patient Sex'
    M = 'M'
    F = 'F'
    O = 'O'
    Manufacturer_1 ='Manufacturer'
    Patient_Modality = 'Modality'
    Manufacturer_Mode_Name = 'Manufacturer Mode Name'
    Patirnt_PlanIntent = 'Plan Intent'
    Patient_BrachyTreatment_Technique = 'Brachy Treatment Technique'
    Patient_BrachyTreatment_type ='Brachy Treatment Type'
    Treatment_Machine_Name ='Treatment Machine Name'
    NumberOf_BrachyApplication_Setups = 'Number Of BrachyApplication Setups'
    Dose_Delivery_max = 'Delivery of Maximum Dose'
    Dose_Delivery_min = 'Delivery of Manimum Dose'
    Channel_sqeuence = 'Min and Max channel number'
    channel_number_range = "Channel number "
    Dwell_Time_value ='Dwell Time'
    Dwell_Time_value_11 = 'At least one dwell time must be greater than zero'
    Dwell_Position_MM = 'Dwell position(mm)'
    APPlicator_Step_size ='APPlicator Step Size'
    Dwell_Position_number = 'Dwell position number'
    Treatment_Machine_Sequence = 'Treatment Machine Sequence'
    FC_Time_Weight = 'Final Cumulative Time Weight'

    couch = 0

    languageTranslationSQL = (Args[5].strip()).split(";")
    if (languageTranslationSQL[0] == "local" or languageTranslationSQL[0] == "Local"):
        IP = "(local)"
    else:
        IP = languageTranslationSQL[0]

    conn_string = "Driver={SQL Server};SERVER=" + IP + ";DATABASE=" + languageTranslationSQL[1] + ";uid=" + \
                  languageTranslationSQL[2] + ";pwd=" + languageTranslationSQL[3]
    cnxx = pyodbc.connect(conn_string)
    cursor1 = cnxx.cursor()

############################################Reading Language translation Database######################################
#language selection
    cursor1.execute("SELECT isDefault FROM DefaultLanguage ")
    col = cursor1.fetchone()
    defaultLanguage = col[0]
    print("defaultLanguage...", defaultLanguage)

#fetching primary languade data
    primaryLanguage = []
    secondaryLanguage = []
    fetchePriConx = cursor1.execute("SELECT PrimaryLanguage FROM Languages")
    fetchPriData = fetchePriConx.fetchall()
    a = 0
    print("Primary Language...")
    while a < 1:
        for col in fetchPriData:
            primaryLanguage.append(col[a])
        a = a + 1
    # print("Primary Language: ", primaryLanguage)
        # fetching secondary languade data
        fetcheSecConx = cursor1.execute("SELECT SecondaryLanguage FROM Languages")
        fetchSecData = fetcheSecConx.fetchall()
        if (defaultLanguage == False):
            b = 0
            while b < 1:
                for col in fetchSecData:
                    secondaryLanguage.append(col[b])
                b = b + 1
            print("Secondary Language...")
            # print("Secondary Language:", secondaryLanguage)

    # fetching secondary languade data
    fetcheSecConx = cursor1.execute("SELECT SecondaryLanguage FROM Languages")
    fetchSecData = fetcheSecConx.fetchall()
    if (defaultLanguage == False):
        b=0
        while b < 1:
            for col in fetchSecData:
                secondaryLanguage.append(col[b])
            b = b + 1
        print("Secondary Language...")
        # print("Secondary Language:", secondaryLanguage)


    ############################################Reading Offline Settings Database######################################

    LimitValues_Section00 = "SELECT * FROM MachineSettings WHERE ManufacturerModelName ='" + Treatmentmachine + "' and DeviceSerialNumber='" + Deviceno + "'"
    cursor.execute(LimitValues_Section00)
    row00 = cursor.fetchone()
    # print("LimitValues_Section00 ",row00)

    LimitValues_Section01 = "SELECT * FROM MachineSettingsSection1 WHERE ManufacturerModelName ='"+Treatmentmachine+"' and DeviceSerialNumber='"+Deviceno+"'"
    cursor.execute(LimitValues_Section01)
    row01 = cursor.fetchone()
    # print("LimitValues_Section01",row01)

    LimitValues_Section02 = "SELECT * FROM MachineSettingsSection2 WHERE ManufacturerModelName ='"+Treatmentmachine+"' and DeviceSerialNumber='"+Deviceno+"'"
    cursor.execute(LimitValues_Section02)
    row02 = cursor.fetchone()
    # print("LimitValues_Section02", row02)

    cursor.close()
    cnxn.close()




    print("VALIDATE parameters")

    # ##--------------------------------------04-10-2024----------------------------------

    try:
        Modality = str(ds.Modality)
        if Modality == row02[3]:
            # print("Modality", Modality)
            pass
        else:
            List1.append(Patient_Modality + "_00080060:" + "_" + Given_Value + ":" + str(Modality) + "_" + Required_Value + ":" +str(row02[3]) + "_ _ ")
    except Exception as e:
        print("Caught Exception in Modality:", e)
        Modality = " "


    try:
        PlanIntent = str(ds.PlanIntent)
        intents = row02[4].split(", ")
        if PlanIntent in intents:
            # print("plan intent ", PlanIntent)
            pass
        else:
            List1.append(Patirnt_PlanIntent + "_300A000A:" + "_" + Given_Value + ":" + str(PlanIntent) + "_" + Required_Value + ":" + str(row02[4])  + "_ _ ")


    except Exception as e:
        print("Caught Exception in PlanIntent:", e)


    try:
        BrachyTreatmentTechnique = str(ds.BrachyTreatmentTechnique)

        TreatmentTechnique = row00[30].split(", ")
        if BrachyTreatmentTechnique in TreatmentTechnique:
            pass
        else:
            List1.append(Patient_BrachyTreatment_Technique + "_300A0200:" + "_" + Given_Value + ":" + str(BrachyTreatmentTechnique) + "_" + Required_Value + ":" + str(row00[30]) + "_ _ ")

    except Exception as e:
        print("Caught Exception in BrachyTreatmentTechnique :", e)

    try:
        BrachyTreatmentType = str(ds.BrachyTreatmentType)
        if BrachyTreatmentType == row00[31]:
            # print("Brachy Treatment Type ", BrachyTreatmentType)

            pass
        else:
            List1.append(Patient_BrachyTreatment_type + "_300A0202:" + "_" + Given_Value + ":" + str(BrachyTreatmentType) + "_" + Required_Value + ":" + str(row00[31]) + "_ _ ")

    except Exception as e:
        print("Caught Exception in BrachyTreatmentType:", e)
        BrachyTreatmentType = " "


    try:
        for i in range(0, len(ds.TreatmentMachineSequence)):
            TreatmentMachineName = ds.TreatmentMachineSequence[i].TreatmentMachineName
            required_value = row02[12]
            if TreatmentMachineName != required_value:
                List1.append(Treatment_Machine_Name + "_300A00B2:" + "_" + Given_Value + ":" + str(
                    TreatmentMachineName) + "_" + Required_Value + ":" + str(row02[12]) + "_ _ ")
            else:
                # print("TreatmentMachineName ", TreatmentMachineName)
                pass
    except Exception as e:
        print("TreatmentMachineSequence Group ", e)

    try:
        Manufacturer = str(ds.Manufacturer)
        if Manufacturer == row02[13]:
            # print("Manufacturer ", Manufacturer)

            pass
        else:
            List1.append(Manufacturer_1+"_00080070:"+ "_" + Given_Value + ":" + str(
                    Manufacturer) + "_" + Required_Value + ":" + str(row02[13]) + "_ _ ")
    except Exception as e:
        print("Caught Exception in Manufacturer:", e)
        Manufacture1 = " "

    try:
        ManufacturerModelName = str(ds.ManufacturerModelName)
        if ManufacturerModelName == row02[14]:
            # print("ManufacturerModelName ", ManufacturerModelName)
            pass
        else:
            List1.append(Manufacturer_Mode_Name + "_00081090:" + "_" + Given_Value + ":" + str(
                ManufacturerModelName) + "_" + Required_Value + ":" + str(row02[14]) + "_ _ ")
    except Exception as e:
        print("Caught Exception in ManufacturerModelName:", e)
        ManufacturerModelName = " "

    try:
        for i in range(0, len(ds.FractionGroupSequence)):
            NumberOfBrachyApplicationSetups = ds.FractionGroupSequence[i].NumberOfBrachyApplicationSetups
            print("NumberOfBrachyApplicationSetups ", NumberOfBrachyApplicationSetups)
            required_value = int(row02[23])
            if NumberOfBrachyApplicationSetups <= required_value:
                pass
            else:
                List1.append(NumberOf_BrachyApplication_Setups + "_300A000A:" + "_" + Given_Value + ":" + str(
                    NumberOfBrachyApplicationSetups) + "_" + Required_Value + ":" + str(row02[23]) + "_ _ ")
    except Exception as e:
        print("Fraction Group Sequence error", e)


    FCTimeWeight = []
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                value = ds.ApplicationSetupSequence[j].ChannelSequence[i].FinalCumulativeTimeWeight
                FCTimeWeight.append(value)
    except Exception as e:
        print("TreatmentMachineSequence Group ", e)

    print("FCTimeWeight",FCTimeWeight,row02[30])



    try:
        ApproveStatus = str(ds.ApprovalStatus)

        if ApproveStatus == row02[79]:
            # print(" ApproveStatus:", ApproveStatus)
            pass
        else:
            List1.append(Approve_Status + "_300E0002:" + "_" + Given_Value + ":" + str(
                ApproveStatus) + "_" + Required_Value + ":" + str(row02[79]) + "_ _ ")
    except Exception as e:
        print("Caught Exception in ApproveStatus:", e)
        ApproveStatus = " "

    # print("DeliveryMaximumDose",float(row02[32]),float(row02[33]))

    DeliveryMaximumDose300A0023=[]
    try:
        for i in range(0, len(ds.DoseReferenceSequence)):
            DeliveryMaximumDose300A0023  = ds.DoseReferenceSequence[i].DeliveryMaximumDose
    except Exception as e:
        print("Dose Reference Sequence1", e)

    TargetPrescriptionDose300A0026=[]
    try:
        for i in range(0, len(ds.DoseReferenceSequence)):
            TargetPrescriptionDose300A0026 = ds.DoseReferenceSequence[i].TargetPrescriptionDose
    except Exception as e:
        print("Dose Reference Sequence2", e)



    try:
        if DeliveryMaximumDose300A0023 <= float(row02[33]):
            # print(" DeliveryMaximumDose300A0023:", DeliveryMaximumDose300A0023)
            pass
        else:
            List1.append(Dose_Delivery_max + "_300A0023" + "_" + Given_Value + ":" + str(
                DeliveryMaximumDose300A0023) + "_" + Required_Value + ":" + str(row02[32]) + " " + to + " " + str(row02[33]) + "_ _ ")

        if TargetPrescriptionDose300A0026 >= float(row02[32]):
            pass
        else:
            List1.append(Dose_Delivery_min + "_300A0026" + "_" + Given_Value + ":" + str(
                TargetPrescriptionDose300A0026) + "_" + Required_Value + ":" + str(row02[32]) + " " + to + " " + str(row02[33]) + "_ _ ")
    except Exception as e:
        print("Dose Reference Sequence3", e)


    CLength = []
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                value = ds.ApplicationSetupSequence[j].ChannelSequence[i].ChannelLength
                CLength.append(value)
    except Exception as e:
        print("TreatmentMachineSequence Group ", e)
    print("CLength", CLength)

    NumberOfControlPoints_length = []

    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                value = ds.ApplicationSetupSequence[j].ChannelSequence[i].NumberOfControlPoints
                NumberOfControlPoints_length.append(value)
    except Exception as e:
        print("TreatmentMachineSequence Group ", e)
    print("NumberOfControlPoints_length", NumberOfControlPoints_length)

    Numberchannel = []

    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                value = ds.ApplicationSetupSequence[j].ChannelSequence[i].ChannelNumber
                Numberchannel.append(value)
    except Exception as e:
        print("TreatmentMachineSequence Group ", e)
    print("Numberchannel", Numberchannel)


    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                controlpoints  = int(NumberOfControlPoints_length[i])
                # print("controlpoints",controlpoints)
                if controlpoints >= row02[80] and controlpoints <=row02[81]:
                    pass
                else:
                    List1.append(Control_Point + "_300A0110" + "_" + Given_Value + ":" + str(
                        controlpoints) + "_" + Required_Value + ":" + str(row02[80]) + " " + to + " " + str(
                        row02[81]) +  "_channelnumber:" +  str(Numberchannel[i]) +"_CP:" + str(NumberOfControlPoints_length[i]))
    except Exception as e:
        print("ControlPoints range  ", e)


    chanelNumber = []
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                for k in range(0, len(ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence)):
                    value = ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence[k].ChannelNumber
                    chanelNumber.append(value)
    except Exception as e:
        print("ControlPointSequence Group ", e)
    print("chanelNumber ControlPointSequence ",chanelNumber)

    CTotalTime = []
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                value = ds.ApplicationSetupSequence[j].ChannelSequence[i].ChannelTotalTime
                CTotalTime.append(value)
    except Exception as e:
        print("TreatmentMachineSequence Group ", e)

    # print("CTotalTime112", CTotalTime)

    CApplicatorStepsize = []
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                value = ds.ApplicationSetupSequence[j].ChannelSequence[i].SourceApplicatorStepSize
                CApplicatorStepsize.append(value)

    except Exception as e:
        print("TreatmentMachineSequence Group ", e)
    # print("CApplicatorStepsize", CApplicatorStepsize)

    CLength = []
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                value = ds.ApplicationSetupSequence[j].ChannelSequence[i].ChannelLength
                CLength.append(value)

    except Exception as e:
        print("TreatmentMachineSequence Group ", e)
    # print("CLength", CLength)


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
    ControlPointIndex = []
    try:
        for j in range(len(ds.ApplicationSetupSequence)):

            for i in range(len(ds.ApplicationSetupSequence[j].ChannelSequence)):
                for k in range(0, len(ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence)):
                    value = ds.ApplicationSetupSequence[j].ChannelSequence[i].ControlPointSequence[k].ControlPointIndex
                    ControlPointIndex.append(value)

    except Exception as e:
        print("ControlPointSequence Group ", e)

    # print("ControlPointIndex",ControlPointIndex)
    channel_weights = {}

    for ch_num, bcp in zip(chanelNumber, CTimeWeight):
        key = str(ch_num)
        if key not in channel_weights:
            channel_weights[key] = []
        channel_weights[key].append(bcp)

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
    print("chanelNumber_value",chanelNumber_value)

    value_min = int(row02[98])
    value_max = int(row02[99])
    value_max = (value_max + 1)

    valid_range = range(value_min, value_max)
    print("valid_range",valid_range)

    for value in chanelNumber_value:
        try:
            int_value = int(value)

            if int_value in valid_range:
                pass
            else:
                List1.append(channel_number_range + "_300A0282" + "_" + Given_Value + ":" + str(
                    value) + "_" + Required_Value + ":" + str(row02[98]) + " " + to + " " + str(
                    row02[99]) + "_ _ ")

        except ValueError:
            List1.append(channel_number_range + "_300A0282" + "_" + Given_Value + ":" + str(
                value) + "_" + Required_Value + ":" + str(row02[98]) + " " + to + " " + str(
                row02[99]) + "_ _ ")

    dwell_time_dict = {}

    chanelNumber_value = [str(ch_num) for ch_num in chanelNumber_value]

    for ch_num in chanelNumber_value:
        if ch_num in channel_weights:
            CTimeWeight_current = channel_weights[ch_num]
            FCTimeWeight_current = channel_weights11[ch_num]
            CTotalTime_current = channel_weights22[ch_num]
            DWellTime = []

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
                        DWellTimeValue = (CTotalTime_current[i] * CTimeWeight_current[i]) / FCTimeWeight_current[i]
                    else:
                        DWellTimeValue = (CTotalTime_current[i] *
                                          (CTimeWeight_current[i] - CTimeWeight_current[i - 1])) / FCTimeWeight_current[
                                             i]

                    DWellTimeValue = round(DWellTimeValue, 1)
                    DWellTime.append(DWellTimeValue)
                except Exception as e:
                    print("DWellTime calculation error for channel", ch_num, ":", e)

            dwell_time_dict[ch_num] = DWellTime

    print("DWellTime Dictionary:", dwell_time_dict)
    print("DWellTime",DWellTime)

    CumalativeTimeWeight_current = []
    for ch_num, bcp in zip(chanelNumber, channel_weights):
        key = str(ch_num)
        if key not in channel_weights:
            channel_weights[key] = []
        channel_weights[key].append(bcp)

    for key in sorted(channel_weights, key=int):
        CumalativeTimeWeight_current.extend(channel_weights[key])

    print("channel_weights",channel_weights)
    for key in channel_weights:
        if key in dwell_time_dict:
            channel_values = list(map(float, channel_weights[key]))
            dwell_time_values = dwell_time_dict[key]

            for i in range(1, min(len(channel_values), len(dwell_time_values))):
                if channel_values[i] == channel_values[i - 1]:
                    if dwell_time_values[i] == 0.0:
                        pass
                    else:
                        print("entered")
                        List1.append(Dwell_Time_value + "_" + "_" + Given_Value + ":" + str(dwell_time_values[i]) + "_" +Required_Value + ":" +"_chanelNumber:" + str(key) + "_CP:" + str(ControlPointIndex[i]))
                elif channel_values[i] != channel_values[i - 1]:
                    if dwell_time_values[i] == 0.0:
                        List1.append(Dwell_Time_value + "_" + "_" + Given_Value + ":" + str(
                            dwell_time_values[i]) + "_" +Required_Value + ":" +"_chanelNumber:" + str(key) + "_CP:" + str(ControlPointIndex[i]) )

    dwellmin = float(row02[96])
    dwellmax = float(row02[97])
    # print("row02[98]", row02[96], row02[97],dwellmin,dwellmax)
    dwellmin = dwellmin/1000
    dwellmax = dwellmax/1000

    channel_Positions = {}
    channel_Positions_pre = []
    for ch_num, bcp in zip(chanelNumber, ControlPointRelativePosition):
        key = str(ch_num)
        if key not in channel_Positions:
            channel_Positions[key] = []
        channel_Positions[key].append(bcp)

    for key in sorted(channel_Positions, key=int):
        channel_Positions_pre.extend(channel_Positions[key])
    print(channel_Positions_pre)


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

    DWellPosition = [float(ch_len) - float(ch_pos) for ch_len, ch_pos in
                     zip(channel_length_values, channel_Positions_pre)]
    print("Dwell position", len(DWellPosition))


    print("dwellmin & dwellmax", dwellmin, dwellmax)
    for key in channel_weights:
        if key in dwell_time_dict:
            channel_values = list(map(float, channel_weights[key]))
            dwell_time_values = dwell_time_dict[key]

            for i in range(1, min(len(channel_values), len(dwell_time_values))):
                current_dwell_time = dwell_time_values[i]
                current_position = DWellPosition[i]
                previous_position = DWellPosition[i - 1]
                if current_dwell_time == 0.0:
                   if current_position != previous_position:
                       continue

                   else:
                       List1.append( Dwell_Time_value_11 + "__" + Given_Value + ":" + str(current_dwell_time) + "_" +
                           Required_Value + ":" + str(dwellmin) + " " + to + " " + str(dwellmax) +
                           "_chanelNumber:" + str(key) +
                           "_CP:" + str(ControlPointIndex[i])
                       )

            for i in range(1, min(len(channel_values), len(dwell_time_values))):
                if dwell_time_values[i] == 0.0:
                    if channel_values[i] == channel_values[i - 1]:
                        continue
                    else:
                        List1.append(Dwell_Time_value + "_" + "_" + Given_Value + ":" + str(
                            dwell_time_values[i]) + "_" +Required_Value + ":" + str(dwellmin) + " " + to + " " + str(dwellmax)+ "_chanelNumber:" + str(key) + "_CP:" + str(ControlPointIndex[i]))
                else:
                    if not (dwellmin <= float(dwell_time_values[i]) <= dwellmax) :
                        List1.append(Dwell_Time_value + "_" + "_" + Given_Value + ":" + str(
                            dwell_time_values[i])+"_" +Required_Value + ":" + str(dwellmin) + " " + to + " " + str(dwellmax)+ "_chanelNumber:" + str(key) + "_CP:" + str(ControlPointIndex[i]) )

    for j in range(len(ds.ApplicationSetupSequence)):
        ch_number = len(ds.ApplicationSetupSequence[j].ChannelSequence)

    try:

        if ch_number >= row02[98] and ch_number <= row02[99] :
            # print("channel number range ")
            pass
        else:
            List1.append(Channel_sqeuence + "_300A0282" + "_" + Given_Value + ":" + str(
                ch_number) + "_" + Required_Value + ":" + str(row02[98]) + " " + to + " " + str(
                row02[99]) + "_ _ ")
            # print("min and max channel number not in the range ")
    except Exception as e:
        pass



    # channel_Positions = {}
    # channel_Positions_pre = []
    # for ch_num, bcp in zip(chanelNumber, ControlPointRelativePosition):
    #     key = str(ch_num)
    #     if key not in channel_Positions:
    #         channel_Positions[key] = []
    #     channel_Positions[key].append(bcp)
    #
    # for key in sorted(channel_Positions, key=int):
    #     channel_Positions_pre.extend(channel_Positions[key])

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



    DWellPosition = [float(ch_len) - float(ch_pos) for ch_len, ch_pos in
                     zip(channel_length_values, channel_Positions_pre)]
    print("Dwell position", len(DWellPosition))

    try:
        required_value1 = float(row02[100])
        required_value2 = float(row02[101])
        # print(required_value2,required_value1)
        for i in range(len(DWellPosition)):
            if required_value1 <= DWellPosition[i] <= required_value2:
                # print("mtched DWellPosition")
                pass
            else:
                List1.append(Dwell_Position_MM + "_" + "_" + Given_Value + ":" + str(
                    DWellPosition[i]) + "_" + Required_Value + ":" + str(row02[100]) + " " + to + " " + str(
                    row02[101]) +  "_chanelNumber:" + str(chanelNumber[i]) + "_CP:" + str(ControlPointIndex[i]) )
    except Exception as e:
        print("DWell Position Number range error:", e)


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
    # print("ControlPointRelativePosition",ControlPointRelativePosition)

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
    print("DWellPositionnumber",DWellPositionnumber)

    print("CApplicatorStepsize",CApplicatorStepsize)


    for i in range(len(CApplicatorStepsize)):
        try:
            if CApplicatorStepsize[i] is None:
                List1.append(APPlicator_Step_size + "_300A02A0" + "_" + Given_Value + ":" +
                             str(CApplicatorStepsize[i]) + "_" + Required_Value + ":" +
                             str(row02[102]) + " " + to + " " + str(row02[103]) + "_ _ ")
                continue

            if row02[102] is None or row02[103] is None:
                List1.append(APPlicator_Step_size + "_300A02A0" + "_" + Given_Value + ":" +
                             str(CApplicatorStepsize[i]) + "_" + Required_Value + ":" +
                             str(row02[102]) + " " + to + " " + str(row02[103]) + "_ _ ")
                continue

            if float(row02[102]) <= CApplicatorStepsize[i] <= float(row02[103]):
                pass
            else:
                List1.append(APPlicator_Step_size + "_300A02A0" + "_" + Given_Value + ":" +
                             str(CApplicatorStepsize[i]) + "_" + Required_Value + ":" +
                             str(row02[102]) + " " + to + " " + str(row02[103]) + "_ _ ")

        except Exception as e:
            print("CApplicator Stepsize range error at index", i, e)
    print("row02[106]",row02[106],row02[107])
    # print("DWellPositionnumber before",DWellPositionnumber)

    try:
        for i in range(len(chanelNumber)):
            channel = chanelNumber[i]
            dwell_position = DWellPositionnumber[i]

            # Ensure each dwell_position is iterable
            if not isinstance(dwell_position, (list, tuple)):
                dwell_position = [dwell_position]

            for value in dwell_position:
                try:
                    # print( "Ensure row02[106] and row02[107] are converted to float")
                    min_range = float(str(row02[106]))
                    max_range = float(str(row02[107]))

                    if min_range <= value <= max_range:
                        pass
                    else:

                        List1.append(Dwell_Position_number + "_" + "_" + Given_Value + ":" + str(value) + "_" +
                            Required_Value + ":" + str(min_range) + " " + to + " " + str(max_range) +
                            " _channelnumber:" + str(channel) + " _CP:" + str(ControlPointIndex[i]) )
                except Exception as inner_e:
                    print("Error processing value ",value,i,inner_e)
    except Exception as e:
        print("DWell Position Number range error:", e)

    try:
        if row00[31] != len(ds.TreatmentMachineSequence):
            # print("mtched Dwell number")
            pass
        else:
            List1.append(Treatment_Machine_Sequence + "_300A0206" + "_" + Given_Value + ":" + str(
                value) + "_" + Required_Value + ":" + str(row00[31]) + "_ _ ")
    except Exception as e:
        print("DWell Position Number range error:", e)


    List1=(list(set(List1)))
    List1 = list(filter(lambda x: x != "", List1))
    # print("Errors",List1)
    return(List1,RTID)



if __name__ == "__main__":
    if len(sys.argv)>1:

        readtxtfile = open(sys.argv[1])
        Args = readtxtfile.readlines()
        OfflinevalSQL = (Args[4].strip()).split(";")
        if (OfflinevalSQL[0] == "local" or OfflinevalSQL[0] == "Local"):
            IP = "(local)"
        else:
            IP = OfflinevalSQL[0]

        con_string = "Driver={SQL Server};SERVER="+IP+";DATABASE="+OfflinevalSQL[1]+";uid="+OfflinevalSQL[2]+";pwd="+OfflinevalSQL[3]
        cnxn = pyodbc.connect(con_string)
        cursor = cnxn.cursor()


        [list1,RTID] = validate_dicom(sys.argv[1])
        file = 'D:\\tempfile\\RTPLAN\\PLAN_MISMATCH_TAGS.txt'
        file1 = file.split("\n")
        file1 = file.split("\n")
        if (len(file1) > 1):
            file = file1[0] + file1[1]
        with codecs.open(file, 'w', encoding='utf-8') as f:
            # f = open(file, "w")
            for k in range(0, len(list1)):
                f.write(list1[k])
                f.write("\n")
            f.close()
        print("Validation completed")
        time.sleep(1)
        # os.system("taskkill /f /im DICOM2SQL_HDR.exe")

############ "Uncomment to run in the IDE and Comment to create exe" ##############################################################
ArgumentList = "D:\\tempfile_hdr\\DicomValidationArgumentsFile.txt"
readtxtfile=open(ArgumentList)
Args = readtxtfile.readlines()
OfflinevalSQL = (Args[4].strip()).split(";")
if(OfflinevalSQL[0] == "local" or OfflinevalSQL[0] == "Local"):
   IP = "(local)"
else:
   IP = OfflinevalSQL[0]
con_string = "Driver={SQL Server};SERVER="+IP+";DATABASE="+OfflinevalSQL[1]+";uid="+OfflinevalSQL[2]+";pwd="+OfflinevalSQL[3]
cnxn = pyodbc.connect(con_string)
cursor = cnxn.cursor()

list1=[]
[list2,RTID]=validate_dicom(ArgumentList)
# file = 'D:\\tempfile\\RTPLAN\\'+str(RTID)+'_PLAN_MISMATCH_TAGS.txt'
file = 'D:\\tempfile\\RTPLAN\\PLAN_MISMATCH_TAGS.txt'
# print("File",file.split("\n"))
file1=file.split("\n")
if(len(file1)>1):
   file=file1[0]+file1[1]
with codecs.open(file, 'w', encoding='utf-8') as f:
# f = open(file, "w")
   for k in range (0,len(list2)):
       f.write (list2[k])
       f.write ("\n")
   f.close()
print("Validation completed")


