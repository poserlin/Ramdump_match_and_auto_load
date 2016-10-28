import os
from Search_module import ELF_2_msghash

# ==========================================================
# User Variable
# ==========================================================
with open('config.txt', 'r') as config_file:
    for line in config_file:
        if 'Codebase_root_folder' in line:
            Codebase_root_folder = line.rstrip().split('= ')[1]

# ==========================================================
# Variable declaration
# ==========================================================
cmm_path = r'\common\Core\tools\cmm\common\msm8996'
read_loadsim_cmm = r'\std_loadsim_mpss_htc_8996.cmm'
read_loadsyms_cmm = r'\std_loadsyms_mpss.cmm'
read_recover_f3_cmm = r'\recovery_f3_htc.cmm'

# ==========================================================
# Function declaration
# ==========================================================
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


def update_cmm_dict(read_cmm, replace_word_dict):
    write_cmm = read_cmm.replace('.cmm', '_poser_out.cmm')
    with open(write_cmm, 'w') as output_file, open(read_cmm, 'r') as input_file:
        for line in input_file:
            for key in replace_word_dict:
                if key in line:
                    output_file.write(line.replace(key, replace_word_dict[key]))
                else:
                    output_file.write(line)
                break

# ==========================================================
# update_cmm module
# ==========================================================


def update_all_cmm(BIN_file_location, ELF_file_location):
    # Replace string
    replace_in_loadsim = ['DIALOG.FILE *.bin', 'ENTRY &DDRCS0_FILENAME', 'do std_loadsyms_mpss &logpath',
                          'v.write #1 "RCMS_Name = " %STanDard %string htc_smem_ram.RCMS_Name']
    replace_out_loadsim = ['', '&DDRCS0_FILENAME="' + BIN_file_location + '"',
                           'do std_loadsyms_mpss_poser_out &logpath',
                           'v.write #1 "qc_image_version_string = " %STanDard %string coredump.image.qc_image_version_string']

    replace_in_loadsyms = ['DIALOG.FILE "&filepath/*&RootElfSuffix"', 'ENTRY &rvalue_elffile',
                           'DIALOG.FILE "*&RootElfSuffix"']
    replace_out_loadsyms = ['', '&rvalue_elffile="' + ELF_file_location + '"', '']

    replace_in_recover_f3 = ['cd.do ../../../../../modem_proc/core/services/diag/f3_trace/cmm/recover_f3.cmm  &nowpath']
    replace_out_recover_f3 = [
        'cd.do ../../../../../../modem_proc/core/services/diag/f3_trace/cmm/recover_f3.cmm  ' + os.path.dirname(
            BIN_file_location) + ' ' + ELF_2_msghash(ELF_file_location)]

    process_loadsim_dict = dict(zip(replace_in_loadsim, replace_out_loadsim))
    process_loadsyms_dict = dict(zip(replace_in_loadsyms, replace_out_loadsyms))
    process_recover_f3_dict = dict(zip(replace_in_recover_f3, replace_out_recover_f3))

    input_files = [read_loadsim_cmm, read_loadsyms_cmm, read_recover_f3_cmm]
    input_cmm = [Codebase_root_folder + cmm_path + i for i in input_files]
    input_cmm_dict = dict(zip(['loadsim', 'loadsyms', 'recover_f3'], input_cmm))

    update_cmm_dict(input_cmm_dict['loadsim'], process_loadsim_dict)
    update_cmm_dict(input_cmm_dict['loadsyms'], process_loadsyms_dict)
    update_cmm_dict(input_cmm_dict['recover_f3'], process_recover_f3_dict)