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
_endian = ">"


def stripcomments(text):
    """Returns text with C/C++ comments removed

    https://stackoverflow.com/questions/241327/remove-c-and-c-comments-using-python
    """
    return re.sub("//.*?\n|/\*.*?\*/", "", text, flags=re.S)


def get_definition(filename):
    """get Timer file header definition

    Parameters
    ----------
    filename : name of .h file defining struct

    Returns
    -------
    keywords : dict
    dictionary of `Keyword`s
    """
    _header_file = os.path.join(
        pkg_resources.resource_filename(__name__, "data/"), filename
    )

    fh = open(
        _header_file,
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
            try:
                length = int(varname.split("[")[1].replace("]", ""))
            except ValueError:
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

    def read(self, fptr):
        out = fptr.read(self.size)
        if self.dtype == "char":
            try:
                result = out.decode().rstrip("\x00")
            except UnicodeDecodeError:
                logger.warning(f"Unable to decode contents of '{self.name}'")
                result = None
        elif self.dtype == "int":
            result = struct.unpack(_endian + "i", out)[0]
        elif self.dtype == "float":
            result = struct.unpack(_endian + "f", out)[0]
        elif self.dtype == "double":
            result = struct.unpack(_endian + "d", out)[0]
        elif self.dtype == "uint32_t":
            # unsigned 4-byte integer?
            result = struct.unpack(_endian + "I", out)[0]
        self.value = result

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

    def read(self, fptr):
        out = fptr.read(self.size)
        results = struct.unpack(">" + self.sequence, out)
        for k, r in zip(self.keywords, results):
            self.keywords[k].value = r
        self.frequency = self["centrefreq"].value * u.MHz
        self.bandwidth = self["bw"].value * u.MHz
        self.npol = self["npol"].value

    def asstr(self):
        s = []
        for key in self.keywords:
            s.append(str(self.keywords[key]))
        return s

    def __repr__(self):
        s = f"{self.bandwidth} Band at {self.frequency}"
        return s

    def __str__(self):
        return repr(self) + ":\n" + ("\n".join(self.asstr()))

    def __getitem__(self, key):
        return self.keywords[key]

    def __setitem__(self, key, value):
        self.keywords[key].value = value


class Subint:
    def __init__(self, number=None):
        self.keywords = copy.deepcopy(_subint_keyword_definition)
        self.number = number

    @property
    def size(self):
        size = 0
        for k in self.keywords:
            size += self.keywords[k].size
        return size

    def read(self, fptr):
        for varname in self.keywords:
            self.keywords[varname].read(fptr)
        self.starttime = Time(
            self.keywords["mjd"].value + self.keywords["fracmjd"].value, format="mjd"
        )
        self.integration = self.keywords["integration"].value * u.s

    def asstr(self):
        s = []
        for key in self.keywords:
            s.append(str(self.keywords[key]))
        return s

    def __repr__(self):
        s = f"Subint {self.number} at {self.starttime} for {self.integration}"
        return s

    def __str__(self):
        return repr(self) + ":\n" + ("\n".join(self.asstr()))

    def __getitem__(self, key):
        return self.keywords[key]

    def __setitem__(self, key, value):
        self.keywords[key].value = value


class TimerHeader:
    """Read a PSRCHIVE Timer header
    the header is a struct defined in "data/timer.h"
    which is a copy of "psrchive/Base/Formats/Timer/timer.h"

    also uses: "data/band.h"
    which is a copy of "psrchive/Base/Formats/Timer/band.h"

    This reads all of the header keywords it can and puts them into self.keywords
    It also extracts a few of particular importance:
    telescope
    starttime
    stoptime
    duration
    position
    psrname
    polyco
    ephem
    """

    def __init__(self, filename=None):
        self.keywords = copy.deepcopy(_timer_keyword_definition)
        self.subints = []
        if filename is not None:
            self.read(filename)

    def read(self, filename):
        logger.debug(f"Reading Timer file {filename}")
        self.filename = filename
        f = open(filename, "rb")
        for varname in self.keywords:
            if self.keywords[varname].dtype == "band":
                result = Band(name=varname)
                result.read(f)
                self.keywords[varname].value = result
                self.keywords[varname].size = result.size
            else:
                self.keywords[varname].read(f)

        # ignore the backend info
        out = f.read(self.keywords["be_data_size"].value)

        if self.keywords["nbytespoly"].value > 0:
            out = f.read(self.keywords["nbytespoly"].value)
            self.polyco = out.decode().rstrip("\x00")

        out = f.read(self.keywords["nbytesephem"].value)
        self.ephem = out.decode().rstrip("\x00")

        # process some of the more useful keywords
        # self.starttime = Time(
        #    self.keywords["mjd"].value + self.keywords["fracmjd"].value, format="mjd"
        # )
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
        self.psrname = self.keywords["psrname"].value
        self.nchannels = self.keywords["nsub_band"].value
        # is this right
        self.npol = self.keywords["banda"].value["npol"].value
        logger.debug(f"Reading {self.keywords['nsub_int'].value} subints")
        self.duration = 0 * u.s
        self.read_subints(f)
        # set the start time to the start of the first subint
        self.starttime = self.subints[0].starttime
        logger.debug(f"Telescope = {self.telescope}")
        logger.debug(f"Pulsar = {self.psrname}")
        logger.debug(f"Start = {self.starttime.mjd} = {self.starttime.iso}")
        logger.debug(f"Duration = {self.duration}")

        # this is just for the first subint
        # self.duration = (
        #    self.keywords["nsub_int"].value * self.keywords["sub_int_time"].value * u.s
        # )
        self.stoptime = self.starttime + self.duration

    def read_subints(self, fptr):
        for subint in range(self.keywords["nsub_int"].value):
            self.subints.append(Subint(number=subint))
            self.subints[-1].read(fptr)
            self.duration += self.subints[-1].integration
            fptr.seek(self.subint_data_size, 1)

    @property
    def size(self):
        size = 0
        for k in self.keywords:
            size += self.keywords[k].size
        return size

    @property
    def subint_data_size(self):
        if self["wts_and_bpass"]:
            # stores data + weights + bandpass
            size = self.nchannels * _data_lengths["float"] * (1 + 2 * self.npol)
        else:
            # looks like float(scale) + float(offset) + nbin*nchan*npol*2
            # CHECK
            size = (
                _data_lengths["float"] * 2
                + self.nchannels * self.npol * self["nbin"].value * 2
            )
        # floats for centrefreq, wt
        # ints for nbin, poln
        size += self.nchannels * (_data_lengths["float"] * 2 + _data_lengths["int"] * 2)
        # has 2 floats + nbin * 2byte integers
        # CHECK: this is in the "no_amps" case
        # otherwise it's more complicated?
        size += self.nchannels * (2 * _data_lengths["float"] + self["nbin"].value * 2)
        return size

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

    def __setitem__(self, key, value):
        self.keywords[key].value = value


_timer_keyword_definition = get_definition("timer.h")
_band_keyword_definition = get_definition("band.h")
_subint_keyword_definition = get_definition("mini.h")
