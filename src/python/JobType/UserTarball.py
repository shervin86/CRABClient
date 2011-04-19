#! /usr/bin/env python

"""
    UserTarball class, a subclass of TarFile
"""

import os
import glob
import tarfile

from ScramEnvironment import ScramEnvironment

class UserTarball(object):
    """
        _UserTarball_

            A subclass of TarFile for the user code tarballs. By default
            creates a new tarball with the user libraries from lib, module,
            and the data/ sections of the src/ area.

            Also adds user specified files in the right place.
    """

    def __init__(self, name=None, mode='w:gz', logger=None):
        self.logger = logger
        self.scram = ScramEnvironment(logger=self.logger)
        self.logger.debug("Making tarball in %s" % name)
        self.tarfile = tarfile.open(name=name, mode=mode, dereference=True)

    def addFiles(self, userFiles=None):
        """
        Add the necessary files to the tarball
        """
        directories = ['lib', 'module']
        dataDirs    = ['data']
        userFiles = userFiles or []

        # Tar up whole directories
        for directory in  directories:
            fullPath = os.path.join(self.scram.getCmsswBase(), directory)
            self.logger.debug(" checking directory %s" % fullPath)
            if os.path.exists(fullPath):
                self.logger.debug(" adding directory %s to tarball" % fullPath)
                self.tarfile.add(fullPath, directory, recursive=True)

        # Search for and tar up "data" directories in src/
        srcPath = os.path.join(self.scram.getCmsswBase(), 'src')
        for root, _dummy, _dummy in os.walk(srcPath):
            if os.path.basename(root) in dataDirs:
                directory = root.replace(srcPath,'src')
                self.logger.debug(" adding data directory %s to tarball" % root)
                self.tarfile.add(root, directory, recursive=True)

        # Tar up extra files the user needs
        for globName in userFiles:
            for filename in glob.glob(globName):
                self.logger.debug(" adding file %s to tarball" % filename)
                self.tarfile.add(filename, os.path.basename(filename), recursive=True)


    def __getattr__(self, *args):
        """
        Pass any unknown functions or attribute requests on to the TarFile object
        """
        self.logger.debug("Passing getattr %s on to TarFile" % args)
        return self.tarfile.__getattribute__(*args)


    def __enter__(self):
        """
        Allow use as context manager
        """
        return self


    def __exit__(self, excType, excValue, excTrace):
        """
        Allow use as context manager
        """
        self.tarfile.close()
        if excType:
            return False