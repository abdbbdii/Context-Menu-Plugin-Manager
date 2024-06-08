"""Create folder icon for Mac"""
import os
import sys
from pathlib import Path
import cv2  # opencv-python
import Cocoa
import numpy as np


class IconCreator:
    """
    Create icon for windows folder
    """

    def __init__(self, debug=False):
        """
        Initialization
        :param bool debug: Debug status
        """
        self.debug = debug

    def create_icon(self, input_file, folder="", placement="", relative=False):
        """
        Generates icons for MacOS
        :param str input_file: Input image or text file.
        Image file location is used as folder location if not set other vice.
        :param str folder: Folder location.
        :param str placement: Ignored on mac
        :param bool relative: Ignored on mac
        :return:
        """
        if os.path.splitext(input_file.lower())[1] == ".txt":
            with open(input_file, "r", encoding="UTF-8") as file:
                while line := file.readline().rstrip():
                    # print('*'+line+'*')
                    # print(os.stat(line))
                    # print(os.path.exists(line))
                    if os.path.exists(line):
                        self._create_mac_icons(line, str(Path(line).parent))
        else:
            if folder == "":
                folder = str(Path(input_file).parent)
            self._create_mac_icons(input_file, folder)

        if self.debug:
            print("creating mac icon")

    def _create_mac_icons(self, image, folder):
        """
        Creating actual icon
        :param str image: Path of the image
        :param str folder: Path of the folder
        :return:
        """
        # Reading an image (you can use PNG or JPG)
        # img = cv2.imread(image, cv2.IMREAD_UNCHANGED)
        img = cv2.imdecode(np.fromfile(image, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

        # Getting the bigger side of the image
        s = max(img.shape[0:2])

        if img.shape[2] != 4:  # add transparency layer, if we do not have one
            # editing input image to have alpha channel
            alpha = np.full((img.shape[0], img.shape[1]), 255, dtype=np.uint8)
            img = np.dstack((img, alpha))

        # Creating a dark square with NUMPY
        f = np.zeros((s, s, 4), np.uint8)

        # Getting the centering position
        ax, ay = (s - img.shape[1]) // 2, (s - img.shape[0]) // 2

        # Pasting the 'image' in a centering position
        f[ay : img.shape[0] + ay, ax : ax + img.shape[1]] = img

        # Showing results (just in case)
        # cv2.imshow("IMG", f)
        # A pause, waiting for any press in keyboard
        # cv2.waitKey(0)

        # Saving the image
        temp_file = folder + os.sep + "_temp_.png"
        # cv2.imwrite(temp_file, f)
        is_success, im_buf_arr = cv2.imencode(".png", f)
        im_buf_arr.tofile(temp_file)

        # cv2.destroyAllWindows()

        Cocoa.NSWorkspace.sharedWorkspace().setIcon_forFile_options_(
            Cocoa.NSImage.alloc().initWithContentsOfFile_(temp_file), folder, 0
        ) or sys.exit("Unable to set file icon")
        os.remove(temp_file)
        if self.debug:
            print("Icon Created for " + folder)
