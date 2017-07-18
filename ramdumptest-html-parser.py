import os
import zipfile
import Search_module
import Update_cmm
import read_config
import getopt
import sys
import re

# ==========================================================
# Variable declaration
# ==========================================================

ELF_file_location = 0
Radio_version = 0
input_file_location = 0
# ==========================================================
# Main function
# ==========================================================
#process the argument
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:r:h', ['dump_file=', 'radio_ver=', 'help'])
except getopt.GetoptError:
    # usage()
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-h', '--help'):
        print('-d/ --dump_file: Input dump file'+'\r\n'+
              '-r/ --radio_ver: Input radio version' + '\r\n')
        sys.exit(2)
    elif opt in ('-d', '--dump_file'):
        input_file_location = arg
    elif opt in ('-r', '--radio_ver'):
        Radio_version = arg
    else:
        # usage()
        sys.exit(2)

if input_file_location == 0:
    input_file_location = input("Plz input DDRCS0.BIN or Zip file: \r\n")
else:
    print('Input file is {}'.format(input_file_location))
# Try to find the BIN from zip file
BIN_file_location = Search_module.search_bin(input_file_location)

# Try to read the Radio_version from DUMP
if Radio_version == 0:
    Radio_version = Search_module.search_radio_version(BIN_file_location)

    if Radio_version == 0:
        # Radio version not found in BIN file
        Radio_version = input("Plz input Radio version or ELF file: \r\n")
else:
    print('Input radio version is {}'.format(input_file_location))
# determine codebase
read_config.read_from_file(Radio_version)

# Input is elf file location
if os.path.splitext(Radio_version)[1] == '.elf':
    ELF_file_location = Radio_version
# Input is Radio version
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
    os.chdir(read_config.Codebase_root_folder + r'\common\Core\tools\cmm\\')

    print('>>>> Loading Ramdump by T32......')
    os.system(read_config.T32_full_path + ' -s ' + Update_cmm.update_all_cmm(BIN_file_location, ELF_file_location))

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
            input_file.write('\n'+'Crash on '+ crash_filename +'#'+crash_fileline+': '+crash_message+' "'+crash_aux_msg+'"')

        case_zip_file = zipfile.ZipFile(re.sub('[<>:"/\|?*]','', zip_filename)+'.zip', mode='w', compression=zipfile.ZIP_DEFLATED)

        if os.path.isfile('_F3log\orig_modem_proc_img_8998_f3log.txt'):
            case_zip_file.write('_F3log\orig_modem_proc_img_8998_f3log.txt')

        msg_hash_qsr = Search_module.search_msg_hash(os.path.dirname(ELF_file_location))

        case_zip_file.write(BIN_file_location, os.path.basename(BIN_file_location))
        case_zip_file.write(ELF_file_location, os.path.basename(ELF_file_location))
        case_zip_file.write(msg_hash_qsr, os.path.basename(msg_hash_qsr))
        case_zip_file.write('coredump.txt')

        case_zip_file.close()
    os.system('explorer ' + os.path.dirname(BIN_file_location))
