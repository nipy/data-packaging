#!/usr/bin/env python
''' Re-create and check data packages

The script expects to be run something like this:

<script_name> <pkg_dir>

where <pkg_dir> is a directory containing the tree for a nipy data
package.  <pkg_dir> will therefore contain a ``setup.py`` file, and will
contain one and only one data sub-directory <datadir> with at least a
``config.ini`` file, giving the package version.

The script runs ``python setup.py sdist`` on the package to check the
sdist mechanism and generate the archive.  It then unpacks the generated
archive in a temporary directory, installs it with ``python setup.py
install`` in that same temporary directory, then checks that NIPY can
read the package.
'''

from __future__ import with_statement

import os
from os.path import join as pjoin
import sys
import re
import subprocess
from functools import partial
from glob import glob
import zipfile
import tarfile
import shutil

from nipy.utils import InTemporaryDirectory, make_datasource

caller = partial(subprocess.check_call, shell=True)

pkg_re = re.compile(r"nipy-(\w+)-\d+\.\d+")

format2ext = {
    'bztar': 'tar.bz2',
    'gztar': 'tar.gz',
    'tar': 'tar',
    'zip': 'zip',
    'ztar': 'tar.Z'}


def extract_zip(zipobj, todir=''):
    ''' Extract all files in ZipFile instance to directory `todir`

    Parameters
    ----------
    zipobj : ``ZipFile`` object
       archive from which to extract files
    todir : string, optional
       directory to which to extract zip archive contents.  Default is
       '' resulting in extraction to working directory

    Returns
    -------
    None

    Notes
    -----
    Replicates Python 2.6 ZipFile.extractall, I guess
    '''
    for name in zipobj.namelist():
        out_file = pjoin(todir, name)
        pth, fname = os.path.split(out_file)
        try: # create directory tree on the fly
            os.makedirs(pth)
        except OSError:
            pass
        with open(out_file, 'wb') as f:
            f.write(zipobj.read(name))


def extract_archive(archive, todir=None):
    ''' Extract archive to given directory

    Deals with tar (etc) files and zip files

    Parameters
    ----------
    archive : string
       archive filename
    todir : None or string, optional
       directory to which to extract archive files (working directory if
       None)
    '''
    if todir is None:
        todir = os.getcwd()
    if archive.endswith('.zip'):
        zipf = zipfile.ZipFile(archive)
        extract_zip(zipf)
        return
    tar = tarfile.open(archive)
    tar.extractall(todir)
    
            
def check_pkg_dir(pkg_dir, clobber=False, formats=('gztar',)):
    ''' Check package creation from unpacked package directory

    Parameters
    ----------
    pkg_dir : string
       directory containing package (must contain ``setup.py`` file
    clobber : bool, optional
       whether to remove existing `pkg_dir`/dist subdirectory before we
       try and create the package (default=False).  If the directory
       does already exist, and `clobber` is False, raise an ``OSError``
    formats : sequence, optional
       tuple of formats to write, from acceptable ``sdist`` formats.
       Default is ('gztar,)
       
    Returns
    -------
    archive : list of strings
       List of created archive filenames (one per passed format)
    '''
    # check there are no dist files
    dist_dir = pjoin(pkg_dir, 'dist')
    if os.path.isdir(dist_dir):
        if clobber:
            shutil.rmtree(dist_dir)
        else:
            raise OSError('Existing dist directory %s, '
                          'consider clobber=True' % dist_dir)
    # Run sdist from directory 
    pwd = os.getcwd()
    try:
        os.chdir(pkg_dir)
        caller('python setup.py sdist --formats=%s --force-manifest' %
               ','.join(formats))
    finally:
        os.chdir(pwd)
    # Collect created archive(s)
    archives = []
    for fmt in formats:
        gpattern = pjoin(dist_dir, '*.%s' % format2ext[fmt])
        gres = glob(gpattern)
        if len(gres) == 0:
            raise OSError('Could not find expected archive with "%s"' %
                          gpattern)
        if len(gres) > 1:
            raise OSError('More archives than I wanted with "%s"' %
                          gpattern)
        archives.append(gres[0])
    return archives


def check_pkg_install(archive):
    ''' Check that source package installs so that NIPY can read it

    Parameters
    ----------
    archive : string
       filename of source archive

    Returns
    -------
    None
    '''
    # extract package name from archive
    pth, fname = os.path.split(archive)
    fname, ext = os.path.splitext(fname)
    pkg_match = pkg_re.search(fname)
    if not pkg_match:
        raise OSError('Could not get package name from %s' % archive)
    pkg_name = pkg_match.groups()[0]
    archive = os.path.abspath(archive)
    with InTemporaryDirectory() as tmpdir:
        extract_archive(archive, tmpdir)
        out_dirs = glob('*')
        if not out_dirs:
            raise OSError('No directory created by package unpack')
        if len(out_dirs) > 1:
            raise OSError('Expecting only one directory, got %s' %
                          ';'.join(out_dirs))
        os.chdir(out_dirs[0])
        caller('python setup.py install --prefix=%s' % tmpdir)
        # check that nipy finds the directory and initializes it correctly
        repo = make_datasource('share', 'nipy', 'nipy', pkg_name,
                               data_path=[tmpdir])


def main():
    archives = []
    for pkg_dir in sys.argv[1:]:
        archive = check_pkg_dir(pkg_dir, clobber=True, formats=('gztar',))[0]
        check_pkg_install(archive)
        archives.append(archive)
    print 'Checked archives'
    print archives


if __name__ == '__main__':
    main()
    
