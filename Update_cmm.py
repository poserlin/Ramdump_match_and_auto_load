import os
import fnmatch
from Search_module import ELF_2_msghash,BIN_2_smem

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
write_loadsim_cmm = r'\std_loadsim_mpss_htc_8996_poser_out.cmm'

read_loadsim_SSR_cmm = r'\std_loadsim_mpss_htc_8996_SSR.cmm'
write_loadsim_SSR_cmm = r'\std_loadsim_mpss_htc_8996_SSR_poser_out.cmm'

read_loadsyms_cmm = r'\std_loadsyms_mpss.cmm'
write_loadsyms_cmm = r'\std_loadsyms_mpss_poser_out.cmm'

read_recover_f3_cmm = r'\recovery_f3_htc.cmm'
write_recover_f3_cmm = r'\recovery_f3_htc_out.cmm'

read_loadsim_cmm_all = Codebase_root_folder + cmm_path + read_loadsim_cmm
write_loadsim_cmm_all = Codebase_root_folder + cmm_path + write_loadsim_cmm

read_loadsim_SSR_cmm_all = Codebase_root_folder + cmm_path + read_loadsim_SSR_cmm
write_loadsim_SSR_cmm_all = Codebase_root_folder + cmm_path + write_loadsim_SSR_cmm

read_loadsyms_cmm_all = Codebase_root_folder + cmm_path + read_loadsyms_cmm
write_loadsyms_cmm_all = Codebase_root_folder + cmm_path + write_loadsyms_cmm

read_recover_f3_cmm_all = Codebase_root_folder + cmm_path + read_recover_f3_cmm
write_recover_f3_cmm_all = Codebase_root_folder + cmm_path + write_recover_f3_cmm


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


# ==========================================================
# update_cmm module
# ==========================================================
def update_all_cmm(BIN_file_location, ELF_file_location):

    # Replace string
    replace_in_loadsim = ['DIALOG.FILE *.bin', 'ENTRY &DDRCS0_FILENAME', 'do std_loadsyms_mpss &logpath',
                          'v.write #1 "RCMS_Name = " %STanDard %string htc_smem_ram.RCMS_Name',
                          'v.write #1 "qxdm_dbg_msg = " %STanDard %string qxdm_dbg_msg',
                          'GOSUB POSTMORTEM_ANALYSIS']
    replace_out_loadsim = ['', '&DDRCS0_FILENAME="' + BIN_file_location + '"',
                           'do std_loadsyms_mpss_poser_out &logpath',
                           'v.write #1 "qc_image_version_string = " %STanDard %string coredump.image.qc_image_version_string',
                           'v.write #1 "aux_msg = " %STanDard %string coredump.err.aux_msg',
                           'do recovery_f3_htc_out']

    replace_in_loadsim_SSR = ['DIALOG.FILE *.bin', 'ENTRY &DDRCS0_FILENAME',
                              'dialog.file ramdump_smem_*.bin', 'entry &SMEM_log',
                              'do std_loadsyms_mpss &logpath',
                              'v.write #1 "RCMS_Name = " %STanDard %string htc_smem_ram.RCMS_Name',
                              'v.write #1 "qxdm_dbg_msg = " %STanDard %string qxdm_dbg_msg',
                              'GOSUB POSTMORTEM_ANALYSIS']
    replace_out_loadsim_SSR = ['', '&DDRCS0_FILENAME="' + BIN_file_location + '"',
                               '', '&SMEM_log="'+BIN_2_smem(BIN_file_location)+'"',
                               'do std_loadsyms_mpss_poser_out &logpath',
                               'v.write #1 "qc_image_version_string = " %STanDard %string coredump.image.qc_image_version_string',
                               'v.write #1 "aux_msg = " %STanDard %string coredump.err.aux_msg',
                               'do recovery_f3_htc_out']

    replace_in_loadsyms = ['DIALOG.FILE "&filepath/*&RootElfSuffix"', 'ENTRY &rvalue_elffile',
                           'DIALOG.FILE "*&RootElfSuffix"']
    replace_out_loadsyms = ['', '&rvalue_elffile="' + ELF_file_location + '"', '']

    replace_in_recover_f3 = ['cd.do ../../../../../modem_proc/core/services/diag/f3_trace/cmm/recover_f3.cmm  &nowpath']
    replace_out_recover_f3 = [
        'cd.do ../../../../../../modem_proc/core/services/diag/f3_trace/cmm/recover_f3.cmm  ' + os.path.dirname(
            BIN_file_location) + ' ' + ELF_2_msghash(ELF_file_location)]

    # Update cmm files
    update_cmm(read_loadsyms_cmm_all, write_loadsyms_cmm_all, replace_in_loadsyms, replace_out_loadsyms)
    update_cmm(read_recover_f3_cmm_all, write_recover_f3_cmm_all, replace_in_recover_f3, replace_out_recover_f3)

    if fnmatch.fnmatch(os.path.basename(BIN_file_location), 'ramdump_modem_' + '*'):
        print('SSR dump')
        update_cmm(read_loadsim_SSR_cmm_all, write_loadsim_SSR_cmm_all, replace_in_loadsim_SSR, replace_out_loadsim_SSR)
        return write_loadsim_SSR_cmm_all
    elif fnmatch.fnmatch(os.path.basename(BIN_file_location), 'DDRCS0' + '*'):
        print('Fulldump')
        update_cmm(read_loadsim_cmm_all, write_loadsim_cmm_all, replace_in_loadsim, replace_out_loadsim)
        return write_loadsim_cmm_all
