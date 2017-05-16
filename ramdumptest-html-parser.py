import os
import zipfile
import Search_module
import Update_cmm
import read_config


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

        os.chdir(os.path.dirname(BIN_file_location))

        def tryread_coredump(line):
            try:
                parm = line.rstrip().split(':= ')[1]
            except:
                parm = ''
            return parm

        with open('coredump.txt', 'r') as input_file:
            for line in input_file:
                if 'coredump.err.filename' in line:
                    crash_filename = tryread_coredump(line)
                elif 'coredump.err.linenum' in line:
                    crash_fileline = tryread_coredump(line)
                elif 'coredump.err.message' in line:
                    crash_message = tryread_coredump(line)
                elif 'coredump.err.aux_msg' in line:
                    crash_aux_msg = tryread_coredump(line)
                else:
                    crash_aux_msg = ''

        with open('coredump.txt', 'a') as input_file:
            input_file.write('\n'+'Crash on '+ crash_filename +'#'+crash_fileline+': '+crash_message+' "'+crash_aux_msg+'"')

        case_zip_file = zipfile.ZipFile('case' + case_number + '@' + crash_filename + '#' + crash_fileline + '.zip',
                                        mode='w', compression=zipfile.ZIP_DEFLATED)

        if os.path.isfile('_F3log\orig_modem_proc_img_8998_f3log.txt'):
            case_zip_file.write('_F3log\orig_modem_proc_img_8998_f3log.txt')

        msg_hash_qsr = Search_module.search_msg_hash(os.path.dirname(ELF_file_location))

        case_zip_file.write(BIN_file_location, os.path.basename(BIN_file_location))
        case_zip_file.write(ELF_file_location, os.path.basename(ELF_file_location))
        case_zip_file.write(msg_hash_qsr, os.path.basename(msg_hash_qsr))
        case_zip_file.write('coredump.txt')

        case_zip_file.close()
    os.system('explorer ' + os.path.dirname(BIN_file_location))
