#Uncommented  List15[] in Tolerance table latral was wrong...
from datetime import datetime

import sys, warnings
if not sys.warnoptions:
   warnings.simplefilter("ignore")
   try:
       import pydicom as dicom
   except ImportError:
       import dicom
import dicom
from dicom.dataset import Dataset, FileDataset
from datetime import datetime
import os
import sys
import json
import xlrd
import pyodbc
import csv
from openpyxl import Workbook
import numpy
import subprocess
from dicom.dataset import Dataset, FileDataset,  DataElement
from dicom.tag import Tag
import pydicom
from pydicom.uid import generate_uid

filenameList=[]
textpath1 = ""
dicompath = ""
ListDicom=[]
ListPatientID=[]
List1=[]
Tps2Machine1=[]
carriageA1=[]
carriageB1=[]
ListStudyInstanceUIDfromCT=[]
ListPatientIDfromCT=[]
StudyInstanceUIDfromCT=""
PatientIDfromCT=""

def generatedicom(ArgList):
    
    txtfile = ArgList
    readtxtfile=open(txtfile)
    Args=readtxtfile.readlines()
    excelpath = Args[0].strip()
    treatmentmachinename = Args[1].strip()
    Deviceno = Args[2].strip()
    savepath = Args[3].strip()
    OfflinevalSQL = (Args[4].strip()).split(";")

    if (OfflinevalSQL[0] == "local"):
        offlineIP = "(local)"
    else:
        offlineIP = OfflinevalSQL[0]

    print("Excel2Dcm Input parameters : ",excelpath,treatmentmachinename,Deviceno,savepath)
###############################Reading the machine config file###############################################
    # ConfigFile = "D:/Krystal/MachineConfig.config"
    # Machinefile = open(ConfigFile,"r")
    # Data = Machinefile.readlines()
    # MachineData = []
    # for i in range(0,len(Data)):
    #     Values =  Data[i].split(";")
    #     MachineData.append(Values)
##    print("MachineData",MachineData)
    # b = []
    # for k in range(0,len(MachineData[0])):
    #     a = MachineData[0][k].split("_")
    #     b.append(a)
    #     if (b[k][0] == treatmentmachinename and b[k][1] == Deviceno):
    #         if(b[k][4] == "False" or b[k][4] == "FALSE" or b[k][4] == "false"):
    #             LeafApplicable = 0
    #         else:
    #             LeafApplicable = 1

            # if(b[k][9] == " " or b[k][9] == ""):
            #     WedgeApplicable = 0
            # elif(b[k][9] == "NA"):
            #     WedgeApplicable = 1
            # else:
            #     WedgeApplicable = 1
            #
            # if(b[k][10] == " " or b[k][10] == ""):
            #     Fluencemode = 0
            # else:
            #     Fluencemode = 1

    ############################## Reading the database ###################################
    con_string = "Driver={SQL Server};SERVER="+offlineIP+";DATABASE="+OfflinevalSQL[1]+";uid="+OfflinevalSQL[2]+";pwd="+OfflinevalSQL[3]+""
    cnxn = pyodbc.connect(con_string)

    cursor = cnxn.cursor()
    LimitValues_Section = "SELECT * FROM MachineSettings WHERE ManufacturerModelName ='" + treatmentmachinename + "' and DeviceSerialNumber='" + Deviceno + "'"
    cursor.execute(LimitValues_Section)
    machineSettingsSection = cursor.fetchone()

    cursor2 = cnxn.cursor()
    LimitValues_Section2 = "SELECT * FROM MachineSettingsSection2 WHERE ManufacturerModelName ='" + treatmentmachinename + "' and DeviceSerialNumber='" + Deviceno + "'"
    cursor2.execute(LimitValues_Section2)
    machineSettingsSection2 = cursor2.fetchone()

    if (len(machineSettingsSection2) == 0 or len(machineSettingsSection2) == 0):
        print("DB offlinesetting --- failed")
        return
    else:
        print("")
    LeafApplicable = 0
    WedgeApplicable = 0
    Fluencemode = 0
    ##checking for MLC applicability
    print("machineSettingsSection[20]", machineSettingsSection[20], type(machineSettingsSection[20]))
    if (machineSettingsSection[1] == treatmentmachinename and machineSettingsSection[2] == Deviceno):
        if (machineSettingsSection[20] == False):
            LeafApplicable = 0
        else:
            LeafApplicable = 1

    ##checking for Wedge applicability
    if ((machineSettingsSection2[28] == " ") or (machineSettingsSection2[28] == "") or (machineSettingsSection2[28] == "NULL")):
        WedgeApplicable = 0
    elif (machineSettingsSection2[28] == "NA"):
        WedgeApplicable = 1
    else:
        WedgeApplicable = 1

    ##checking for Fluencemode
    if ((machineSettingsSection2[82] == " ") or (machineSettingsSection2[82] == "") or (machineSettingsSection2[82] == None)):
    # if ((machineSettingsSection2[82] == "NA") or (machineSettingsSection2[82] == "")):
        Fluencemode = 0
    else:
        Fluencemode = 1

    ########################################################################################
    # print("MachineData",treatmentmachinename,LeafApplicable,WedgeApplicable,Fluencemode)

    Dicom_FileNAME = excelpath
