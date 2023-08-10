import pydicom 
from typing import Optional,List
import os

def save_rtplan_referenced_structure_set(path_to_rtplan: str, title: str, path_to_new_rtstruct: str) -> None : 
    """
    This method create a new RTPLAN file with a new referenced structure set 
    :param path_to_rtplan: the path to the RTPLAN file
    :param title : the title of the new RTPLAN file
    :param path_to_new_path_to_new_rtstr : the path of a new rtstruct
    return : None 
    """    
    open_plan = pydicom.dcmread(path_to_rtplan) 
    change_referenced_rtstruct(open_plan, path_to_new_rtstruct)
    open_plan.save_as(title)

def change_referenced_rtstruct(file_dataset: pydicom.FileDataset, path_to_new_rtstru: str) -> None :
    """
    This method refer a DICOM file to a new rtstruct file 
    :param file_dataset : a pydicom file dataset
    :param path_to_new_path_to_new_rtstr : the path of a new rtstruct
    return : None 
    """   
    open_rtstru = pydicom.dcmread(path_to_new_rtstru)
    rtstruc_new_sop_instance_uid = open_rtstru.SOPInstanceUID 
    file_dataset.ReferencedStructureSetSequence[0].ReferencedSOPInstanceUID = rtstruc_new_sop_instance_uid


def change_rtstruct_uids(rtstrut_file_dataset: pydicom.FileDataset, path_to_new_series0_folder: str) -> None : 
    """
    This method change some UIDs of a rtstruct file and store the old one in appropriate attribute
    :param rtstrut_file_dataset : a pydicom rtstruct file type dataset
    :param path_to_new_series_0_folder : the path of a new series0 folder with all the new images 
    return : None 
    """
    add_PredecessorStructureSet(rtstrut_file_dataset)
    change_contour_image_referenced_sop_uid(rtstrut_file_dataset, path_to_new_series0_folder)
    change_sop_instance_uid(rtstrut_file_dataset)
    change_series_instance_uid(rtstrut_file_dataset)
    change_frame_of_reference_series0_instance_uid(rtstrut_file_dataset, path_to_new_series0_folder)

def change_contour_image_referenced_sop_uid(rtstrut_file_dataset: pydicom.FileDataset, path_to_new_series0_folder: str) -> None : 
    """
    This method refer all contour in a rtstruct file with the new images SOPInstanceUID 
    :param rtstrut_file_dataset : a pydicom rtstruct type dataset
    :param path_to_new_series_0_folder : the path of a new series0 folder with all the new images 
    return : None
    """    
    dict_sop_series0 = create_dict_of_sop_series0(path_to_new_series0_folder)
    contour_image_sequence = rtstrut_file_dataset.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[0].ContourImageSequence
    for i in range(len(contour_image_sequence)): 
        contour = contour_image_sequence[i]
        old_sop_instance_uid = contour.ReferencedSOPInstanceUID 
        new_sop_instance_uid = find_new_sop_instance_uid(dict_sop_series0,old_sop_instance_uid) 
        rtstrut_file_dataset.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[0].ContourImageSequence[i].ReferencedSOPClassUID = new_sop_instance_uid

def change_frame_of_reference_series0_instance_uid(rtstrut_file_dataset: pydicom.FileDataset, path_to_new_series_0_folder: str) -> None : 
    """
    This method refer the ReferencedSeriesInstanceUID attribute which is in the ReferencedFrameOfReference attribute 
    with a new SeriesInstanceUID
    :param rtstrut_file_dataset : a pydicom rtstruct type dataset
    :param path_to_new_series_0_folder : the path of a new series0 folder with the new SeriesInstanceUID
    return : None
    """
    images = os.listdir(path_to_new_series_0_folder) 
    path_image = os.path.join(path_to_new_series_0_folder, images[0])
    open_image = pydicom.dcmread(path_image) 
    new_series0_UID = open_image.SeriesInstanceUID 
    rtstrut_file_dataset.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[0].SeriesInstanceUID = new_series0_UID

def add_PredecessorStructureSet(rtstrut_file_dataset: pydicom.FileDataset) -> None : 
    """
    This method add the PredecessorStructureSet attribute in a rtstruct file dataset. It containin 
    the present SOPInstanceUID and SOPClassUID of the rtstruct file
    :param rtstrut_file_dataset : a pydicom rtstruct type dataset
    return : None
    """
    predecessor_structure_set_sequence = pydicom.Dataset()
    predecessor_structure_set_sop_class_uid = rtstrut_file_dataset.SOPClassUID
    predecessor_structure_set_sop_instance_uid = rtstrut_file_dataset.SOPInstanceUID
    rtstrut_file_dataset.PredecessorStructureSetSequence = pydicom.Sequence([predecessor_structure_set_sequence])
    rtstrut_file_dataset.PredecessorStructureSetSequence[0].ReferencedSOPClassUID = predecessor_structure_set_sop_class_uid
    rtstrut_file_dataset.PredecessorStructureSetSequence[0].ReferencedSOPInstanceUID = predecessor_structure_set_sop_instance_uid


