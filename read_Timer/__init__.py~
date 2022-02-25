from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time
import struct
import re
import pkg_resources
import os

from loguru import logger

data_lengths = {"int": 4, "float": 4, "double": 8, "uint32_t": 32}


def stripcomments(text):
    """
    https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
    """
    return re.sub("//.*?\n|/\*.*?\*/", "", text, flags=re.S)


class TimerHeader:
    """Read a PSRCHIVE Timer header
    the header is a struct defined in "data/timer.h"
    which is a copy of "psrchive/Base/Formats/Timer/timer.h"

    This reads all of the header keywords it can and puts them into self.keywords
    It also extracts a few of particular importance:
    telescope
    mjd
    duration
    position
    """

    keywords = None

    def __init__(self, filename):
        if TimerHeader.keywords is None:
            TimerHeader.keywords = self.__class__.get_definition()
        keywords = TimerHeader.keywords

        f = open(filename, "rb")
        for varname in keywords:
            out = f.read(keywords[varname][1])
            if keywords[varname][0] == "char":
                try:
                    result = out.decode().rstrip("\x00")
                except UnicodeDecodeError:
                    # ???
                    pass
            elif keywords[varname][0] == "int":
                result = struct.unpack(">i", out)[0]
            elif keywords[varname][0] == "float":
                result = struct.unpack(">f", out)[0]
            elif keywords[varname][0] == "double":
                result = struct.unpack(">d", out)[0]
            keywords[varname].append(result)
        self.keywords = keywords

        self.mjd = Time(
            self.keywords["mjd"][-1] + self.keywords["fracmjd"][-1], format="mjd"
        )
        if self.keywords["coord_type"][-1] == "05":
            self.position = SkyCoord(
                self.keywords["ra"][-1] * u.rad, self.keywords["dec"][-1] * u.rad
            )
        elif self.keywords["coord_type"][-1] == "04":
            self.position = SkyCoord(
                self.keywords["l"][-1] * u.deg,
                self.keywords["b"][-1] * u.deg,
                frame="galactic",
            )
        else:
            self.position = None

        self.telescope = self.keywords["telid"][-1]
        self.duration = (
            self.keywords["nsub_int"][-1] * self.keywords["sub_int_time"][-1] * u.s
        )
        self.telescope = self.keywords["telid"][-1]
        self.psrname = self.keywords["psrname"][-1]
        logger.debug(f"Telescope = {self.telescope}")
        logger.debug(f"Pulsar = {self.psrname}")
        logger.debug(f"Start = {self.mjd.mjd} = {self.mjd.iso}")
        logger.debug(f"Duration = {self.duration}")

    @staticmethod
    def get_definition():
        """get Timer file header definition
        
        Returns
        -------
        keywords : dict
        dictionary of keywords with each entry being [`type`, `size`]
        """

        fh = open(
            os.path.join(pkg_resources.resource_filename(__name__, "data/"), "timer.h"),
            "r",
        )

        lines = stripcomments("".join(fh.readlines())).split("\n")

        keywords = {}

        # first extract the lengths of the different char[] variables
        chararray_lengths = {}
        for line in lines:
            if line.startswith("#define"):
                if len(line.split()) == 3:
                    try:
                        chararray_lengths[line.split()[1]] = int(line.split()[2])
                    except ValueError:
                        # not a char array
                        pass
        # now parse the rest
        for line in lines:
            if line.startswith("//") or line.startswith("#"):
                continue
            if len(line.strip()) == 0:
                continue
            try:
                vartype, varname = line.split(";")[0].split()
            except:
                # assume still a comment?
                continue
            if vartype == "char":
                length = chararray_lengths[varname.split("[")[1].replace("]", "")]
                varname = varname.split("[")[0]
            else:
                length = data_lengths[vartype]
            keywords[varname] = [vartype, length]
        return keywords
