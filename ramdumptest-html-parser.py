import os
import re
import sys
import math
import platform
import threading
import binascii
import codecs
import re
import fnmatch
import subprocess
import shutil
import zipfile

from lxml import etree
from lxml import html


#========================================================== 
# Function declarification
#==========================================================
#Define the Search elf based on provide radio version

ELF_2_msghash = lambda ELF_address: os.path.join(os.path.dirname(ELF_address),'msg_hash.txt')
    
#Define the Search elf based on provide radio version
def search_elf(search_dir, Radio_version):
    for dirPath, dirNames, fileNames in os.walk(search_dir):   
        for x in fileNames:
            if fnmatch.fnmatch(x, '*'+Radio_version+'*.img'):
                Full_Radio_version = x.split('_')[1]
                for elf in os.listdir(dirPath):
                    if fnmatch.fnmatch(elf, 'M*.elf'):
                        ELF_file = os.path.join(dirPath, elf)
                        print('Match ELF is \r\n %s' %ELF_file)    
                        return ELF_file, Full_Radio_version
        
#Define the Remote Search                         
def search_elf_remote(Radio_str, Radio_release_root):   
    print('>>> Searching Remotely......', end='')
    # Search remote dir by release ver
    if len(Radio_str) == 3: # full radio version, parser & speed up search by release version
        for dir_1 in os.listdir(Radio_release_root): 
            if re.search(Radio_str[1], dir_1):
                new_path = os.path.join(Radio_release_root, dir_1)
                for dir_2 in os.listdir(new_path):
                    if re.search(Radio_str[2], dir_2):
                        new_path = os.path.join(new_path, dir_2)
                        ELF_file_remote_location, Full_Radio_version = search_elf(new_path, Radio_version)                        
                        
    #if Fail, Search all dir from root, support partial Radio ver search
    if ELF_file_remote_location == 0:
        #print('Full search from root dir due to partial Radio_ver')            
        ELF_file_remote_location, Full_Radio_version = search_elf(Radio_release_root, Radio_version)                    
         
        
    #if Found, copy ELF from remote server to Temp_Elf_folder
    if ELF_file_remote_location != 0:
                
        ELF_file_rename = os.path.splitext(os.path.basename(ELF_file_remote_location))[0]+'_'+Radio_str[2]+os.path.splitext(os.path.basename(ELF_file_remote_location))[1]
        Local_ELF_file_location = os.path.join(os.path.join(Temp_Elf_folder, Full_Radio_version), ELF_file_rename)
        
        if not os.path.exists(os.path.dirname(Local_ELF_file_location)):
            os.mkdir(os.path.dirname(Local_ELF_file_location))
        
        print('>>>>>>Found, Copy file from SSD server......')
        shutil.copy(ELF_file_remote_location, Local_ELF_file_location)
        shutil.copy(ELF_2_msghash(ELF_file_remote_location), ELF_2_msghash(Local_ELF_file_location))
        
        #checking the file size, if match, add _fin in the file name.
        if os.path.getsize(Local_ELF_file_location) != os.path.getsize(ELF_file_remote_location):
            return 0
        else:
            print('>>>>>>Finish copying......')
            os.replace(Local_ELF_file_location, os.path.splitext(Local_ELF_file_location)[0]+'_fin'+os.path.splitext(Local_ELF_file_location)[1])
            print('Local_ELF_file_location', Local_ELF_file_location)
            return Local_ELF_file_location

    
#Define the local Search
def search_elf_local(Radio_version_list, search_dir):
    print('>>> Searching Locally......', end='')
    ELF_file = 0
    # Full radio version
    if len(Radio_version_list) == 3:
        Radio_version_part = Radio_version_list[2]
    else:
        Radio_version_part = Radio_version_list[0]
        
    for dirPath, dirNames, fileNames in os.walk(search_dir):   
        for x in fileNames:
            if fnmatch.fnmatch(x, '*'+Radio_version_part+'_fin.elf'):
                print('dirpath', dirPath)
                ELF_file = os.path.join(dirPath, x)
                print('Match ELF locally in  \r\n %s' %ELF_file)
                return ELF_file 
    print('Not found locally')         
    return 0

        
#Define the update_cmm function for update correct cmm script
def update_cmm(read_cmm, write_cmm, replace_target, replace_object):
    with open(write_cmm, 'w') as output_file, open(read_cmm, 'r') as input_file:
        for line in input_file:
            for replace_index in range(len(replace_target)):
                if replace_target[replace_index] in line:
                    output_file.write(line.replace(replace_target[replace_index], replace_object[replace_index]))
                    break
                elif replace_index == len(replace_target)-1:
                    output_file.write(line)    
                    break

#========================================================== 
# Variable declarification
#==========================================================
cmm_path = r'\common\Core\tools\cmm\common\msm8996'

Codebase_root_folder = r'D:\codebase\8996\8996_AND_LA_1.9_12301_UMTS_29.01_0726_c0e35ff_189'

read_loadsim_cmm = r'\std_loadsim_mpss_htc_8996.cmm'
write_loadsim_cmm = r'\std_loadsim_mpss_htc_8996_poser_out.cmm'