##    print("Dicom_FileNAME",Dicom_FileNAME)

    wb = xlrd.open_workbook(excelpath)
    sheet = wb.sheet_by_index(0)
    total_records = sheet.nrows
    suffix = '.dcm'

    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.481.5'
    file_meta.MediaStorageSOPInstanceUID = dicom.UID.generate_uid()
    # file_meta.MediaStorageSOPInstanceUID = Args[5].strip()

    file_meta.ImplementationClassUID = "1.2.3.4"

    print("sopclassuid",file_meta.MediaStorageSOPClassUID)
    print("sopinstanceuid",file_meta.MediaStorageSOPInstanceUID)

    savedcm = savepath + "\\"+file_meta.MediaStorageSOPInstanceUID+'.dcm'

# Create the FileDataset instance (initially no data elements, but file_meta supplied)
    ds = FileDataset(savedcm, {}, file_meta=file_meta, preamble=b"\0" * 128)              

# Set creation date/time
    dt = datetime.now()
    ds.InstanceCreationDate = dt.strftime('%Y%m%d')
    timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
    ds.InstanceCreationTime = timeStr

     ## Works Excel Sheet
    ds.AccessionNumber= str(sheet.cell_value(0,2))
    ds.ApprovalStatus = sheet.cell_value(1,2)
    ds.DeviceSerialNumber = sheet.cell_value(4,2)
    frameuid = generate_uid()
    ds.FrameOfReferenceUID = str(frameuid)
    ID0 = str(sheet.cell_value(6,2))
    ID1 = str(ID0[0:8])
    IT0 = str(sheet.cell_value(7,2))
    IT1 = str(IT0[0:6])
    ds.InstanceCreationDate = ID1
    ds.InstanceCreationTime = IT1
    ds.Manufacturer= sheet.cell_value(8,2)
    ds.ManufacturerModelName= sheet.cell_value(9,2)
    ds.Modality= sheet.cell_value(10,2)
    ds.OperatorsName= sheet.cell_value(11,2)
    # ds.OtherPatientID= sheet.cell_value(10,2)
    DOB0 = str(sheet.cell_value(12,2))
    DOB1 = str(DOB0[0:8])
    ds.PatientBirthDate= DOB1
    ds.PatientID = sheet.cell_value(13,2)
    ds.PatientName = sheet.cell_value(14,2)
    ds.PatientSex= sheet.cell_value(15,2)
    ds.PlanIntent= sheet.cell_value(16,2)
    ds.PositionReferenceIndicator= sheet.cell_value(17,2)
    ds.ReferringPhysicianName= sheet.cell_value(18,2)
    RD0 = str(sheet.cell_value(19,2))
    RD1 = str(RD0[0:8])
    RT0 = str(sheet.cell_value(20,2))
    RT1 = str(RT0[0:6])
    ds.ReviewDate= RD1
    ds.ReviewTime= RT1
    ds.ReviewerName= sheet.cell_value(21,2)
    RTD0 = str(sheet.cell_value(22,2))
    RTD1 = str(RTD0[0:8])
    RTT0 = str(sheet.cell_value(23,2))
    RTT1 = str(RTT0[0:6])
    ds.RTPlanDate= RTD1
    ds.RTPlanTime= RTT1
    ds.RTPlanGeometry= sheet.cell_value(24,2)
    ds.RTPlanLabel= sheet.cell_value(25,2)
    ds.RTPlanName= sheet.cell_value(26,2)
    ds.SeriesDescription= sheet.cell_value(27,2)
