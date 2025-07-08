###############################################################################
# VTT to SRT converter
# -----------------------------------------------------------------------------
# Author: Miksu2001
# License:
# -----------------------------------------------------------------------------
# This script finds all VTT files in a given directory, converts them into SRT
# files, and saves the converted files into the output directory of choice.
# The VTT files will not be deleted automatically.
#
###############################################################################

import re
import os

SUBTITLE_TIMESTAMP_PATTERN = r"([0-9]|:|\.)* --> ([0-9]|:|\.)*"
"""Defines the regex pattern for timestamp lines in VTT files."""

FILE_SEARCH_PATTER = r".*\.vtt"
"""Defines the file name pattern used to find VTT files."""


class TIMESTAMP:
    """Holds information about a single timestamp.

    Attributes
    ----------
    hour : int
        Hours [0, inf)
    minute : int
        Minutes [0, 59]
    second : int
        Seconds [0, 59]
    milliseconds : int
        Milliseconds [0, 999]

    Methods
    -------
    __init__(self) : TIMESTAMP
    __init__(self, str) : TIMESTAMP
    __str__(self) : str

    """

    _INDEX_MILLISECOND = 0
    _INDEX_SECOND = 1
    _INDEX_MINUTE = 2
    _INDEX_HOUR = 3

    hour:int = 0
    minute:int = 0
    second:int = 0
    millisecond:int = 0


    def __init__(self):
        """Creates new TIMESTAMP object with all values set to 0."""

        self.hour = 0
        self.minute = 0
        self.second = 0
        self.millisecond = 0


    def __init__(self, timestring:str):
        """Create a new TIMESTAMP object from timestring.

        Parameters
        ----------
        timestring : str
            Time in the VTT string format. For example: 01:02:34.567 --> 1h, 2m,
            34s, 567ms or 2:01.123 --> 2m, 1s, 123ms.

        """

        timestring = timestring.replace(".", ":")
        time_parts = list(reversed(timestring.split(":")))

        if (len(time_parts) > TIMESTAMP._INDEX_MILLISECOND):
            self.millisecond = int(time_parts[TIMESTAMP._INDEX_MILLISECOND])

        if (len(time_parts) > TIMESTAMP._INDEX_SECOND):
            self.second = int(time_parts[TIMESTAMP._INDEX_SECOND])

        if (len(time_parts) > TIMESTAMP._INDEX_MINUTE):
            self.minute = int(time_parts[TIMESTAMP._INDEX_MINUTE])

        if (len(time_parts) > TIMESTAMP._INDEX_HOUR):
            self.hour = int(time_parts[TIMESTAMP._INDEX_HOUR])

    
    def __str__(self) -> str:
        """Returns the timestamp in the format HH:MM:SS,sss, whe s is milliseconds"""
        return f"{self.hour:02}:{self.minute:02}:{self.second:02},{self.millisecond:03}"


class SUBTITLE_LINE:
    """A class containing information about one subtitle line.

    Attributes
    ----------
    number : int
        Running number of the subtitle line.
    timestamp : str
        Start and end time of the subtitle line.
    text : str
        Text displayed to the viewer.

    """

    number:int = 0
    timestamp:str = ""
    time_start:TIMESTAMP = ""
    time_end:TIMESTAMP = ""
    text:str = ""

    def __str__(self):
        return f"{self.number}\n{self.time_start} --> {self.time_end}\n{self.text}"

    def set_timestamp(self, timestampline:str):
        timestamps = timestampline.split(" --> ")
        self.time_start = TIMESTAMP(timestamps[0])
        self.time_end = TIMESTAMP(timestamps[1])


def read_file(filepath:str) -> list[SUBTITLE_LINE]:
    """Reads the subtitle data from the given file.

    Paramerets
    ----------
    filepath : str
        Path to the file to read.

    Returns
    -------
        A list of SUBTITLE_LINE objects containing the subtitle info within the file.

    """

    print(f"Reading file '{filepath}'")
    try:
        subtitle_lines:list[SUBTITLE_LINE] = []
        with open(filepath, "r", encoding="utf-8") as file:
            file.readline() # Skip vtt header.
            file.readline() # Skip vtt header.
            line_number:int = 0
            subtitle_line:SUBTITLE_LINE = None
            for line in file:
                line = line[:-1]
                if (re.match(SUBTITLE_TIMESTAMP_PATTERN, line)):
                    line_number += 1
                    subtitle_line = SUBTITLE_LINE()
                    subtitle_line.set_timestamp(line)
                elif (line != ""):
                    subtitle_line.text += line + "\n"
                else:
                    subtitle_lines.append(subtitle_line)
            print(f"Found {line_number} subtitle lines in file '{filepath}'")
            return subtitle_lines
    except Exception as e:
        print(f"Cannot read file: {e}")
        return None


def write_file(filepath:str, subtitle_lines:list[SUBTITLE_LINE]) -> None:
    """Writes subtitle to a file in the SRT format.

    Parameters
    ----------
    filepath : str
        Path to the file to be written.
    subtitle_lines : list[SUBTITLE_LINE]
        A list containing the subtitle lines as SUBTITLE_LINE objects.

    """

    print(f"Writing file '{filepath}'.")
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            for subtitle_line in subtitle_lines:
                file.write(f"{subtitle_line}\n")
    except Exception as e:
        print(f"Cannot write file: {e}")


def get_vtt_files(directory_path:str) -> list[str]:
    """Finds all VTT files in the given directory.

    Parameters
    ----------
    directory_path : str
        Where to look for the VTT files.

    Returns
    -------
        A string list of file names including extensions.

    """

    directory_contents:list[str] = os.listdir(directory_path)
    vtt_files:list[str] = []
    for item in directory_contents:
        if (re.match(FILE_SEARCH_PATTER, item)):
            vtt_files.append(item)
    return vtt_files


def convert_files(vtt_files:list[str], input_directory_path:str, output_directory_path:str) -> None:
    """Converts VTT files to SRT files.

    Parameters
    ----------
    vtt_files : list[str]
        List containing the file names for the VTT files that should be converted.
    input_directory_path : str
        The directory that contains the VTT files.
    output_directory_path : str
        The directory where to save the converted SRT files.

    """

    for vtt_file in vtt_files:
        input_path = f"{input_directory_path}\\{vtt_file}"
        output_path = f"{output_directory_path}\\{vtt_file.replace("vtt", "srt")}"
        write_file(output_path, subtitle_lines=read_file(input_path))
        print()


def main():
    input_directory_path = input("Enter input directory (vtt): ")
    output_directory_path = input("Enter output directory (srt): ")
    print()
    convert_files(get_vtt_files(input_directory_path), input_directory_path, output_directory_path)
    print("Thank you for using the program.")


main()
