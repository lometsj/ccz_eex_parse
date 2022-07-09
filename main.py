
import os
import sys

config = "ccz_origin.xml"

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: ./export_config.py [ccz_path]")
    ccz_path = sys.argv[1]
    if os.access(ccz_path, os.F_OK) == False:
        print("path invalid")
        exit(0)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