##    ds.SeriesInstanceUID= sheet.cell_value(27,2)
    seriesuid = generate_uid()
    ds.SeriesInstanceUID= str(seriesuid)
    try:
        ds.SeriesNumber= str(sheet.cell_value(29,2))
    except Exception as e:
        print("Exception", e)
    # print("sheet.cell SeriesNumber", sheet.cell_value(29, 2))
    ds.SoftwareVersions= sheet.cell_value(30,2)
    # print("SoftwareVersions", ds.SoftwareVersions)
    ds.SOPClassUID= '1.2.840.10008.5.1.4.1.1.481.5'
##    print('SOPInstanceUID',sheet.cell_value(31,2))
##    ds.SOPInstanceUID= sheet.cell_value(31,2)

    sopuid = file_meta.MediaStorageSOPInstanceUID
    ds.SOPInstanceUID= str(sopuid)
    ds.SpecificCharacterSet= sheet.cell_value(33,2)


    ds.StationName= sheet.cell_value(34,2)
    SD0 = str(sheet.cell_value(35,2))
    SD1 = str(SD0[0:8])
    ST0 = str(sheet.cell_value(36,2))
    ST1 = str(ST0[0:6])
    ds.StudyDate=SD1
    ds.StudyTime=ST1
    ds.StudyDescription= sheet.cell_value(37,2)
    ds.StudyID= str(sheet.cell_value(38,2))
    ds.StudyInstanceUID= sheet.cell_value(39,2)
    # ds.TreatmentSite = sheet.cell_value(40,2)
    ds.BrachyTreatmentTechnique = sheet.cell_value(2,2)
    ds.BrachyTreatmentType = sheet.cell_value(3,2)
    ds.FrameOfReferenceUID = sheet.cell_value(5,2)

    # ds.add_new((0x3010, 0x0077), 'LO',  sheet.cell_value(40, 2))
    ds.add_new((0x0020, 0x0011), 'IS', sheet.cell_value(29, 2))



    # print("sheet.cell values 2", sheet.cell_value(2, 2))
    # print("sheet.cell values 3 ", sheet.cell_value(3, 2))
    # print("sheet.cell values 5", sheet.cell_value(5, 2))
    # print("sheet.cell values 40", sheet.cell_value(40, 2))
