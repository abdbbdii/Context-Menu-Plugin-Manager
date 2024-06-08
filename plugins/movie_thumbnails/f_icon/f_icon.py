"""Set folder icon based on the input file"""
import os
import platform
import argparse
from os import path

if platform.system() == "Windows":
    from windows_icon import IconCreator
elif platform.system() == "Darwin":
    from mac_icon import IconCreator
else:
    print("Linux is not supported at this time :(")


def create_icon(input_file, folder="", placement="", relative=False, debug=False):
    """
    Checks all parameters and generates folder icons.
    :param str input_file: Input image or text file. Image file location is used as folder location
    if not set other vice.
    :param str folder: Folder location.
    :param str placement: Placement location of the ico file
    :param bool relative: Path to the placement folder is relative.
    If Placement folder is on another drive, relative is ignored.
    :param bool debug: display debug in formation
    :return:
    """

    # current_platform = platform.system()

    if path.exists(input_file) and path.isfile(input_file):
        accepted_files = [".jpg", ".jpeg", ".png", ".txt"]
        if path.splitext(input_file.lower())[1] in accepted_files:
            if folder == "" or path.isdir(folder):
                if placement == "" or path.isdir(placement):
                    if (
                        relative
                        and folder != ""
                        and placement != ""
                        and os.path.splitdrive(folder.lower())[0]
                        != os.path.splitdrive(placement.lower())[0]
                    ):
                        relative = False
                    icon_creator = IconCreator(debug)
                    icon_creator.create_icon(input_file, folder, placement, relative)

                else:
                    print(folder + " Is not a valid folder.")
            else:
                print(folder + " Is not a valid folder.")
        else:
            print(
                "Only accepted file formats are: "
                + ", ".join([str(item) for item in accepted_files])
            )
    else:
        print("Input file need to exist !!!")


def main():
    """Checks input parameters and directs appropriate icon creator to creates icons"""

    current_platform = platform.system()
    parser = argparse.ArgumentParser(
        prog="F-Icon", description="Set target folder icon to the provided image file."
    )
    parser.add_argument(
        "input",
        help="Path to an image (jpg, jpeg or png) or text (txt) file with the list of the images.",
    )
    parser.add_argument(
        "-f",
        "--folder",
        help="Path to the folder that will have its icon changed. "
        "It is ignored if the input is a text file.",
        default="",
    )
    if current_platform == "Windows":
        parser.add_argument(
            "-p",
            "--placement",
            help="Path to the folder where to keep generated icons. "
            "By default, they are stored inside the folder with a changed icon.",
            default="",
        )
        parser.add_argument(
            "-r",
            "--relative",
            action="store_true",
            help="If the icon is located in another folder, it forces the path to be relative, "
            "and it gets ignored if the drive for both locations is different.",
        )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display any debug information",
    )

    args = parser.parse_args()
    if platform.system() == "Windows":
        create_icon(args.input, args.folder, args.placement, args.relative, args.verbose)
    elif platform.system() == "Darwin":
        create_icon(args.input, args.folder, '', False, args.verbose)
    else:
        print("Linux is not supported at this time :(")



if __name__ == "__main__":
    main()
