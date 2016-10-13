#!/usr/bin/env python

'''
    Script to extract absorption spectra from Dalton TDDFT calculations.
    NOTE: Currently only '*LINEAR' response calculations with '*SINGLE RESIDUE'
    option selected.

    Copyright (C) 2016  Bruce F. Milne

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

__author__ = "Bruce F. Milne"
__copyright__ = "Copyright (C) 2016 Bruce F. Milne"
__license__ = "GPL"


import numpy as np
import sys
import re

ev = []
oscstr = []
dipstr = []
com = []

# Name of the Dalton output file
log = 'mol2_TDCAMB3LYP_ACCD_CH2Cl2_LRSR.log'

# Get the absorption energies and oscillator strengths
def get_spectrum(file):
    for line in open(file, 'r'):
        if "eV" in line:
            if "cm-1" in line:
                ev.append(float(line.split()[1]))
    for line in open(file, 'r'):
        if "Oscillator strength" in line:
            oscstr.append(float(line.split()[5]))
    if len(oscstr) % 3 != 0:
        print >> sys.stderr, "Seems some components of the oscillator strengths are missing..."
        sys.exit(1)

# Get the transition dipole components
def transition(file):
    for line in open(file, 'r'):
        if "Oscillator strength" in line:
            dipstr.append(float(line.split()[9]))

# Get the center of mass in case the molecule is not centered
def get_com(file):
    for line in open(file, 'r'):
        if "Center-of-mass" in line:
            for i in 3, 4, 5:
                com.append(float(line.split()[i]))

# Now actually get the spectrum
get_spectrum(log)
transition(log)
get_com(log)

print "COM: "
print com
com = (np.array([com]).reshape(1, 3)) * 0.5292
print com
print re.sub('[\[\]]', '', str(com))
print com.dtype.name

oscstr = np.array([oscstr]).reshape(len(oscstr) / 3, 3)
oscstr = np.sum(oscstr, axis=1) / 3

dipstr = np.array([dipstr]).reshape(len(dipstr) / 3, 3)

spect = np.column_stack((ev, oscstr))

print 'Absorption spectrum from Dalton output'
print log
print
print 'Spectrum [eV, f(osc)]:'
for i in range(len(spect)):
    np.set_printoptions(suppress=True)
    print 'Root ' + str(i + 1) + ': ' + re.sub('[\[\]]', '', str(spect[i]))
    np.set_printoptions()
print

np.savetxt(log + '.txt', spect)

print 'Transition dipole moments [x, y, z]:'
for i in range(len(dipstr)):
    bild = open(log + '.' + str(i + 1) + '.bild', 'w')
    bild.write(".arrow " + re.sub('[\[\]]', '', str(com[0])) + " " + re.sub('[\[\]]', '', str(dipstr[i])))
    bild.close()
    print 'Root ' + str(i + 1) + ': ' + re.sub('[\[\]]', '', str(dipstr[i]))

#if __name__ == '__main__':
#    filename='H2TPPS3_anion_TDCAMB3LYP_ACCD_LRSR.log'
#    output=get_data(log)
#    print output
