import os
import fnmatch
from Search_module import search_msg_hash
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
cmm_path = r'\common\Core\tools\cmm\common\msm8998\\'

read_load_ramdump_cmm = r'\common\Core\tools\cmm\htc_load_ramdump.cmm'
writ_load_ramdump_cmm = r'\common\Core\tools\cmm\htc_poser_out_load_ramdump.cmm'

read_loadsim_SSR_cmm = 'std_loadsim.cmm'
writ_loadsim_SSR_cmm = 'std_loadsim_poser_out.cmm'

read_htc_tool_menu_cmm = r'\common\Core\tools\cmm\htc\htc_tool_menu.cmm'
writ_htc_tool_menu_cmm = r'\common\Core\tools\cmm\htc\htc_tool_menu_poser_out.cmm'

read_load_ramdump_cmm_all = Codebase_root_folder + read_load_ramdump_cmm
writ_load_ramdump_cmm_all = Codebase_root_folder + writ_load_ramdump_cmm

read_loadsim_SSR_cmm_all = Codebase_root_folder + cmm_path + read_loadsim_SSR_cmm
writ_loadsim_SSR_cmm_all = Codebase_root_folder + cmm_path + writ_loadsim_SSR_cmm


read_htc_tool_menu_cmm_all = Codebase_root_folder + read_htc_tool_menu_cmm
writ_htc_tool_menu_cmm_all = Codebase_root_folder + writ_htc_tool_menu_cmm

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
    replace_in_load_ramdump = ['DIALOG.FILE *\n', 'ENTRY &ramdump_file',
                               'DIALOG.FILE *.elf\n', 'ENTRY &elf',
                               'do std_loadsim',
                               r'IF (OS.FILE(./htc/htc_tool_menu.cmm))']
    replace_ou_load_ramdump = ['', '&ramdump_file="' + BIN_file_location + '"',
                                '', '&elf="' + ELF_file_location + '"',
                                'do std_loadsim_poser_out',
                               'v.v coredump %STanDard %string coredump.err.message %Hex coredump.err.param %STanDard %string coredump.err.filename %STanDard %Decimal coredump.err.linenum %STanDard %string htc_radio_version %STanDard %string htc_radio_build_date' + '\n'+
                               'IF (!OS.FILE(&logpath/coredump.txt))'+'\n(\n'+
                               '  open #1 &logpath/coredump.txt /create\n'+
                               '  v.write #1 "coredump.err.message := " %STanDard %string coredump.err.message\n'+
                               '  v.write #1 "coredump.err.param := " %Hex coredump.err.param\n'+
                               '  v.write #1 "coredump.err.filename := " %STanDard %string coredump.err.filename\n'+
                               '  v.write #1 "coredump.err.linenum := " %STanDard %Decimal coredump.err.linenum\n'+
                               '  v.write #1 "aux_msg := " %STanDard %string coredump.err.aux_msg\n'+
                               '  v.write #1 "htc_radio_version := " %STanDard %string htc_radio_version\n'+
                               '  v.write #1 "htc_radio_build_date := " %STanDard %string htc_radio_build_date\n'+
                               '  v.write #1 "qc_image_version_string := " %STanDard %string coredump.image.qc_image_version_string\n'+
                               '  close #1\n)\n'+





                               'IF (OS.FILE(./htc/htc_tool_menu_poser_out.cmm))']

    replace_in_loadsim_SSR = ['RETURN &load_wlan_menu_option &extraoption']
    replace_ou_loadsim_SSR = ['']

    replace_in_htc_tool_menu = ['recover_f3.cmm',
                                '  DIALOG.DISABLE ChkF3Btn' ]
    replace_ou_htc_tool_menu = ['recover_f3.cmm',
                                '(\n'+
                                4*' '+'IF OS.DIR(&f3log_path)==FALSE()\n'+
                                8*' '+'MKDIR &f3log_path\n'+
                                4*' '+r'CD.DO &base_path\modem_proc\core\services\diag\f3_trace\cmm\recover_f3.cmm &f3log_path '+search_msg_hash(os.path.dirname(ELF_file_location))+'\n'+
                                4*' '+'WAIT 0.3s\n'+
                                4*' '+'DIALOG.EXECUTE ChkF3Btn\n'+
                                '  )\n']


    # Update cmm files
    update_cmm(read_load_ramdump_cmm_all, writ_load_ramdump_cmm_all, replace_in_load_ramdump, replace_ou_load_ramdump)
    update_cmm(read_htc_tool_menu_cmm_all, writ_htc_tool_menu_cmm_all, replace_in_htc_tool_menu, replace_ou_htc_tool_menu)



    if fnmatch.fnmatch(os.path.basename(BIN_file_location), 'ramdump_modem_' + '*'):
        print('SSR dump')
        update_cmm(read_loadsim_SSR_cmm_all, writ_loadsim_SSR_cmm_all, replace_in_loadsim_SSR, replace_ou_loadsim_SSR)
        return writ_load_ramdump_cmm_all
    # elif fnmatch.fnmatch(os.path.basename(BIN_file_location), 'DDRCS0' + '*'):
    #     print('Fulldump')
    #     update_cmm(read_loadsim_cmm_all, write_loadsim_cmm_all, replace_in_loadsim, replace_out_loadsim)
    #     return write_loadsim_cmm_allread_loadsim_SSR_cmm_all
