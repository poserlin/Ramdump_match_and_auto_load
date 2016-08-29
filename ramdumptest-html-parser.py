import os
import shutil
import zipfile
import re
import Search_module
import Update_cmm

# ==========================================================
# User Variable
# ==========================================================


with open('config.txt', 'r') as config_file:
    for line in config_file:
        if 'Codebase_root_folder' in line:
            Codebase_root_folder = line.rstrip().split('= ')[1]
        elif 'radio_release_root' in line:
            remote_radio_release_root = line.rstrip().split('= ')[1]
        elif 'T32_full_path' in line:
            T32_full_path = line.rstrip().split('= ')[1]
        elif 'local_temp_elf_folder' in line:
            local_temp_elf_folder = line.rstrip().split('= ')[1]
        elif 'local_temp_dump_folder' in line:
            local_temp_dump_folder = line.rstrip().split('= ')[1]

# ==========================================================
# Variable declaration
# ==========================================================

ELF_file_location = 0

# ==========================================================
# Main function
# ==========================================================

BIN_file_location = input("Plz input DDRCS0.BIN: \r\n")


if os.path.basename(BIN_file_location) != 'DDRCS0.BIN' :
    if os.path.splitext(BIN_file_location)[1] == '.zip':
        # zip file found, try tp extract the DDRCSO.BIN from it
        with zipfile.ZipFile(BIN_file_location, 'r') as zip_read:
            for file in zip_read.namelist():
                if 'DDRCS0.BIN' in file:
                    temp_dump_folder = os.path.join(local_temp_dump_folder, os.path.splitext(os.path.basename(BIN_file_location))[0])
                    print('BIN found @ {zip_location}, unzipping to {temp_dump_location} ....'.format(zip_location = file, temp_dump_location = temp_dump_folder))
                    os.mkdir(os.path.splitext(temp_dump_folder)[0])
                    source = zip_read.open(file)
                    target = open(os.path.join(temp_dump_folder, 'DDRCS0.BIN'), 'wb')
                    with source, target:
                        shutil.copyfileobj(source, target)
                        BIN_file_location = target

Radio_version = input("Plz input Radio version: \r\n")
# Search internal ELF first         
ELF_file_location = Search_module.search_elf_local(Radio_version, local_temp_elf_folder)

# If local Search fail, Search remote dir by release ver
if ELF_file_location == 0:
    ELF_file_location = Search_module.search_elf_remote(Radio_version, remote_radio_release_root)

if ELF_file_location == 0:
    print('Fail to find ELF')
else:
    Update_cmm.update_all_cmm(BIN_file_location, ELF_file_location)

    # change to correct dir
    os.chdir(Codebase_root_folder + Update_cmm.cmm_path)

    print('>>> Loading Ramdump by T32......')
    os.system(T32_full_path + ' -s ' + Update_cmm.write_loadsim_cmm_all)

    case_number = input(">>> Input Case number for zip file, empty for skip the zip process: \r\n")
    if case_number != '':
        print('>>> Zip everything for case#', case_number)

        os.chdir(os.path.dirname(BIN_file_location))
        with open('coredump.txt', 'r') as input_file:
            for line in input_file:
                if 'coredump.err.filename = ' in line:
                    crash_filename = line.rstrip().split('= ')[1]
                if 'coredump.err.linenum' in line:
                    crash_fileline = line.rstrip().split('= ')[1]

        case_zip_file = zipfile.ZipFile('case' + case_number + '@' + crash_filename + '#' + crash_fileline + '.zip',
                                        mode='w')
        case_zip_file.write('f3log.txt')
        case_zip_file.write('coredump.txt')

        case_zip_file.write(BIN_file_location, os.path.basename(BIN_file_location))
        case_zip_file.write(ELF_file_location, os.path.basename(ELF_file_location))
        case_zip_file.close()
        os.system('explorer ' + os.path.dirname(BIN_file_location))
