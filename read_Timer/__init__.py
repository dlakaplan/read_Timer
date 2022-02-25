import struct
import re
import pkg_resources
import os
import copy

from loguru import logger

from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.time import Time

_data_lengths = {"int": 4, "float": 4, "double": 8, "uint32_t": 4}


def stripcomments(text):
    """
    https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
    """
    return re.sub("//.*?\n|/\*.*?\*/", "", text, flags=re.S)


def get_definition(filename="timer.h"):
    """get Timer file header definition
    
    Returns
    -------
    keywords : dict
    dictionary of `Keyword`s
    """
    _header_file = os.path.join(
        pkg_resources.resource_filename(__name__, "data/"), filename
    )

    fh = open(_header_file, "r",)

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
        if not ";" in line:
            continue
        goodline = line.split(";")[0]
        if len(goodline.split()) == 2:
            try:
                vartype, varname = goodline.split()
            except:
                # assume still a comment?
                continue
        elif (
            (len(goodline.split()) == 3)
            and (goodline.split()[0] == "struct")
            and not ("{" in goodline)
        ):
            vartype, varname = goodline.split()[1:]
        else:
            continue
        if vartype == "char":
            length = chararray_lengths[varname.split("[")[1].replace("]", "")]
            varname = varname.split("[")[0]
        keywords[varname] = Keyword(name=varname, dtype=vartype)
        if vartype == "char":
            keywords[varname].size = length
    return keywords


class Keyword:
    def __init__(self, name=None, size=0, dtype=None, value=None):
        self.name = name
        self.size = size
        self.dtype = dtype
        self.value = value

    @property
    def dtype(self):
        return self._dtype

    @dtype.setter
    def dtype(self, value):
        self._dtype = value
        if self._dtype in _data_lengths:
            self.size = _data_lengths[self._dtype]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{self.name}[{self.dtype}, {self.size} bytes] = {self.value}"


class Band:
    def __init__(self, name=None):
        self.keywords = copy.deepcopy(_band_keyword_definition)
        self.name = name
        self.size = 0
        self.sequence = ""
        for key in _band_keyword_definition:
            self.size += _band_keyword_definition[key].size
            self.sequence += _band_keyword_definition[key].dtype[0]

    def asstr(self):
        s = []
        for key in self.keywords:
            s.append(str(self.keywords[key]))
        return s

    def __repr__(self):
        s = f"{self['bw'].value} MHz band at {self['centrefreq'].value} MHz"
        return s

    def __str__(self):
        return repr(self) + ":\n" + ("\n".join(self.asstr()))

    def __getitem__(self, key):
        return self.keywords[key]


class TimerHeader:
    """Read a PSRCHIVE Timer header
    the header is a struct defined in "data/timer.h"
    which is a copy of "psrchive/Base/Formats/Timer/timer.h"

    This reads all of the header keywords it can and puts them into self.keywords
    It also extracts a few of particular importance:
    telescope
    starttime
    stoptime
    duration
    position
    """

    def __init__(self, filename):
        self.keywords = copy.deepcopy(_timer_keyword_definition)

        logger.debug(f"Reading Timer file {filename}")
        self.filename = filename
        f = open(filename, "rb")
        for varname in self.keywords:
            if self.keywords[varname].dtype == "band":
                result = Band(name=varname)
                self.keywords[varname].size = result.size
            out = f.read(self.keywords[varname].size)
            if self.keywords[varname].dtype == "char":
                try:
                    result = out.decode().rstrip("\x00")
                except UnicodeDecodeError:
                    logger.warning(f"Unable to decode contents of '{varname}'")
            elif self.keywords[varname].dtype == "band":
                results = struct.unpack(">" + result.sequence, out)
                for k, r in zip(result.keywords, results):
                    result.keywords[k].value = r
            elif self.keywords[varname].dtype == "int":
                result = struct.unpack(">i", out)[0]
            elif self.keywords[varname].dtype == "float":
                result = struct.unpack(">f", out)[0]
            elif self.keywords[varname].dtype == "double":
                result = struct.unpack(">d", out)[0]
            elif self.keywords[varname].dtype == "uint32_t":
                # unsigned 4-byte integer?
                result = struct.unpack(">I", out)[0]
            self.keywords[varname].value = result

        self.starttime = Time(
            self.keywords["mjd"].value + self.keywords["fracmjd"].value, format="mjd"
        )
        if self.keywords["coord_type"].value == "05":
            self.position = SkyCoord(
                self.keywords["ra"].value * u.rad, self.keywords["dec"].value * u.rad
            )
        elif self.keywords["coord_type"].value == "04":
            self.position = SkyCoord(
                self.keywords["l"].value * u.deg,
                self.keywords["b"].value * u.deg,
                frame="galactic",
            )
        else:
            logger.warning(
                f"Do not know how to interpret coordinate type {self.keywords['coord_type'].value}"
            )
            self.position = None

        self.telescope = self.keywords["telid"].value
        self.duration = (
            self.keywords["nsub_int"].value * self.keywords["sub_int_time"].value * u.s
        )
        self.stoptime = self.starttime + self.duration
        self.psrname = self.keywords["psrname"].value
        logger.debug(f"Telescope = {self.telescope}")
        logger.debug(f"Pulsar = {self.psrname}")
        logger.debug(f"Start = {self.starttime.mjd} = {self.starttime.iso}")
        logger.debug(f"Duration = {self.duration}")

    def asstr(self):
        s = []
        for key in self.keywords:
            s.append(str(self.keywords[key]))
        return s

    def __repr__(self):
        s = f"Timer file {self.filename}: {self.psrname} at MJD {self.starttime.mjd} for {self.duration} with {self.telescope}"
        return s

    def __str__(self):
        return repr(self) + ":\n" + ("\n".join(self.asstr()))

    def __getitem__(self, key):
        return self.keywords[key]


_timer_keyword_definition = get_definition("timer.h")
_band_keyword_definition = get_definition("band.h")
