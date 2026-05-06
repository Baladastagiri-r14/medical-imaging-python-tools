import pydicom
import sys

def generatedicom(NewSOP,Planpath):

    print("SOPdata",NewSOP,Planpath)
    dcm = Planpath
    ds = pydicom.read_file(dcm)
    ds.SOPInstanceUID = NewSOP
    ds.save_as(dcm)
    
if __name__ == "__main__":
    print("check")
    generatedicom(sys.argv[1],sys.argv[2])
   
## generatedicom("1.2.826.0.1.3680043.2.1143.7326137517520174900665547453555950537.0","D:\\tempfile\\1.2.826.0.1.3680043.8.498.154946507487693992057678927.dcm")
