import pydicom

dcm="D:\\dastagiri\\New folder\\06_09_2023_16_00_46_646LMLO_modified.dcm"
ds = pydicom.read_file(dcm)
ds.Manufacturer = "PANACEA"
ds['PatientName'].value = "Jyotshna Begam"
ds.PatientAge = "032Y"
ds.save_as(dcm)

