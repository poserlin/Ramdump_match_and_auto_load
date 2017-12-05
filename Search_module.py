# Define the Search elf based on provide radio version
import fnmatch
import os
import re
import shutil
import zipfile
import read_config

# ==========================================================
# Class declaration
# =========================================================
class Elf_search:
    def __init__(self, radio_version):
        self.radio_version = radio_version
        self.elf_loc = 0

    def locally(self):
        self.elf_loc = search_elf_local(self.radio_version)
        return self.elf_loc

    def remotely(self):
        self.elf_loc = search_elf_remote(self.radio_version)
        return self.elf_loc


# ==========================================================
# Function declaration
# ==========================================================

# Define the Search smem for SSR Ramdump based on provide bin
def BIN_2_smem(BIN_file_location):
    for file in filter(lambda file: fnmatch.fnmatch(file, 'ramdump_smem_*'), os.listdir(os.path.dirname(BIN_file_location))):
        return os.path.join(os.path.dirname(BIN_file_location), file)
    return ''

def search_msg_hash(dirPath):
    for msg_hash in filter(lambda msg_hash: fnmatch.fnmatch(msg_hash, 'qdsp6m.qdb'), os.listdir(dirPath)):
        return os.path.join(dirPath, msg_hash)


# Define the Search elf based on provide radio version
def search_elf(search_dir, radio_version):
    for dirPath, dirNames, fileNames in os.walk(search_dir):
        for x in filter(lambda x: fnmatch.fnmatch(x, '*' + radio_version + '*.img'), fileNames):
            full_radio_version = x.split('_')[2]
            print(full_radio_version)
            for elf in filter(lambda elf: fnmatch.fnmatch(elf, 'orig_MODEM_PROC_IMG*.elf'), os.listdir(dirPath)):
                elf_file = os.path.join(dirPath, elf)
            for msg_hash in filter(lambda msg_hash: fnmatch.fnmatch(msg_hash, 'msg_hash_*.qsr4'), os.listdir(dirPath)):
                msg_hash_file = os.path.join(dirPath, msg_hash)
                print('>> Match ELF in \r\n %s' % elf_file)
                return elf_file, radio_version, msg_hash_file


def search_elf_g_radio(search_dir, radio_version):
    for dir_1 in os.listdir(search_dir):
        if radio_version in dir_1:
            dir_2 = os.path.join(read_config.radio_release_root, dir_1)
            for dirPath, dirNames, fileNames in os.walk(dir_2):
                for elf in filter(lambda elf: fnmatch.fnmatch(elf, 'orig_MODEM_PROC_IMG_8998.gen.prodQ.elf'),fileNames):
                    elf_file = os.path.join(dirPath, elf)
                for msg_hash in filter(lambda msg_hash: fnmatch.fnmatch(msg_hash, 'qdsp6m.qdb'), fileNames):
                    msg_hash_file = os.path.join(dirPath, msg_hash)
                    print('>> Match ELF in \r\n %s' % elf_file)
                    return elf_file, radio_version, msg_hash_file

# Define the Remote Search, assume different build have diff build
def search_elf_remote(radio_version):
    print('>>>> Searching Remotely......', end='')
    # Search remote dir by release ver
    radio_version_list = radio_version.split('-')

    # If Google radio, using search_elf_g_radio
    if radio_version_list[0] == 'g8998':
        elf_file_remote_location, full_radio_version, msg_hash_file = search_elf_g_radio(read_config.radio_release_root, radio_version)
    #Elif htc radio, search SSD folder:
    elif radio_version_list[0] == 'sdm845' or radio_version_list[0] == '8998':
        if len(radio_version_list) == 3:  # full radio version, parser & speed up search by release version
            for dir_1 in os.listdir(read_config.radio_release_root):
                if re.search(radio_version_list[1], dir_1):
                    new_path = os.path.join(read_config.radio_release_root, dir_1)
                    for dir_2 in os.listdir(new_path):
                        if re.search(radio_version_list[2], dir_2):
                            new_path = os.path.join(new_path, dir_2)
                            elf_file_remote_location, full_radio_version, msg_hash_file = search_elf(new_path, radio_version)



    # if Fail, Search all dir from root, support partial Radio ver search
    if elf_file_remote_location == 0:
        # print('Full search from root dir due to partial Radio_ver')
        elf_file_remote_location, full_radio_version, msg_hash_file = search_elf(read_config.radio_release_root, radio_version)

    # if Found, copy ELF from remote server to local_temp_elf_folder
    if elf_file_remote_location != 0:

        elf_file_rename = os.path.splitext(os.path.basename(elf_file_remote_location))[0] + '_' + radio_version_list[
            2] + \
                          os.path.splitext(os.path.basename(elf_file_remote_location))[1]
        local_elf_file_location = os.path.join(os.path.join(read_config.Temp_Elf_folder, full_radio_version), elf_file_rename)
        local_msg_hash_file_location = os.path.join(os.path.join(read_config.Temp_Elf_folder, full_radio_version), os.path.basename(msg_hash_file))

        if not os.path.isdir(os.path.dirname(local_elf_file_location)):
            os.makedirs(os.path.dirname(local_elf_file_location))
        else:
            pass


        print('>>>> Found, Copy file from SSD server...... to %s'%local_elf_file_location)
        # shutil.copy(elf_file_remote_location, local_elf_file_location)
        with open(elf_file_remote_location, 'rb') as fin:
            with open(local_elf_file_location, 'wb') as fout:
                shutil.copyfileobj(fin, fout, 16*1024*1024)
        shutil.copy(msg_hash_file, local_msg_hash_file_location)

        # checking the file size, if match, add _fin in the file name.
        if os.path.getsize(local_elf_file_location) != os.path.getsize(elf_file_remote_location):
            return 0
        else:
            print('>>>> Finish copying......')
            add_fin = lambda input_address: os.path.splitext(input_address)[0] + '_fin' + \
                                            os.path.splitext(input_address)[1]

            local_elf_file_location_fin = add_fin(local_elf_file_location)
            os.rename(local_elf_file_location, local_elf_file_location_fin)
            # print('local_elf_file_location', local_elf_file_location_fin)
            return local_elf_file_location_fin


