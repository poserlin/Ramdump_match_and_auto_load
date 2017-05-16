Codebase_root_folder = ''
radio_release_root = ''
T32_full_path = ''
local_temp_dump_folder = r'D:\8998\dump' # default set to 8998 folder
Temp_Elf_folder = ''

def read_from_file(Radio_version):
    global Codebase_root_folder
    global radio_release_root
    global T32_full_path
    global local_temp_dump_folder
    global Temp_Elf_folder

    codebase_ver = Radio_version.split('-')[0][-4:]

    with open('config.txt', 'r') as config_file:

        for line in config_file:
            if codebase_ver+'_Codebase_root_folder' in line:
                Codebase_root_folder = line.rstrip().split('= ')[1]
            elif 'radio_release_root' in line:
                radio_release_root = line.rstrip().split('= ')[1]
            elif 'T32_full_path' in line:
                T32_full_path = line.rstrip().split('= ')[1]
            elif codebase_ver+'_local_temp_dump_folder' in line:
                local_temp_dump_folder = line.rstrip().split('= ')[1]
                import os
                Temp_Elf_folder = os.path.join(local_temp_dump_folder, 'ELF_temp')