def find_new_sop_instance_uid(dict_sop_series0: dict, old_sop_instance_uid_associated: str) -> str :
    """
    This method search in a dictionnary create with dict_sop_series0_creator the patient with the
    new SOPInstanceUID associated with a given old SOPInstanceUID
    :param dict_sop_series0 : a dictionnary created with dict_sop_series0_creator
    :param old_sop_associated : the old SOPInstanceUID of the image 
    return : the new SOPInstance UID of the image
    """    
    images = list(dict_sop_series0.keys()) 
    new_sop_instance_uid = ''
    for image in range(len(images)) : 
        if dict_sop_series0[images[image]][0] == old_sop_instance_uid_associated : 
            new_sop_instance_uid = dict_sop_series0[images[image]][1]
    return new_sop_instance_uid


def create_dict_of_sop_series0(path_to_new_series0_folder: str) -> dict : 
    """
    This method create a dictionnary associating an image of the series0 with his 
    old image and new image SOPInstanceUID
    :param path_to_new_series0_folder : the path of a position corrected series0 folder 
    return : a dictionnary with image files names as keys and a list with the old images SOPInstanceUID 
    and new images SOPInstanceUID as values 
    """    
    dict = {}
    images = os.listdir(path_to_new_series0_folder) 
    for image in range(len(images)): 
        path_ct_file = os.path.join(path_to_new_series0_folder, images[image])
        open_image = pydicom.dcmread(path_ct_file) 
        old_sop = open_image.ReferencedImageSequence[0].ReferencedSOPInstanceUID
        new_sop = open_image.SOPInstanceUID 
        dict[images[image]] = [old_sop, new_sop]
    return dict


def change_and_store_ct_uids(ct_file_dataset: pydicom.FileDataset) -> None :
    """
    This method change some UIDs of a ct file and store the old one in 
    appropriate attribute
    :param ct_file_dataset : a pydicom ct file type dataset
    return : None 
    """
    add_referenced_image_sequence(ct_file_dataset)
    add_related_series_sequence(ct_file_dataset)
    change_sop_instance_uid(ct_file_dataset) 

def change_sop_instance_uid(file_dataset: pydicom.FileDataset) -> None :  
    """
    This method change the present SOPInstanceUID of a file with a new random one 
    :param file_dataset : a pydicom file dataset
    return : None 
    """
    file_dataset.SOPInstanceUID = generate_uid()

def change_series_instance_uid(file_dataset: pydicom.FileDataset) -> None :  
    """
    This method change the present SeriesInstanceUID of a file with a new random one 
    :param ct_file_dataset : a pydicom ct file type dataset
    return : None 
    """
    file_dataset.SeriesInstanceUID = generate_uid()

def change_ct_series_instance_uid(ct_file_dataset: pydicom.FileDataset, new_series_instance_uid: str) -> None : 
    """
    This method change the present SeriesInstanceUID of a CT file with a new predefined one 
    :param ct_file_dataset : a pydicom ct file type dataset
    :param new_series_instance_uid : the new SeriesInstanceUID that replace the old one 
    return : None 
    """
    ct_file_dataset.SeriesInstanceUID = new_series_instance_uid

def add_referenced_image_sequence(ct_file_dataset: pydicom.FileDataset) -> None : 
    """
    This method add the ReferencedImageSequence attribute in a ct file dataset. It contain the present 
    SOPInstanceUID and SOPClassUID of the ct file
    :param ct_file_dataset : a pydicom ct file type dataset
    return : None 
    """
    referenced_image_sequence = pydicom.Dataset()
    referenced_image_sop_class_uid = ct_file_dataset.SOPClassUID
    referenced_image_sop_instance_uid = ct_file_dataset.SOPInstanceUID
    ct_file_dataset.ReferencedImageSequence=pydicom.Sequence([referenced_image_sequence])
    ct_file_dataset.ReferencedImageSequence[0].ReferencedSOPClassUID = referenced_image_sop_class_uid
    ct_file_dataset.ReferencedImageSequence[0].ReferencedSOPInstanceUID = referenced_image_sop_instance_uid

def add_related_series_sequence(ct_file_dataset: pydicom.FileDataset) -> None : 
    """
    This method add the RelatedSeriesSequence attribute in a ct file dataset.It contain the present 
    SeriesInstanceUID and StudyInstanceUID of the ct file
    :param ct_file_dataset : a pydicom ct file type dataset
    return : None 
    """
    referenced_series_sequence = pydicom.Dataset()
    referenced_image_study_instance_uid = ct_file_dataset.StudyInstanceUID
    referenced_image_series_instance_uid = ct_file_dataset.SeriesInstanceUID
    ct_file_dataset.RelatedSeriesSequence = pydicom.Sequence([referenced_series_sequence])
    ct_file_dataset.RelatedSeriesSequence[0].StudyInstanceUID = referenced_image_study_instance_uid
    ct_file_dataset.RelatedSeriesSequence[0].SeriesInstanceUID = referenced_image_series_instance_uid

def generate_uid(entropy_sources: Optional[List[str]] = None) -> pydicom.uid.UID:
    """Generate a unique DICOM UID with the GRPM prefix.
    Parameters
    ----------
    entropy_sources
        The GRPM prefix will be appended with a SHA512 hash of the given list
        which means the result is deterministic and should make the original
        data unrecoverable.
    Returns
    -------
    str
        A DICOM UID of up to 64 characters.
    """
    GRPM_PREFIX=GRPM_PREFIX = '1.2.826.0.1.3680043.10.424.'
    return pydicom.uid.generate_uid(prefix=GRPM_PREFIX, entropy_srcs=entropy_sources)