##    studyuid = generate_uid()
##    ds.StudyInstanceUID= str(studyuid)

    ## Works Excel Sheet
    
    ######################################
    sheet1 = wb.sheet_by_index(1)
    total_records1 = sheet1.nrows



    ## Dose Reference new
    # print("Total no.of Beams", sheet1.nrows-2);

    list1=[];list2=[];list3=[];list4=[];list5=[];list6=[];
    list7=[];list8=[];list9=[];list10=[];list11=[];list12=[];
    list13=[];list14=[];list15=[];list16=[];list17=[];list18=[];
    list19=[];list20=[];list21=[];list22=[];list23=[];list24=[];
    list25=[];
    h1=2

    NLeaf=""
    for i1 in range(2,int(total_records1)) :
        list1.append(sheet1.cell_value(i1, 0))
        list2.append(sheet1.cell_value(i1, 1))
        list3.append(sheet1.cell_value(i1, 2))
        list4.append(sheet1.cell_value(i1, 3))
        list5.append(sheet1.cell_value(i1, 4))
        list6.append(sheet1.cell_value(i1, 5))
        list7.append(sheet1.cell_value(i1, 6))
        list8.append(sheet1.cell_value(i1, 7))
        # print("sheet1.cell_valuei1, 7",sheet1.cell_value(i1, 7))

        ndrs = 1
        drs = []
        for k in range(0, total_records1 - 2):
            dr = Dataset()
            dr.DoseReferenceNumber = list1[k];
            dr.DoseReferenceUID = list2[k];
            dr.DoseReferenceStructureType = list3[k];
            dr.DoseReferenceDescription = list4[k];
            dr.DoseReferenceType = list5[k];
            dr.DeliveryMaximumDose = list6[k];
            dr.TargetPrescriptionDose = list7[k];
            dr.TargetMaximumDose = list8[k];
            drs.append(dr)
        ds.DoseReferenceSequence = drs

    ## Fraction Group sequence
    sheet2 = wb.sheet_by_index(2)
    total_records2 = sheet2.nrows
    for i1 in range(2, int(total_records2)):
        list9.append(sheet2.cell_value(i1, 0))
        list10.append(sheet2.cell_value(i1, 1))
        list11.append(sheet2.cell_value(i1, 2))
        list12.append(sheet2.cell_value(i1, 3))
        list13.append(sheet2.cell_value(i1, 4))
        list14.append(sheet2.cell_value(i1, 5))
        list15.append(sheet2.cell_value(i1, 6))

        # print("sheet2.cell_valuei1, 6", sheet2.cell_value(i1, 3))
    nfgs = 1
    fgs = []
    for k in range(0, total_records2 - 2):
        fg = Dataset()
        fg.FractionGroupNumber = list9[k];
        fg.NumberOfFractionsPlanned = list10[k];
        fg.NumberOfBeams = list11[k];
        fg.NumberOfBrachyApplicationSetups = list12[k];
        fg.ReferencedBrachyApplication = list13[k];
        fg.BrachyApplicationSetupDose = list14[k];
        fg.ReferencedBrachyApplicationSetupNumber = list15[k];
        fgs.append(fg)
    ds.FractionGroupSequence = fgs

    ## TreatmentMachineName sequnce
    sheet3 = wb.sheet_by_index(3)
    total_records3 = sheet3.nrows
    for i1 in range(2, int(total_records3)):

        list16.append(sheet3.cell_value(i1, 0))
        list17.append(sheet3.cell_value(i1, 1))
        list18.append(sheet3.cell_value(i1, 2))
        list19.append(sheet3.cell_value(i1, 3))
        list20.append(sheet3.cell_value(i1, 4))
        # print("sheet3.cell_valuei1, 4", sheet3.cell_value(i1, 4))

    ntms = 1
    tms = []
    for k in range(0, total_records3 - 2):
        tm = Dataset()
        # tm.TreatmentMachineName = list
        tm.Manufacturer = list16[k];
        tm.InstitutionName = list17[k];
        tm.ManufacturerModelName = list18[k];
        tm.DeviceSerialNumber = list19[k];
        tm.TreatmentMachineName = list20[k];
        tms.append(tm)
    ds.TreatmentMachineSequence = tms

    # ## ApplicationSetup sequnce
    # sheet4 = wb.sheet_by_index(4)
    # total_records4 = sheet4.nrows
    # for i1 in range(2, int(total_records4)):
    #     list21.append(sheet4.cell_value(i1, 0))
    #     list22.append(sheet4.cell_value(i1, 1))
    #     list23.append(sheet4.cell_value(i1, 2))
    #     list24.append(sheet4.cell_value(i1, 3))
    #     # print("sheet4.cell_valuei1, 3", sheet4.cell_value(i1, 0))
    #     # print("sheet4.cell_valuei1, 3", sheet4.cell_value(i1, 3))
    #
    # nass =1
    # assG = []
    # for k in range(0,int(total_records4-2)):
    #     ass = Dataset()
    #     ass.ApplicationSetupType = list21[k];
    #     ass.ApplicationSetupNumber = list22[k];
    #     ass.TotalReferenceAirKerma = list23[k];
    #     ass.ReferencedSourceNumber = list24[k];
    #     assG.append(ass)
    # ds.ApplicationSetupSequence = assG

    list26=[];list27=[];list28=[];list29=[];list30=[];list31=[];list32=[];list33=[];list34=[];list35=[];list36=[];list37=[];list38=[];list39=[];list40=[];
    list41=[];list42=[];list43=[];list44=[];list45=[];list46=[];list47=[];list48=[];list49=[];list50=[];list51=[];list52=[];list53=[];


    ## Source sequnce
    sheet5 = wb.sheet_by_index(5)
    total_records5 = sheet5.nrows
    for i1 in range(2,int(total_records5)) :
        list25.append(sheet5.cell_value(i1, 0))
        list26.append(sheet5.cell_value(i1, 1))
        list27.append(sheet5.cell_value(i1, 2))
        list28.append(sheet5.cell_value(i1, 3))
        list29.append(sheet5.cell_value(i1, 4))
        list33.append(sheet5.cell_value(i1, 5))
        list34.append(sheet5.cell_value(i1, 6))
        list35.append(sheet5.cell_value(i1, 7))
        list36.append(sheet5.cell_value(i1, 8))
        # print("sheet5.cell_valuei1, 3", sheet5.cell_value(i1, 0))
        # print("sheet5.cell_valuei1, 3", sheet5.cell_value(i1, 8))

    nss = 1
    ssg = []
    for k in range(0, int(total_records5 - 2)):
        ss = Dataset()
        ss.SourceSerialNumber = list25[k];
        ss.SourceNumber = list26[k];
        ss.SourceType = list27[k];
        ss.SourceIsotopeName = list28[k];
        ss.SourceIsotopeHalfLife = list29[k];
        ss.SourceStrengthUnits = list33[k];
        ss.ReferenceAirKermaRate = list34[k];
        # try:
        #     ss.SourceStrengthReferenceDate = list35[k];
        # except Exception as e:
        #     print("Exception", e)

        try:
            value_to_assign = list35[k]
            if isinstance(value_to_assign, (float, int)):
                ss.SourceStrengthReferenceDate = str(value_to_assign)
            elif isinstance(value_to_assign, str):
                ss.SourceStrengthReferenceDate = value_to_assign
            else:
                raise ValueError("Invalid type for SourceStrengthReferenceDate: {type(value_to_assign)}")

            value_to_assign = list36[k]
            if isinstance(value_to_assign, (float, int)):
                ss.SourceStrengthReferenceTime = str(value_to_assign)
            elif isinstance(value_to_assign, str):
                ss.SourceStrengthReferenceTime = value_to_assign
            else:
                raise ValueError("Invalid type for SourceStrengthReferenceTime: {type(value_to_assign)}")

        except IndexError:
            print("Index {k} is out of bounds for one of the lists.")
        except Exception as e:
            print("An error occurred: {e}")

        # ss.SourceStrengthReferenceDate = list35[k];
        # ss.SourceStrengthReferenceTime = list36[k];
        ssg.append(ss)
    ds.SourceSequence = ssg

    # ## channel sequnce
    # sheet6 = wb.sheet_by_index(6)
    # total_records6 = sheet6.nrows
    # for i1 in range(2, total_records6):
    #     list37.append(sheet6.cell_value(i1, 0))
    #     list38.append(sheet6.cell_value(i1, 1))
    #     list39.append(sheet6.cell_value(i1, 2))
    #     list40.append(sheet6.cell_value(i1, 3))
    #     list41.append(sheet6.cell_value(i1, 4))
    #     list42.append(sheet6.cell_value(i1, 5))
    #     list43.append(sheet6.cell_value(i1, 6))
    #     list44.append(sheet6.cell_value(i1, 7))
    #     list45.append(sheet6.cell_value(i1, 8))
    #
    # ncss = 1
    # cssg = []
    # for k in range(0, int(total_records6 - 2)):
    #     css = Dataset()
    #     css.NumberOfControlPoints = list37[k];
    #     css.ChannelNumber = list38[k];
    #     css.ChannelLength = list39[k];
    #     css.ChannelTotalTime = list40[k];
    #     css.SourceMovementType = list41[k];
    #     css.SourceApplicatorStepSize = list42[k];
    #     css.TransferTubeNumber = list43[k];
    #     css.TransferTubeLength = list44[k];
    #     css.FinalCumulativeTimeWeight = list45[k];
    #     cssg.append(css)
    # ds.ChannelSequence = cssg
    #
    # ## control point sequnce
    # sheet7 = wb.sheet_by_index(7)
    # total_records7 = sheet7.nrows
    # for i1 in range(1, total_records7):
    #     list46.append(sheet7.cell_value(i1, 0))
    #     list47.append(sheet7.cell_value(i1, 1))
    #     list48.append(sheet7.cell_value(i1, 2))
    #     list49.append(sheet7.cell_value(i1, 3))
    #     list50.append(sheet7.cell_value(i1, 4))
    #     list51.append(sheet7.cell_value(i1, 5))
    #     list52.append(sheet7.cell_value(i1, 6))
    # # print("Total records:00", total_records7)
    # # print("Lengths of lists:00", len(list46), len(list47), len(list48), len(list49), len(list50), len(list51),
    # #       len(list52))
    # ncps =1
    # cpsg = []
    # total_records7 = min(len(list46), len(list47), len(list48), len(list49), len(list50), len(list51), len(list52))
    #
    # for k in range(total_records7):
    #     cps = Dataset()
    #     cps.ChannelNumber = list46[k]
    #     cps.ControlPointIndex = list47[k]
    #     cps.ControlPointRelativePosition = list48[k]
    #     cps.CumulativeTimeWeight = list49[k]
    #     cps.SourceNumber = list50[k]
    #     cps.ReferencedDoseReferenceNumber = list51[k]
    #     cps.ApplicationSetupNumber = list52[k]
    #     cpsg.append(cps)
    # ds.ControlPointSequence = cpsg

    sheet4 = wb.sheet_by_index(4)
    total_records4 = sheet4.nrows

    # application_setups = []
    #
    # for i1 in range(2, int(total_records4)):
    #     application_setup = Dataset()
    #     application_setup.ApplicationSetupType = sheet4.cell_value(i1, 0)
    #     application_setup.ApplicationSetupNumber = sheet4.cell_value(i1, 1)
    #     application_setup.TotalReferenceAirKerma = sheet4.cell_value(i1, 2)
    #     application_setup.ReferencedSourceNumber = sheet4.cell_value(i1, 3)
    #
    #     # ChannelSequence inside ApplicationSetupSequence
    #     sheet6 = wb.sheet_by_index(6)
    #     total_records6 = sheet6.nrows
    #
    #     channels = []
    #     for j in range(2, int(total_records6)):
    #         channel = Dataset()
    #         channel.ChannelNumber = sheet6.cell_value(j, 1)  # Assuming column 1 is ChannelNumber
    #         channel.NumberOfControlPoints = sheet6.cell_value(j, 0)
    #         channel.ChannelLength = sheet6.cell_value(j, 2)
    #         channel.ChannelTotalTime = sheet6.cell_value(j, 3)
    #         channel.SourceMovementType = sheet6.cell_value(j, 4)
    #         channel.SourceApplicatorStepSize = sheet6.cell_value(j, 5)
    #         channel.TransferTubeNumber = sheet6.cell_value(j, 6)
    #         channel.TransferTubeLength = sheet6.cell_value(j, 7)
    #         channel.FinalCumulativeTimeWeight = sheet6.cell_value(j, 8)
    #
    #         # ControlPointSequence inside ChannelSequence
    #         sheet7 = wb.sheet_by_index(7)
    #         total_records7 = sheet7.nrows
    #
    #         control_points = []
    #         for k in range(1, total_records7):
    #             # Match ChannelNumber between ChannelSequence and ControlPointSequence
    #             if sheet7.cell_value(k, 0) == channel.ChannelNumber:  # Assuming column 0 in sheet7 is ChannelNumber
    #                 control_point = Dataset()
    #                 control_point.ChannelNumber = sheet7.cell_value(k, 0)
    #                 control_point.ControlPointIndex = sheet7.cell_value(k, 1)
    #                 control_point.ControlPointRelativePosition = sheet7.cell_value(k, 2)
    #                 control_point.CumulativeTimeWeight = sheet7.cell_value(k, 3)
    #                 control_point.SourceNumber = sheet7.cell_value(k, 4)
    #                 control_point.ReferencedDoseReferenceNumber = sheet7.cell_value(k, 5)
    #                 control_point.ApplicationSetupNumber = sheet7.cell_value(k, 6)
    #                 control_points.append(control_point)
    #
    #         channel.ControlPointSequence = control_points
    #         channels.append(channel)
    #
    #     application_setup.ChannelSequence = channels
    #     application_setups.append(application_setup)
    #
    # ds.ApplicationSetupSequence = application_setups

    application_setups = []

    for i1 in range(2, int(total_records4)):
        application_setup = Dataset()
        application_setup.ApplicationSetupType = sheet4.cell_value(i1, 0)
        application_setup.ApplicationSetupNumber = sheet4.cell_value(i1, 1)
        application_setup.TotalReferenceAirKerma = sheet4.cell_value(i1, 2)
        application_setup.ReferencedSourceNumber = sheet4.cell_value(i1, 3)

        sheet6 = wb.sheet_by_index(6)
        total_records6 = sheet6.nrows

        channels = []
        for j in range(2, int(total_records6)):
            channel = Dataset()
            channel.ChannelNumber = sheet6.cell_value(j, 1)
            channel.NumberOfControlPoints = sheet6.cell_value(j, 0)
            channel.ChannelLength = sheet6.cell_value(j, 2)
            channel.ChannelTotalTime = sheet6.cell_value(j, 3)
            channel.SourceMovementType = sheet6.cell_value(j, 4)
            channel.SourceApplicatorStepSize = sheet6.cell_value(j, 5)
            channel.TransferTubeNumber = sheet6.cell_value(j, 6)
            channel.TransferTubeLength = sheet6.cell_value(j, 7)
            channel.FinalCumulativeTimeWeight = sheet6.cell_value(j, 8)

            sheet7 = wb.sheet_by_index(7)
            total_records7 = sheet7.nrows

            control_points = []
            for k in range(1, total_records7):
                if (
                        sheet7.cell_value(k,
                                          0) == channel.ChannelNumber and
                        sheet7.cell_value(k, 6) == application_setup.ApplicationSetupNumber
                ):
                    control_point = Dataset()
                    control_point.ChannelNumber = sheet7.cell_value(k, 0)
                    control_point.ControlPointIndex = sheet7.cell_value(k, 1)
                    control_point.ControlPointRelativePosition = sheet7.cell_value(k, 2)
                    control_point.CumulativeTimeWeight = sheet7.cell_value(k, 3)
                    control_point.SourceNumber = sheet7.cell_value(k, 4)
                    control_point.ReferencedDoseReferenceNumber = sheet7.cell_value(k, 5)
                    control_point.ApplicationSetupNumber = sheet7.cell_value(k, 6)
                    control_points.append(control_point)

            channel.ControlPointSequence = control_points
            channels.append(channel)

        application_setup.ChannelSequence = channels
        application_setups.append(application_setup)

    ds.ApplicationSetupSequence = application_setups


    # print("Total records:", total_records7)
    # print("Lengths of lists:", len(list46), len(list47), len(list48), len(list49), len(list50), len(list51),
    #       len(list52))

# Set the transfer syntax
    ds.is_little_endian = True
    ds.is_implicit_VR = True

    print("Writing dcm file", savedcm)
    ds.save_as(savedcm)
    cnxn.close()
    print("DCM generated")

    # dcm = savedcm
    # dc = pydicom.read_file(dcm)
    # print(dc.BeamSequence[0].BeamName)
if __name__ == "__main__":
   if len(sys.argv)>1: 
        generatedicom(sys.argv[1])
        
ArgumentList = "D:\\tempfile\\CreatePlanFromExcelArgumentDataFile.txt"
generatedicom(ArgumentList)
