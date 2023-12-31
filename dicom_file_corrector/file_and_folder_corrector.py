import numpy as np 
from patient_folder_info_extractor import create_empty_copy, extract_file_paths_from_patient_folder, extract_series_paths_from_patient_folder
import os
import pydicom
import shutil
import uid_changer

def correct_folder_of_patient(path_main_directory: str, destination_path: str, 
                             path_to_folder: str, dict_patient_translation: dict) -> None:
    """
    This method correct all the patient in a folder full of them. 
    :param path_main_directory : the path of the folder containing the entire project 
    :param destination_path : the path of the location where the user want to put the patient folder
    :param path_to_folder : the path of the folder containing all the patient 
    :param dict_patient_translation : a dictionnary with all the patient as keys and the translation for 
    correction as value 
    return : None 
    """
    patients = os.listdir(path_to_folder) 
    for patient in range(len(patients)) : 
        path_to_patient = os.path.join(path_to_folder, patients[patient])
        translation = dict_patient_translation[patients[patient]] 
        correct_patient_folder(path_main_directory, path_to_patient,
                          destination_path, translation[0][0],
                          translation[1][0], translation[2][0],
                          patients[patient])

def correct_patient_folder(path_main_directory: str, path_to_patient: str,
                      destination_path: str, x_translation: float,
                      y_translation: float, z_translation: float,
                      title: str) -> None : 
    """
    This method correct a patient folder with incorrect structure contour position and incorrect Image position 
    
    :param path_main_directory : the path of the folder containing the entire project 
    :param path_to_patient : the path of the patient that need to be corrected 
    :param destination_path : the path of the location where the user want to put the patient folder
    :param x_translation : the value of the x component of the translation
    :param y_translation : the value of the y component of the translation
    :param z_translation : the value of the z component of the translation  
    :param title : the title of the new patient folder 
    :return : None
    """
    create_empty_copy(path_to_patient, destination_path,title)
    path_to_corrected_patient = os.path.join(destination_path, title)
    comment='GIT : https://github.com/Jobret019/Dicom_file_corrector.git, commit dc7b788. The ReferencedImageSequence and RelatedSeriesSequence refere to the image before correction'

    patient_files_paths = extract_file_paths_from_patient_folder(path_to_patient)
    corrected_patient_series_paths = extract_series_paths_from_patient_folder(path_to_corrected_patient)
    order_of_series_reading = define_order_of_series_correction(path_to_patient)

    image_series = order_of_series_reading[0]
    rtstru_series = order_of_series_reading[1] 
    rtdose_series = order_of_series_reading[2] 
    rtplan_series = order_of_series_reading[3] 

    new_rtplan_instance_uid = uid_changer.generate_uid()
    new_rtdose_instance_uid = uid_changer.generate_uid()
    new_rtstruct_instance_uid = uid_changer.generate_uid()

    for serie in order_of_series_reading : 
        if serie == image_series : 
            correct_a_series_folder_with_ct_files(patient_files_paths['series0'], path_main_directory, corrected_patient_series_paths['Path_to_series0'],
                                     x_translation, y_translation, z_translation, comment)

        elif serie == rtdose_series :
            rtdose = list(patient_files_paths.keys())[1]
            make_a_no_dvh_and_new_ref_rtstruct_rtdose(patient_files_paths[rtdose], rtdose, new_rtplan_instance_uid, new_rtstruct_instance_uid, new_rtdose_instance_uid) 
            new_path_rtdose = os.path.join(path_main_directory, rtdose)
            shutil.move(new_path_rtdose, corrected_patient_series_paths['Path_to_series1']) 

        elif serie == rtplan_series : 
            rtplan = list(patient_files_paths.keys())[2]
            uid_changer.change_rtplan_uid(patient_files_paths[rtplan], rtplan, new_rtstruct_instance_uid, new_rtdose_instance_uid, new_rtplan_instance_uid)
            new_path_rtplan = os.path.join(path_main_directory, rtplan)
            shutil.move(new_path_rtplan, corrected_patient_series_paths['Path_to_series2']) 

        elif serie == rtstru_series : 
            rtstru = list(patient_files_paths.keys())[3]
            correct_rtstruct_file_position(patient_files_paths[rtstru], z_translation, rtstru, corrected_patient_series_paths['Path_to_series0'], comment, new_rtstruct_instance_uid)
            new_path_rtstru = os.path.join(path_main_directory, rtstru)
            shutil.move(new_path_rtstru, corrected_patient_series_paths['Path_to_series3']) 

