from distutils.core import setup
import py2exe
AppVers = "8998.0.0.1"
AppName = "8998 Auto Ramdump"

setup(
    options={'py2exe': {
        'bundle_files': 1,
        'compressed': True,
    }},
    console=[{'script': 'ramdumptest-html-parser.py','name' : "Auto Ramdump", 'version' : AppVers, 'name': AppName, 'copyright': "POser Lin"}],
    data_files = [("",['config.txt'])],
    zipfile=None
)