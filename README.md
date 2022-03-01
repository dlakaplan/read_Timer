# read_Timer
Read [PSRCHIVE](http://psrchive.sourceforge.net/) Timer file headers

## Requirements:
* `astropy`

## Contents:
In `read_Timer/data` are 3 header files taken from `PSRCHIVE` that are used to define the metadata:
* `timer.h`: overall metadata header
* `band.h`: individual sub-bands
* `mini.h`: mini-header for each sub-integration

## Example:
```
In [1]: import read_Timer

In [2]: h=read_Timer.TimerHeader("J2035+36_59216.ar")
2022-02-24 21:14:47.559 | DEBUG    | read_Timer:__init__:151 - Reading Timer file J2035+36_59216.ar
2022-02-24 21:14:47.578 | DEBUG    | read_Timer:__init__:204 - Telescope = CHIME
2022-02-24 21:14:47.578 | DEBUG    | read_Timer:__init__:205 - Pulsar = J2035+36
2022-02-24 21:14:47.578 | DEBUG    | read_Timer:__init__:206 - Start = 59216.89949564594 = 2021-01-02 21:35:16.424
2022-02-24 21:14:47.578 | DEBUG    | read_Timer:__init__:207 - Duration = 374.0147602558136 s

In [3]: h
Out[3]: Timer file J2035+36_59216.ar: J2035+36 at MJD 59216.89949564594 for 374.0147602558136 s with CHIME

In [4]: print(h)
Timer file J2035+36_59216.ar: J2035+36 at MJD 59216.89949564594 for 374.0147602558136 s with CHIME:
ram_boards[char, 32 bytes] =  
corr_boards[char, 32 bytes] =  
machine_id[char, 8 bytes] = ?????
version[float, 4 bytes] = -1.0
minorversion[float, 4 bytes] = -1.0
tape_number[int, 4 bytes] = -1
file_number[int, 4 bytes] = -1
utdate[char, 16 bytes] = 02-01-2021
fracmjd[double, 8 bytes] = 0.8994956459396523
mjd[int, 4 bytes] = 59216
number_of_ticks[int, 4 bytes] = 0
offset[double, 8 bytes] = 0.0
lst_start[double, 8 bytes] = 20.462795104849214
coord_type[char, 8 bytes] = 05
psrname[char, 16 bytes] = J2035+36
ra[double, 8 bytes] = 5.391234401463204
dec[double, 8 bytes] = 0.6436600030724963
l[float, 4 bytes] = 76.93730163574219
b[float, 4 bytes] = 76.93730163574219
nominal_period[double, 8 bytes] = 0.024546332407460934
dm[float, 4 bytes] = 136.71099853515625
fold_true_ratio[int, 4 bytes] = 1
nperiods_long[int, 4 bytes] = -1
nperiods_short[int, 4 bytes] = 0
nbin[int, 4 bytes] = 64
tsmp[float, 4 bytes] = -1.0
sub_int_time[float, 4 bytes] = 3.5620453357696533
ndump_sub_int[int, 4 bytes] = 1
narchive_int[int, 4 bytes] = 1
junk[int, 4 bytes] = 0
nsub_int[int, 4 bytes] = 105
junk2[int, 4 bytes] = 0
dump_time[float, 4 bytes] = 3.5620453357696533
nfreq[int, 4 bytes] = 1
nsub_band[int, 4 bytes] = 1024
feedmode[int, 4 bytes] = 0
tree[char, 8 bytes] =  
telid[char, 16 bytes] = CHIME
tpover[char, 8 bytes] = 10.0
nspan[int, 4 bytes] = 0
ncoeff[int, 4 bytes] = 0
nbytespoly[int, 4 bytes] = 1121
nbytesephem[int, 4 bytes] = 237
banda[band, 96 bytes] = -400.0 MHz band at 600.1953125 MHz:
lo1[double, 8 bytes] = -1.0
lo2[double, 8 bytes] = -1.0
loUP[double, 8 bytes] = -1.0
loDOWN[double, 8 bytes] = -1.0
centrefreq[double, 8 bytes] = 600.1953125
bw[double, 8 bytes] = -400.0
flux_A[float, 4 bytes] = -1.0
inv_mode[int, 4 bytes] = -1
auto_atten[int, 4 bytes] = 0
correlator_mode[int, 4 bytes] = 0
f_atten_A[float, 4 bytes] = -1.0
f_atten_B[float, 4 bytes] = -1.0
polar[int, 4 bytes] = 1
feed_offset[float, 4 bytes] = 0.0
nlag[int, 4 bytes] = -1
flux_B[float, 4 bytes] = -1.0
flux_err[float, 4 bytes] = -1.0
npol[int, 4 bytes] = 1
bandb[band, 96 bytes] = -1.0 MHz band at -1.0 MHz:
lo1[double, 8 bytes] = -1.0
lo2[double, 8 bytes] = -1.0
loUP[double, 8 bytes] = -1.0
loDOWN[double, 8 bytes] = -1.0
centrefreq[double, 8 bytes] = -1.0
bw[double, 8 bytes] = -1.0
flux_A[float, 4 bytes] = -1.0
inv_mode[int, 4 bytes] = -1
auto_atten[int, 4 bytes] = 0
correlator_mode[int, 4 bytes] = -1
f_atten_A[float, 4 bytes] = -1.0
f_atten_B[float, 4 bytes] = -1.0
polar[int, 4 bytes] = -1
feed_offset[float, 4 bytes] = 0.0
nlag[int, 4 bytes] = 0
flux_B[float, 4 bytes] = 0.0
flux_err[float, 4 bytes] = 0.0
npol[int, 4 bytes] = -2
rotm[float, 4 bytes] = 0.0
rmi[float, 4 bytes] = 0.0
pnterr[float, 4 bytes] = -100000.0
ibeam[int, 4 bytes] = 0
tape_label[char, 8 bytes] =  
schedule[char, 32 bytes] = 2021002213516
comment[char, 64 bytes] = TimerArchive created on raid-15.mort - Fri Jun 25 13:04:16 2021
pos_angle[float, 4 bytes] = -10000.0
headerlength[int, 4 bytes] = 1024
corrected[int, 4 bytes] = 0
calibrated[int, 4 bytes] = 0
obstype[int, 4 bytes] = 0
calfile[char, 24 bytes] =  
scalfile[char, 24 bytes] =  
wts_and_bpass[int, 4 bytes] = 1
wtscheme[int, 4 bytes] = 0
software[char, 128 bytes] = dspsrn
backend[char, 8 bytes] = baseband
be_data_size[uint32_t, 4 bytes] = 184
rcvr_id[char, 8 bytes] = unknown
space[char, 184 bytes] = 
```