read_loadsyms_cmm = r'\std_loadsyms_mpss.cmm'
write_loadsyms_cmm = r'\std_loadsyms_mpss_poser_out.cmm'

read_recover_f3_cmm = r'\recovery_f3_htc.cmm'
write_recover_f3_cmm = r'\recovery_f3_htc_out.cmm'

read_loadsim_cmm_all = Codebase_root_folder+cmm_path+read_loadsim_cmm
write_loadsim_cmm_all = Codebase_root_folder+cmm_path+write_loadsim_cmm

read_loadsyms_cmm_all = Codebase_root_folder+cmm_path+read_loadsyms_cmm
write_loadsyms_cmm_all = Codebase_root_folder+cmm_path+write_loadsyms_cmm

read_recover_f3_cmm_all = Codebase_root_folder+cmm_path+read_recover_f3_cmm
write_recover_f3_cmm_all = Codebase_root_folder+cmm_path+write_recover_f3_cmm

Radio_release_root = r'\\10.116.56.36\Release'
T32_full_path = r'D:\M1\T32_D\bin\windows64\t32mqdsp6'
Temp_Elf_folder = r'D:\M1\dump\ELF_temp'




ELF_file_location = 0
#Radio_release_root = r'C:\Users\poser_lin\Desktop\QXDM_log'
#BIN_file_location = r'\\wsd-abs-w2b-2\David\S1_M1_ITS\268\Ramdump_HT6560300026_20160517035548\DDRCS0.bin'
#Radio_version = '8996-011002-1605051809'



#========================================================== 
# Main function
#==========================================================  

# BIN_file_location = input("Plz input DDRCS0.BIN: \r\n")
# Radio_version = input("Plz input Radio version: ")

BIN_file_location = r'D:\M1\dump\mpss.bin'
Radio_version = r'8996-012301-1607231823'
Radio_version_list = Radio_version.split('-')

ELF_file_location = 0
# Search internal ELF first         
ELF_file_location = search_elf_local(Radio_version_list, Temp_Elf_folder)
                        
# If local Search fail, Search remote dir by release ver
if ELF_file_location == 0:
    ELF_file_location = search_elf_remote(Radio_version_list, Radio_release_root)  
    
  
if ELF_file_location == 0:
    print('Fail to find ELF')
else:
    Replace_in_loadsim = ['DIALOG.FILE *.bin', 'ENTRY &DDRCS0_FILENAME'                    , 'do std_loadsyms_mpss &logpath'           ,'v.write #1 "RCMS_Name = " %STanDard %string htc_smem_ram.RCMS_Name']
    Replace_out_loadsim= [                 '', '&DDRCS0_FILENAME="'+BIN_file_location+'"'  , 'do std_loadsyms_mpss_poser_out &logpath' ,'v.write #1 "qc_image_version_string = " %STanDard %string coredump.image.qc_image_version_string']
            
    Replace_in_loadsyms = ['DIALOG.FILE "&filepath/*&RootElfSuffix"' , 'ENTRY &rvalue_elffile'                   , 'DIALOG.FILE "*&RootElfSuffix"'    ]
    Replace_out_loadsyms= [''                                        , '&rvalue_elffile="'+ELF_file_location+'"' , ''                                 ]    
 
    Replace_in_recover_f3 = ['cd.do ../../../../../modem_proc/core/services/diag/f3_trace/cmm/recover_f3.cmm  &nowpath']
    Replace_out_recover_f3= ['cd.do ../../../../../../modem_proc/core/services/diag/f3_trace/cmm/recover_f3.cmm  '+os.path.dirname(BIN_file_location)+' '+ELF_2_msghash(ELF_file_location)]    
   
    
    update_cmm(read_loadsim_cmm_all, write_loadsim_cmm_all, Replace_in_loadsim, Replace_out_loadsim)
    update_cmm(read_loadsyms_cmm_all, write_loadsyms_cmm_all, Replace_in_loadsyms,Replace_out_loadsyms)
    update_cmm(read_recover_f3_cmm_all, write_recover_f3_cmm_all, Replace_in_recover_f3,Replace_out_recover_f3)
    #change to correct dir
    os.chdir(Codebase_root_folder+cmm_path)

    print('>>> Loading Ramdump by T32......')
    #os.system(T32_full_path + ' -s ' +write_loadsim_cmm_all)

    case_number = input("Case#?, empty for skip the zip process: \r\n")
    if case_number != '':
        print('Zip everything for case#',case_number)
      
        os.chdir(os.path.dirname(BIN_file_location))
        with open('coredump.txt', 'r') as input_file:
            for line in input_file:
                if 'coredump.err.filename = ' in line:
                    crash_filename = line.rstrip().split('= ')[1]
                if 'coredump.err.linenum' in line:
                    crash_fileline = line.rstrip().split('= ')[1]        
        
        case_zip_file = zipfile.ZipFile('case'+case_number+'@'+crash_filename+'#'+crash_fileline+'.zip', mode = 'w')
        case_zip_file.write('f3log.txt')
        case_zip_file.write('coredump.txt')
        
        case_zip_file.write(BIN_file_location, os.path.basename(BIN_file_location))
        case_zip_file.write(ELF_file_location, os.path.basename(ELF_file_location))
        case_zip_file.close()
        