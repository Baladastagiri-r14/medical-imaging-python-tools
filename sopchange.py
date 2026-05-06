import pydicom
import dicom
from dicom.dataset import Dataset, FileDataset
from dicom.dataset import Dataset, FileDataset,  DataElement
from dicom.tag import Tag
import pydicom
from pydicom.uid import generate_uid

file_meta = Dataset()
file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.481.5'
file_meta.MediaStorageSOPInstanceUID = dicom.UID.generate_uid()
file_meta.ImplementationClassUID = "1.2.3.4"

savepath = "D:\\tempfile\\RTPLAN\\FluencyMap"
print("sopclassuid",file_meta.MediaStorageSOPClassUID)
print("sopinstanceuid",file_meta.MediaStorageSOPInstanceUID)

savedcm = savepath + "\\"+file_meta.MediaStorageSOPInstanceUID+'.dcm'

ds = FileDataset(savedcm, {}, file_meta=file_meta, preamble=b"\0" * 128)

dicom_file = "D:\\tempfile\\RTPLAN\\RP1.2.752.243.1.1.20241022141209006.3110.23633.dcm"
ds = pydicom.dcmread(dicom_file)

# Tag for SOP Instance UID (0008,0018)
sop_instance_uid_tag = (0x0008, 0x0018)

# Print original SOP Instance UID
print("Original SOP Instance UID:", ds[sop_instance_uid_tag].value)

# New SOP Instance UID (must be a string)
new_sop_instance_uid = file_meta.MediaStorageSOPInstanceUID

# Update the SOP Instance UID value
ds[sop_instance_uid_tag].value = new_sop_instance_uid

# Print the updated SOP Instance UID
print("Updated SOP Instance UID:", ds[sop_instance_uid_tag].value)

# Construct the output file path using the new SOP Instance UID
# output_file = "D:\\tempfile\\RTPLAN\\FluencyMap\\new_sop_instance_uid.dcm"

# Save the modified DICOM file with the new name
print("Writing dcm file", savedcm)
ds.save_as(savedcm)

