import os
import zipfile
import Search_module

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


# Define the update_cmm function for update correct cmm script

def update_cmm(read_cmm, write_cmm, replace_target, replace_object):
    with open(write_cmm, 'w') as output_file, open(read_cmm, 'r') as input_file:
        for line in input_file:
            for replace_index in range(len(replace_target)):
                if replace_target[replace_index] in line:
                    output_file.write(line.replace(replace_target[replace_index], replace_object[replace_index]))
                    break
                elif replace_index == len(replace_target) - 1:
                    output_file.write(line)
                    break


# ==========================================================
# Variable declaration
# ==========================================================
cmm_path = r'\common\Core\tools\cmm\common\msm8996'

read_loadsim_cmm = r'\std_loadsim_mpss_htc_8996.cmm'
write_loadsim_cmm = r'\std_loadsim_mpss_htc_8996_poser_out.cmm'

read_loadsyms_cmm = r'\std_loadsyms_mpss.cmm'
write_loadsyms_cmm = r'\std_loadsyms_mpss_poser_out.cmm'

read_recover_f3_cmm = r'\recovery_f3_htc.cmm'
write_recover_f3_cmm = r'\recovery_f3_htc_out.cmm'

read_loadsim_cmm_all = Codebase_root_folder + cmm_path + read_loadsim_cmm
write_loadsim_cmm_all = Codebase_root_folder + cmm_path + write_loadsim_cmm

read_loadsyms_cmm_all = Codebase_root_folder + cmm_path + read_loadsyms_cmm
write_loadsyms_cmm_all = Codebase_root_folder + cmm_path + write_loadsyms_cmm

read_recover_f3_cmm_all = Codebase_root_folder + cmm_path + read_recover_f3_cmm
write_recover_f3_cmm_all = Codebase_root_folder + cmm_path + write_recover_f3_cmm

ELF_file_location = 0

# ==========================================================
# Main function
# ==========================================================

BIN_file_location = input("Plz input DDRCS0.BIN: \r\n")
Radio_version = input("Plz input Radio version: ")

# Search internal ELF first         
ELF_file_location = Search_module.search_elf_local(Radio_version, local_temp_elf_folder)

# If local Search fail, Search remote dir by release ver
if ELF_file_location == 0:
    ELF_file_location = Search_module.search_elf_remote(Radio_version, remote_radio_release_root)

if ELF_file_location == 0:
    print('Fail to find ELF')
else:
    Replace_in_loadsim = ['DIALOG.FILE *.bin', 'ENTRY &DDRCS0_FILENAME', 'do std_loadsyms_mpss &logpath',
                          'v.write #1 "RCMS_Name = " %STanDard %string htc_smem_ram.RCMS_Name']
    Replace_out_loadsim = ['', '&DDRCS0_FILENAME="' + BIN_file_location + '"',
                           'do std_loadsyms_mpss_poser_out &logpath',
                           'v.write #1 "qc_image_version_string = " %STanDard %string coredump.image.qc_image_version_string']

    Replace_in_loadsyms = ['DIALOG.FILE "&filepath/*&RootElfSuffix"', 'ENTRY &rvalue_elffile',
                           'DIALOG.FILE "*&RootElfSuffix"']
    Replace_out_loadsyms = ['', '&rvalue_elffile="' + ELF_file_location + '"', '']

    Replace_in_recover_f3 = ['cd.do ../../../../../modem_proc/core/services/diag/f3_trace/cmm/recover_f3.cmm  &nowpath']
    Replace_out_recover_f3 = [
        'cd.do ../../../../../../modem_proc/core/services/diag/f3_trace/cmm/recover_f3.cmm  ' + os.path.dirname(
            BIN_file_location) + ' ' + Search_module.ELF_2_msghash(ELF_file_location)]

    # Update cmm files
    update_cmm(read_loadsim_cmm_all, write_loadsim_cmm_all, Replace_in_loadsim, Replace_out_loadsim)
    update_cmm(read_loadsyms_cmm_all, write_loadsyms_cmm_all, Replace_in_loadsyms, Replace_out_loadsyms)
    update_cmm(read_recover_f3_cmm_all, write_recover_f3_cmm_all, Replace_in_recover_f3, Replace_out_recover_f3)

    # change to correct dir
    os.chdir(Codebase_root_folder + cmm_path)

    print('>>> Loading Ramdump by T32......')
    os.system(T32_full_path + ' -s ' + write_loadsim_cmm_all)

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
