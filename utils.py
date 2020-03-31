from pydicom.dataset import Dataset, FileDataset
import datetime, time
import pydicom


def create_secondary_capture(img_data, original_ds):
    filename = 'test.dcm'
    sop_instance_uid = pydicom.uid.generate_uid()
    sop_series_uid = pydicom.uid.generate_uid()
    sop_study_uid = original_ds.SeriesInstanceUID
    sop_class_uid = '1.2.840.10008.5.1.4.1.1.7'

    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = sop_class_uid
    file_meta.MediaStorageSOPInstanceUID = sop_instance_uid
    file_meta.ImplementationClassUID = '1.3.6.1.4.1.9590.100.1.0.100.4.0'
    file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
    ds = FileDataset(filename, {},file_meta = file_meta,preamble=b'\0'*128)
    ds.Modality = 'SYN'
    ds.ContentDate = str(datetime.date.today()).replace('-','')
    ds.ContentTime = str(time.time())

    ds.StudyInstanceUID =  sop_study_uid
    ds.SeriesInstanceUID = sop_series_uid
    ds.SOPInstanceUID = sop_instance_uid
    ds.SOPClassUID = sop_class_uid
    ds.SecondaryCaptureDeviceManufctur = 'AICORE_IMEXHS'
    ds.SeriesDescription = 'AI Diagnostic from ImexHS AI Core'
    ds.Rows, ds.Columns, _ = img_data.shape
    ds.SamplesPerPixel = 3
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.PixelRepresentation = 0
    ds.PhotometricInterpretation = 'RGB'
    ds.PixelData = img_data.tobytes()

    ds.PatientName = original_ds.PatientName
    ds.PatientID = original_ds.PatientID
    ds.PatientBirthDate = original_ds.PatientBirthDate
    ds.PatientSex = original_ds.PatientSex

    ds.is_implicit_VR = False
    ds.save_as(filename)

    return ds