# Define the local Search
def search_elf_local(radio_version):
    # Full radio version
    radio_version_list = radio_version.split('-')
    if len(radio_version_list) == 3:
        radio_version_part = radio_version_list[2]
    else:
        radio_version_part = radio_version_list[0]

    for dirPath, dirNames, fileNames in os.walk(read_config.Temp_Elf_folder):
        for x in fileNames:
            if fnmatch.fnmatch(x, '*' + radio_version_part + '_fin.elf'):
                elf_file = os.path.join(dirPath, x)
                print('>> Match ELF locally in %s' % dirPath)
                return elf_file
    print('>> ELF Not found locally')
    return 0


# Define the Zip BIN file search
def search_bin(bin_file_location):
    match_list = ['*ramdump_modem_*', '*DDRCS0.BIN']
    match_list_sub = ['*ramdump_smem_*', '*OCIMEM.BIN']

    for match_file in match_list:
        # Input file is full or online ramdump directly
        if fnmatch.fnmatch(os.path.basename(bin_file_location), match_file):
            return bin_file_location
        # Input file is zip file
        elif zipfile.is_zipfile(bin_file_location):
            # zip file found, try tp extract dump from it
            with zipfile.ZipFile(bin_file_location, 'r') as zip_read:

                temp_dump_folder = os.path.join(read_config.local_temp_dump_folder,
                                                os.path.splitext(os.path.basename(bin_file_location))[0])

                # for Matching file in zip_read.namelist():
                for match_file in match_list_sub + match_list:
                    for file in filter(lambda file: fnmatch.fnmatch(file, match_file), zip_read.namelist()):

                        print('>> BIN found in ZIP, unzipping to {temp_dump_location} ....'.format(
                            temp_dump_location=temp_dump_folder))
                        if os.path.isdir(temp_dump_folder):
                            if os.path.isfile(os.path.join(temp_dump_folder,
                                                           os.path.basename(file))) and match_file in match_list:
                                continous_go = input('>> Already unzip on ' + temp_dump_folder + '\n' + '>> Need to process Y/N?' + '\n')
                                if continous_go.lower() == 'y':
                                    return os.path.join(temp_dump_folder, os.path.basename(file))
                                else:
                                    quit()
                        else:
                            os.makedirs(temp_dump_folder)

                        source = zip_read.open(file)
                        target = open(os.path.join(temp_dump_folder, os.path.basename(file)), 'wb')
                        with source, target:
                            shutil.copyfileobj(source, target)
                            if match_file in match_list:
                                return os.path.join(temp_dump_folder, os.path.basename(file))


                print('>> NO Match file found in zip file')
                return 0

        #Input file not Zip nor dump file
        else:
            print('>> Input not Zip nor dumpfile')
            return 0

def search_radio_version(BIN_file_location):
    found = 0
    # input Bin file are not valid
    if BIN_file_location == 0:
        return 0

    with open(BIN_file_location, 'rb') as dump_file:
        # Search SSR dump radio version for special mem address
        if fnmatch.fnmatch(os.path.basename(BIN_file_location), 'ramdump_modem_*'):
            # for SSR dump, move index to (0x0247395c) to get the radio version
            for possible_location in [0x0619055F, 0x02DFB096, 0x02D8B69D]:
                dump_file.seek(possible_location)
                try:
                    Radio_version = dump_file.read(22).decode('ascii')
                    if isinstance(Radio_version, str) and Radio_version.isprintable():
                        print('>> Radio found within Bin:', Radio_version)
                        return Radio_version
                except:
                    pass
        # Search Full Dump
        else:
            for possible_location in [0x06010928]:
                dump_file.seek(possible_location)
                try:
                    Radio_version = dump_file.read(20).decode('ascii')
                    if isinstance(Radio_version, str) and Radio_version.isprintable():
                        print('>> Radio found within Bin:', Radio_version)
                        return Radio_version
                except:
                    pass
        return 0

def search_rtel(BIN_file_location, ELF_dir):
    Bin_dir = os.path.dirname(BIN_file_location)

    for fileNames in os.listdir(ELF_dir):
        if '.qdb' in fileNames:
            shutil.copy(os.path.join(ELF_dir,fileNames), os.path.join(Bin_dir, fileNames))

    os.chdir(Bin_dir)
    for fileNames in os.listdir(Bin_dir):
        if 'rtel' in fileNames:
            os.rename(fileNames, fileNames + '.qmdl')
            os.chdir(r'C:\Program Files (x86)\Qualcomm\QCAT 6.x\Bin')
            # print('QCAT.exe' + ' -isf ' + os.path.join(os.path.dirname(BIN_file_location), fileNames + '.qmdl'))
            os.system('QCAT.exe' + ' -isf ' + os.path.join(Bin_dir, fileNames + '.qmdl'))
            return os.path.join(Bin_dir, fileNames + '.isf')
            break