def correct_rtstruct_file_position(path_to_rtstruct: str, z_translation: float, title: str, path_to_new_series0: str, other_comment: str, new_sop_instance_uid : str) -> None : 
    """
    This method create a corrected RTSTRUCT file from an RTSTRUCT file with inverted and 
    incorrect contour z position data  
    :param path_to_structure : the path of the RTSTRUCT Dicom file
    :param z_translation : the value of the z component of the translation  
    :param path_to_new_series0 : the path of the new referenced series0
    :param title : The title of the corrected RTSTRUCT file
    :param other_comments : a comment to add with the default comment
    :param new_sop_instance_uid : the new sop instance of the rtstruct
    :return : None 
    """
    open_structure = pydicom.dcmread(path_to_rtstruct)
    contours_sequence = open_structure.ROIContourSequence
    for structure in range(len(contours_sequence)) :
        contour_sequence = contours_sequence[structure].ContourSequence
        for contour in range(len(contour_sequence)) :
            corrected_contour_data = correct_contour_position(contour_sequence, contour, 0, 0, z_translation)
            open_structure.ROIContourSequence[structure].ContourSequence[contour].ContourData = corrected_contour_data
    string_z_translation = str(z_translation) + ' mm'
    open_structure.StructureSetDescription = 'All the contours in these structures were corrected with an inversion and then a shift of ' + string_z_translation + ' in z with an ICP algorithm.' + other_comment
    uid_changer.change_rtstruct_uids(open_structure, path_to_new_series0, new_sop_instance_uid)
    open_structure.save_as(title)


def make_a_no_dvh_and_new_ref_rtstruct_rtdose(path_to_rtdose: str, title: str, rt_plan_new_sop_instance_uid: str, 
                                              rtstruc_new_sop_instance_uid : str, new_sop_instance_uid : str) -> None : 
    """
    This method remove the DVH data from a RTDOSE Dicom file and change the referenced RTSTRUCT
    :param path_to_RTDOSE : the path of the RTDOSE Dicom file
    :param title : the title of the corrected RT dose file
    :param rt_plan_new_sop_instance_uid : the uid of the new rtplan
    :param rtstruc_new_sop_instance_uid : the uid of the new rtstruc
    :param new_sop_instance_uid :: the uid of the new rtdose
    """
    open_dose = pydicom.dcmread(path_to_rtdose) 
    del open_dose.DVHNormalizationDoseValue
    del open_dose.DVHNormalizationPoint
    del open_dose.DVHSequence 
    uid_changer.change_referenced_rtplan(open_dose, rt_plan_new_sop_instance_uid)
    uid_changer.change_referenced_rtstruct(open_dose, rtstruc_new_sop_instance_uid)
    uid_changer.change_for_choose_sop_instance_uid(open_dose, new_sop_instance_uid)
    uid_changer.change_series_instance_uid(open_dose)
    open_dose.save_as(title)

def correct_a_series_folder_with_ct_files(path_to_series0: str, path_main_directory: str,
                              path_to_new_series0_folder: str, x_translation: float, 
                              y_translation: float, z_translation: float, other_comments: str) -> None : 
    """
    This method create and transfer all the corrected CT images file in a new series0 folder  
    :param path_to_series0 : the path of the series0 of the Dicom file
    :param path_main_directory : the path of the directory of the python project (where the CT.dcm go after the save.as())
    :param path_to_new_series0_folder : the path of the folder where all the CT file will go 
    :param x_translation : the value of the x component of the translation
    :param y_translation : the value of the y component of the translation
    :param z_translation : the value of the z component of the translation  
    :param other_comments : a comment to add with the default comment
    :return : None
    """
    images_files = os.listdir(path_to_series0)
    new_series0_instance_uid = uid_changer.generate_uid()
    for image in range(len(images_files)) : 
        complete_path = os.path.join(path_to_series0, images_files[image])
        title = images_files[image]
        new_path = os.path.join(path_main_directory, title)
        correct_ct_image_file_position(complete_path, x_translation, 
                                y_translation, z_translation,
                                title, other_comments, new_series0_instance_uid)
        shutil.move(new_path, path_to_new_series0_folder) 

def correct_ct_image_file_position(path_to_ct_file: str, x_translation: float, y_translation: float, 
                            z_translation: float, title: str, other_comments: str, series_instance_uid : str = None) -> None : 
    """
    This method correct a CT file with inverted z position and shifted Image Position. The method 
    create a new corrected CT file 
    :param path_to_CT_file: the path of the CT Dicom file 
    :param x_translation : the value of the x component of the translation
    :param y_translation : the value of the y component of the translation
    :param z_translation : the value of the z component of the translation 
    :param title : the title of the new CT Dicom file 
    :param other_comments : a comment to add with the default comment
    :param series_instance_uid : the uid of the new series containing the image file
    :return : None
    """
    open_image = pydicom.dcmread(path_to_ct_file) 
    open_image.ImagePositionPatient[0] += x_translation
    open_image.ImagePositionPatient[1] += y_translation
    open_image.ImagePositionPatient[2] = -open_image.ImagePositionPatient[2]
    open_image.ImagePositionPatient[2] += z_translation
    string_x_translation = str(x_translation)+' mm'
    string_y_translation = str(y_translation)+' mm'
    string_z_translation = str(z_translation)+' mm'
    open_image.ImageComments = 'The Image Position (Patient) was corrected with an inversion in z and then a shift of ' + string_x_translation + ' in x, ' + string_y_translation + ' in y and ' + string_z_translation + ' in z with an ICP algorithm.'+ other_comments
    uid_changer.change_and_store_ct_uids(open_image)
    if series_instance_uid != None : 
        uid_changer.change_ct_series_instance_uid(open_image, series_instance_uid) 
    open_image.save_as(title)

