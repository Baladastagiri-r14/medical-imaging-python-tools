# -*- coding: utf-8 -*-
import sys
import pydicom
from datetime import datetime
import pyodbc
import logging
from pydicom.dataset import Dataset


def RTPlanTagChangeKrystal(ID, ArgList):
    print("VMAT Dose Rate Calculation started.")
    txtfile = ArgList
    readtxtfile = open(txtfile)
    Args = readtxtfile.readlines()
    dicom_file = Args[1].strip()  ##1
    ds = pydicom.read_file(dicom_file)  # arg in this case is path of the dicom file to be read

    ############Fraction Group Sequence#########

    for i in range(0,len(ds.FractionGroupSequence)):
        beamMetersetWeightList = []
        for j in range(0, len(ds.FractionGroupSequence[i].ReferencedBeamSequence)):
            beamMetersetWeightList.append(ds.FractionGroupSequence[i].ReferencedBeamSequence[j].BeamMeterset)

    ############Beam Sequence#########
    try:
        strPlanIntent = str(ds.PlanIntent)
    except:
        strPlanIntent = ""

    ############Beam Sequence Control Points Sequence#########
    try:
        planDescription = str(ds.RTPlanDescription)
        planDescriptionList = planDescription.split(',')
        planDescriptionList1 = []
        planDescriptionList2 = []
        for i in range(0, len(planDescriptionList)):
            planDescriptionList1.append(float(planDescriptionList[i]))
            planDescriptionList2.append(planDescriptionList1[i] / 100)
            # print(planDescriptionList1, planDescriptionList2)
    except:
        pass
    try:
        planName = str(ds.RTPlanName)
        planNameList = planName.split(',')
        planNameList1 = []
        planNameList2 = []
        for i in range (0, len(planNameList)):
            planNameList1.append(float(planNameList[i]))
            planNameList2.append(planNameList1[i]/100)
            # print(planNameList1,planNameList2)
    except:
        pass


    try:
        gantryMaxSpeed = 0.0
        gantryStep = 2
        for i in range(0, len(ds.BeamSequence)):
            if(ds.BeamSequence[i].BeamType == "DYNAMIC"):
                if ((ds.BeamSequence[i].ControlPointSequence[0].DoseRateSet == 0) and (strPlanIntent == "VERIFICATION")):
                    print("Patient QA Collapsed VMAT Plan")
                    for j in range(1, len(ds.BeamSequence[i].ControlPointSequence)):
                        gantryMaxSpeed = planNameList2[i]
                        (ds.BeamSequence[i].ControlPointSequence[j].DoseRateSet) = (((ds.BeamSequence[i].ControlPointSequence[j].CumulativeMetersetWeight)-
                                                                                    (ds.BeamSequence[i].ControlPointSequence[j-1].CumulativeMetersetWeight))*beamMetersetWeightList[i])/(gantryStep/gantryMaxSpeed)*60
                    ds.BeamSequence[i].ControlPointSequence[0].DoseRateSet = ds.BeamSequence[i].ControlPointSequence[1].DoseRateSet

                elif(ds.BeamSequence[i].ControlPointSequence[0].DoseRateSet != 0):
                    try:
                        print("Patient Treatment Plan or Non-Collapsed")
                        for j in range(1, len(ds.BeamSequence[i].ControlPointSequence)):
                            if(strPlanIntent == "VERIFICATION"):
                                gantryMaxSpeed=planNameList2[i]
                            else:
                                gantryMaxSpeed = planDescriptionList2[i]

                            if (ds.BeamSequence[i].ControlPointSequence[j-1].GantryRotationDirection == "CW"):
                                gantryStep = abs((ds.BeamSequence[i].ControlPointSequence[j].GantryAngle)- (ds.BeamSequence[i].ControlPointSequence[j-1].GantryAngle))
                                if (float(ds.BeamSequence[i].ControlPointSequence[j].GantryAngle) < float(ds.BeamSequence[i].ControlPointSequence[j-1].GantryAngle)):
                                    gantryStep = 360 - float(gantryStep)
                                (ds.BeamSequence[i].ControlPointSequence[j].DoseRateSet) = (((ds.BeamSequence[i].ControlPointSequence[j].CumulativeMetersetWeight)-
                                                                                                 (ds.BeamSequence[i].ControlPointSequence[j-1].CumulativeMetersetWeight)) * beamMetersetWeightList[i]) / (gantryStep / gantryMaxSpeed) * 60

                            if (ds.BeamSequence[i].ControlPointSequence[j-1].GantryRotationDirection == "CC"):
                                gantryStep = abs((ds.BeamSequence[i].ControlPointSequence[j].GantryAngle) - (ds.BeamSequence[i].ControlPointSequence[j - 1].GantryAngle))
                                if (float(ds.BeamSequence[i].ControlPointSequence[j].GantryAngle) > float(ds.BeamSequence[i].ControlPointSequence[j - 1].GantryAngle)):
                                    gantryStep = 360 - float(gantryStep)
                                (ds.BeamSequence[i].ControlPointSequence[j].DoseRateSet) = (((ds.BeamSequence[i].ControlPointSequence[j].CumulativeMetersetWeight)-
                                                                                         (ds.BeamSequence[i].ControlPointSequence[j-1].CumulativeMetersetWeight))*beamMetersetWeightList[i])/(gantryStep/gantryMaxSpeed)*60
                            # print(ds.BeamSequence[i].ControlPointSequence[j].DoseRateSet, j)


                    except:
                        print("Not a VMAT Plan.")
                        pass


    except:
        print("Error in Beam Sequence Control Points Sequence")
        pass

    readtxtfile.close()
    ds.save_as(dicom_file)
    print("The Program ends....")




if __name__ == "__main__":
   if len(sys.argv)>1:
      if sys.argv[1]=="0":
          RTPlanTagChangeKrystal(sys.argv[1],sys.argv[2])
      # elif sys.argv[1]=="1":
      #     # CTfileReading(sys.argv[1],sys.argv[2])
      # elif sys.argv[1]=="2":
      #     RTPlanTagChangeKrystal(sys.argv[1],sys.argv[2])


# ArgumentList = "D:\\tempfile\\DicomToSQLArgumentsFile.txt"
# RTPlanTagChangeKrystal("0",ArgumentList)