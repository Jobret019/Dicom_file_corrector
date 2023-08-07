import numpy as np 
from patient_folder_info_extractor import create_empty_copy, extract_file_paths_from_patient_folder, extract_series_paths_from_patient_folder
import os
import pydicom
import shutil
import uid_changer

def patient_folder_corrector(path_main_directory: str, destination_path: str, 
                             path_to_folder: str, dict_patient_translation: dict, 
                             order_of_series_reading: list) -> None:
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
        path_to_patient = os.path.join(patients[patient])
        translation = dict_patient_translation[patients[patient]] 
        patient_corrector(path_main_directory, path_to_patient,
                          destination_path, translation[0],
                          translation[1], translation[2],
                          patients[patient], order_of_series_reading)

def patient_corrector(path_main_directory: str, path_to_patient: str,
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
    path_to_corrected_patient = os.path.abspath(title)

    patient_files_paths = extract_file_paths_from_patient_folder(path_to_patient)
    corrected_patient_series_paths = extract_series_paths_from_patient_folder(path_to_corrected_patient)
    order_of_series_reading = define_order_of_series_correction(path_to_patient)

    image_series = order_of_series_reading[0]
    rtstru_series = order_of_series_reading[1] 
    rtdose_series = order_of_series_reading[2] 
    rtplan_series = order_of_series_reading[3] 

    for serie in order_of_series_reading : 
        if serie == image_series : 
            series_with_ct_file_folder_corrector(patient_files_paths['series0'], path_main_directory, corrected_patient_series_paths['Path_to_series0'],
                                     x_translation, y_translation, z_translation)

        elif serie == rtdose_series :
            rtstru = list(patient_files_paths.keys())[3]
            rtdose = list(patient_files_paths.keys())[1]
            path_new_rt_strut = os.path.join(corrected_patient_series_paths['Path_to_series3'], rtstru)
            no_dvh_and_new_ref_rtstruct_rtdose(patient_files_paths[rtdose], rtdose, path_new_rt_strut) 
            new_path_rtdose = os.path.join(path_main_directory, rtdose)
            shutil.move(new_path_rtdose, corrected_patient_series_paths['Path_to_series1']) 

        elif serie == rtplan_series : 
            rtstru = list(patient_files_paths.keys())[3]
            rtplan = list(patient_files_paths.keys())[2]
            path_new_rt_strut = os.path.join(corrected_patient_series_paths['Path_to_series3'], rtstru)
            uid_changer.save_rtplan_referenced_structure_set(patient_files_paths[rtplan], rtplan, path_new_rt_strut)
            new_path_rtplan = os.path.join(path_main_directory, rtplan)
            shutil.move(new_path_rtplan, corrected_patient_series_paths['Path_to_series2']) 

        elif serie == rtstru_series : 
            rtstru = list(patient_files_paths.keys())[3]
            rtstruct_file_corrector_position(patient_files_paths[rtstru], z_translation, rtstru, corrected_patient_series_paths['Path_to_series0'])
            new_path_rtstru = os.path.join(path_main_directory, rtstru)
            shutil.move(new_path_rtstru, corrected_patient_series_paths['Path_to_series3']) 

def rtstruct_file_corrector_position(path_to_structure: str, z_translation: float, title: str, path_to_new_series0) -> None : 
    """
    This method create a corrected RTSTRUCT file from an RTSTRUCT file with inverted and 
    incorrect contour z position data  
    :param path_to_structure : the path of the RTSTRUCT Dicom file
    :param z_translation : the value of the z component of the translation  
    :param title : The title of the corrected RTSTRUCT file
    :return : None 
    """
    open_structure = pydicom.dcmread(path_to_structure)
    contours_sequence = open_structure.ROIContourSequence
    for structure in range(len(contours_sequence)) :
        contour_sequence = contours_sequence[structure].ContourSequence
        for contour in range(len(contour_sequence)) :
            corrected_contour_data = contour_position_corrector(contour_sequence, contour, 0, 0, z_translation)
            open_structure.ROIContourSequence[structure].ContourSequence[contour].ContourData = corrected_contour_data
    string_z_translation = str(z_translation) + ' mm'
    open_structure.StructureSetDescription = 'All the contours in these structures were corrected with an inversion and then a shift of ' + string_z_translation + ' in z with an ICP algorithm. GIT : https://github.com/Jobret019/Dicom_file_corrector.git, commit X'
    uid_changer.change_rtstruct_uids(open_structure, path_to_new_series0)
    open_structure.save_as(title)


def no_dvh_and_new_ref_rtstruct_rtdose(path_to_rtdose: str, title: str, path_to_new_rtstruct: str) -> None : 
    """
    This method remove the DVH data from a RTDOSE Dicom file and change the referenced RTSTRUCT
    :param path_to_RTDOSE : the path of the RTDOSE Dicom file
    :param title : the title of the corrected RT dose file
    :param path_to_new_rtstruct : the path to the new RTSTRUCT file that the RTDOSE refer too
    return : None 
    """
    open_dose = pydicom.dcmread(path_to_rtdose) 
    del open_dose.DVHNormalizationDoseValue
    del open_dose.DVHNormalizationPoint
    del open_dose.DVHSequence 
    uid_changer.change_referenced_rtstruct(open_dose, path_to_new_rtstruct)
    open_dose.save_as(title)

def series_with_ct_file_folder_corrector(path_to_series0: str, path_main_directory: str,
                              path_to_new_series0_folder: str, x_translation: float, 
                              y_translation: float, z_translation: float) -> None : 
    """
    This method create and transfer all the corrected CT images file in a new series0 folder  
    :param path_to_series0 : the path of the series0 of the Dicom file
    :param path_main_directory : the path of the directory of the python project (where the CT.dcm go after the save.as())
    :param path_to_new_series0_folder : the path of the folder where all the CT file will go 
    :param x_translation : the value of the x component of the translation
    :param y_translation : the value of the y component of the translation
    :param z_translation : the value of the z component of the translation  
    :return : None
    """
    images_files = os.listdir(path_to_series0)
    new_series0_instance_uid = uid_changer.generate_uid()
    for image in range(len(images_files)) : 
        complete_path = os.path.join(path_to_series0, images_files[image])
        title = images_files[image]
        new_path = os.path.join(path_main_directory, title)
        ct_image_file_corrector_position(complete_path, x_translation, 
                                y_translation, z_translation,
                                title, new_series0_instance_uid)
        shutil.move(new_path, path_to_new_series0_folder) 

def ct_image_file_corrector_position(path_to_ct_file: str, x_translation: float, y_translation: float, 
                            z_translation: float, title: str, series_instance_uid : str = None) -> None : 
    """
    This method correct a CT file with inverted z position and shifted Image Position. The method 
    create a new corrected CT file 
    :param path_to_CT_file: the path of the CT Dicom file 
    :param x_translation : the value of the x component of the translation
    :param y_translation : the value of the y component of the translation
    :param z_translation : the value of the z component of the translation 
    :param title : the title of the new CT Dicom file 
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
    open_image.ImageComments = 'The Image Position (Patient) was corrected with an inversion in z and then a shift of ' + string_x_translation + ' in x, ' + string_y_translation + ' in y and ' + string_z_translation + ' in z with an ICP algorithm. GIT : https://github.com/Jobret019/Dicom_file_corrector.git, commit X'
    uid_changer.change_and_store_ct_uids(open_image)
    if series_instance_uid != None : 
        uid_changer.change_ct_series_instance_uid(open_image, series_instance_uid) 
    open_image.save_as(title)

def contour_position_corrector(contour_sequence: object, contour: int, x_translation: float,
                       y_translation: float, z_translation: float) -> np.array :
    """
    This method inverse the z coordinates and then shift a structure contours in a direction
    :param contour_sequence : The contour sequence of the DICOM in which the contour position 
    data are located 
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
            print(open_dicom.SOPClassUID)
            if open_dicom.SOPClassUID == rtdose_class_uid : 
                order[2]=i 
            if open_dicom.SOPClassUID == rtplan_class_uid : 
                order[3]=i 
            if open_dicom.SOPClassUID == rtstruc_class_uid : 
                order[1]=i 
    return order