def correct_contour_position(contour_sequence: object, contour: int, x_translation: float,
                       y_translation: float, z_translation: float) -> np.array :
    """
    This method inverse the z coordinates and then shift a structure contours in a direction
    :param contour_sequence : The contour sequence of the DICOM in which the contour position 
    data are located 
    :param contour_sequence : a dicom dataset object containing all the contours of all the organs
    :param contour : the number link to the contour  
    :param x_translation : the value of the x component of the translation
    :param y_translation : the value of the y component of the translation
    :param z_translation : the value of the z component of the translation  
    :return : the contour array shifted by the translation
    """
    contour_data = contour_sequence[contour].ContourData
    corrected_contour_data = []
    x_contour_data = contour_data[0::3]
    y_contour_data = contour_data[1::3]
    z_contour_data = contour_data[2::3]
    for i in range(len(x_contour_data)) :
        x_contour_data[i] += x_translation
    for i in range(len(y_contour_data)) :
        y_contour_data[i] += y_translation
    for i in range(len(z_contour_data)) :
        z_contour_data[i] = -z_contour_data[i]
        z_contour_data[i] += z_translation
    for i in range(len(x_contour_data)) :
        corrected_contour_data += [x_contour_data[i], ]
        corrected_contour_data += [y_contour_data[i], ]
        corrected_contour_data += [z_contour_data[i], ]
    return corrected_contour_data

def define_order_of_series_correction(path_to_patient: str) -> list : 
    """
    This method define the order of correction of every series in a patient folder. The 
    order is the following : [CT image series, RT Struct series, RT Dose series, RT plan series]
    :param path_to_patient : the path leading to the patient
    :return : a list of numbers associated with their series. For example [0,3,1,2] means that the 
    order of reading is series0, series3, series1 and series2
    """   
    order = [0, 0, 0, 0]
    
    study = os.listdir(path_to_patient)[0]
    path_to_study = os.path.join(path_to_patient, study)   
    series = os.listdir(path_to_study)
    path_series0 = os.path.join(path_to_study, series[0])
    path_series1 = os.path.join(path_to_study, series[1])
    path_series2 = os.path.join(path_to_study, series[2])
    path_series3 = os.path.join(path_to_study, series[3])

    list_of_files_in_series0 = os.listdir(path_series0)
    file_in_series0 = list_of_files_in_series0[0]
    path_file_in_series0 = os.path.join(path_series0, file_in_series0)
    list_of_files_in_series1 = os.listdir(path_series1)
    file_in_series1 = list_of_files_in_series1[0]
    path_file_in_series1 = os.path.join(path_series1, file_in_series1)
    list_of_files_in_series2 = os.listdir(path_series2)
    file_in_series2 = list_of_files_in_series2[0]
    path_file_in_series2 = os.path.join(path_series2, file_in_series2)
    list_of_files_in_series3 = os.listdir(path_series3)
    file_in_series3 = list_of_files_in_series3[0]
    path_file_in_series3 = os.path.join(path_series3, file_in_series3)

    list_of_list_of_files = [list_of_files_in_series0, list_of_files_in_series1, list_of_files_in_series2, list_of_files_in_series3]
    list_of_file_path = [path_file_in_series0, path_file_in_series1, path_file_in_series2, path_file_in_series3] 

    rtdose_class_uid = '1.2.840.10008.5.1.4.1.1.481.2'
    rtplan_class_uid = '1.2.840.10008.5.1.4.1.1.481.5'
    rtstruc_class_uid = '1.2.840.10008.5.1.4.1.1.481.3'

    for i in range(len(list_of_list_of_files)) : 
        if len(list_of_list_of_files[i]) > 1 : 
            order[0] = i
        elif len(list_of_list_of_files[i]) == 1 : 
            open_dicom = pydicom.dcmread(list_of_file_path[i]) 
            if open_dicom.SOPClassUID == rtdose_class_uid : 
                order[2] = i 
            if open_dicom.SOPClassUID == rtplan_class_uid : 
                order[3] = i 
            if open_dicom.SOPClassUID == rtstruc_class_uid : 
                order[1] = i 
    return order
