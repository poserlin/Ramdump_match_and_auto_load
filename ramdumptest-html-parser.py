import os
import zipfile
import Search_module
import Update_cmm
import re

# ==========================================================
# User Variable
# ==========================================================


with open('config.txt', 'r') as config_file:
    for line in config_file:
        if 'Codebase_root_folder' in line:
            Codebase_root_folder = line.rstrip().split('= ')[1]
        elif 'T32_full_path' in line:
            T32_full_path = line.rstrip().split('= ')[1]


# ==========================================================
# Variable declaration
# ==========================================================

ELF_file_location = 0
Radio_version = 0
# ==========================================================
# Main function
# ==========================================================

input_file_location = input("Plz input DDRCS0.BIN or Zip file: \r\n")

# Try to find the BIN from zip file
BIN_file_location = Search_module.search_bin(input_file_location)

# Try to read the Radio_version from DUMP
Radio_version = Search_module.search_radio_version(BIN_file_location)

if Radio_version == 0:
    # Radio version not found in BIN file
    Radio_version = input("Plz input Radio version or ELF file: \r\n")
    # Input is elf file location
    if os.path.splitext(Radio_version)[1] == '.elf':
        ELF_file_location = Radio_version

else:
    # create a search instance
    elf = Search_module.Elf_search(Radio_version)
    # Search internal ELF first, If local Search fail, Search remote dir by release ver
    if elf.locally() == 0:
        ELF_file_location = elf.remotely()
    else:
        ELF_file_location = elf.elf_loc

if ELF_file_location == 0:
    print('>> Fail to find the ELF')
else:


    # change to correct dir
    os.chdir(Codebase_root_folder + Update_cmm.cmm_path)

    print('>> Loading Ramdump by T32......')
    os.system(T32_full_path + ' -s ' + Update_cmm.update_all_cmm(BIN_file_location, ELF_file_location))

    case_number = input(">> Input Case number for zip file, empty for skip the zip process: \r\n")
    if case_number != '':
        print('>>>> Zip everything for case#', case_number)
        zip_filename = 'case' + case_number

        os.chdir(os.path.dirname(BIN_file_location))

        def tryread_coredump(line, zip_filename):
            try:
                parm = line.rstrip().split('= ')[1]
                if not not parm:
                    zip_filename += '_' + parm
            except:
                parm = ''
            return parm, zip_filename

        with open('coredump.txt', 'r') as input_file:
            for line in input_file:
                if 'coredump.err.filename = ' in line:
                    crash_filename, zip_filename = tryread_coredump(line, zip_filename)
                elif 'coredump.err.linenum = ' in line:
                    crash_fileline, zip_filename = tryread_coredump(line, zip_filename)
                elif 'coredump.err.aux_msg = ' in line:
                    crash_aux_msg, zip_filename = tryread_coredump(line, zip_filename)
                elif 'coredump.err.message = ' in line:
                    crash_message, zip_filename = tryread_coredump(line, zip_filename)

        with open('coredump.txt', 'a') as input_file:
            input_file.write('\n'+'Crash on '+ zip_filename)

        case_zip_file = zipfile.ZipFile(re.sub('[<>:"/\|?*]','', zip_filename)+'.zip', mode='w', compression=zipfile.ZIP_DEFLATED)

        case_zip_file.write('f3log.txt')
        case_zip_file.write('coredump.txt')

        case_zip_file.write(BIN_file_location, os.path.basename(BIN_file_location))
        case_zip_file.write(ELF_file_location, os.path.basename(ELF_file_location))
        case_zip_file.close()
    os.system('explorer ' + os.path.dirname(BIN_file_location))
