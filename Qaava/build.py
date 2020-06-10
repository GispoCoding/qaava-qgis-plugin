#!/usr/bin/env python
# -*- coding: utf-8 -*-
import glob
import os
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path

import pytest

'''
/***************************************************************************
Qaava


							 -------------------
		begin				: 2020-06-04
		email				: joona@gispo.fi
***************************************************************************/

/***************************************************************************
*																		 *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or	 *
*   (at your option) any later version.								   *
*																		 *
***************************************************************************/

#################################################
# Edit the following to match your sources lists
#################################################
'''

PLUGINNAME = "Qaava"

# This should be only edited for windows environment
QGIS_INSTALLATION_DIR = os.path.join("C:", "OSGeo4W64", "bin")

# Add files for any locales you want to support here
LOCALES = ["Qaava_fi"]

# If locales are enabled, set the name of the lrelease binary on your system. If
# you have trouble compiling the translations, you may have to specify the full path to
# lrelease

LRELEASE = "lrelease"  # 'lrelease-qt4'
PYRCC = "pyrcc5"

# Name of the QGIS profile you are using in development
PROFILE = "dev"

# source .py files
QAAVA = [fil for fil in glob.glob("**/*.py", recursive=True)
         if "test/" not in fil]

# ui files
UI = list(glob.glob("**/*.ui", recursive=True))

# Resource files
RESOURCES_SRC = list(glob.glob("**/*.qrc", recursive=True))

# sources
SOURCES = [*QAAVA]

PY_FILES = [*QAAVA]

UI_FILES = [*UI]

EXTRAS = ["metadata.txt"]

EXTRA_DIRS = ["icons", "logs"]

COMPILED_RESOURCE_FILES = ["resources.py"]

'''
#################################################
# Normally you would not need to edit below here
#################################################
'''


def is_windows():
    return "win" in sys.platform


# QGISDIR points to the location where your plugin should be installed.
# This varies by platform, relative to your HOME directory:
#	* Linux:
#	  .local/share/QGIS/QGIS3/profiles/default/python/plugins/
#	* Mac OS X:
#	  Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins
#	* Windows:
#	  AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins'

if sys.platform == "linux":
    dr = os.path.join(".local", "share")
elif is_windows():
    dr = os.path.join("AppData", "Roaming")
else:
    dr = os.path.join("Library", "Application Support")

QGISDIR = os.path.join(dr, "QGIS", "QGIS3", "profiles", PROFILE)

PLUGINDIR = os.path.join(str(Path.home()), QGISDIR, "python", "plugins", PLUGINNAME)

I18N = "i18n"

WINDOWS_ENV_BATS = [
    'o4w_env.bat',
    'qt5_env.bat',
    'py3_env.bat'
]


class PluginMaker:

    def __init__(self):
        # git-like usage https://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html
        usage = f'''build.py <command> [<args>]

Commands:
     clean          Cleans resources
     compile        Compiles resources to resources.py
     deploy         Deploys the plugin to the QGIS plugin directory ({PLUGINDIR})
     package        Builds a package that can be uploaded to Github releases or to the plugin
     test           Runs tests
     transup        Search for new strings to be translated
     transcompile   Compile translation files to .qm files.

Put -h after command to see available optional arguments if any
'''
        parser = ArgumentParser(usage=usage)
        parser.add_argument('command', help='Subcommand to run')
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            parser.print_help()
            exit(1)

        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def clean(self):
        for fil in COMPILED_RESOURCE_FILES:
            if os.path.exists(fil):
                print(f"rm {fil}")
                os.remove(fil)

    def compile(self):
        pre_args = self._get_platform_args()
        for fil in RESOURCES_SRC:
            if os.path.exists(fil):
                args = pre_args + [PYRCC, "-o", fil.replace(".qrc", ".py"), fil]
                self.run_command(args)
            else:
                raise ValueError(f"The expected resource file {fil} is missing!")

    def _get_platform_args(self):
        pre_args = []
        if is_windows():
            pre_args = [item for sublist in [f"call {bat} &&".split() for bat in WINDOWS_ENV_BATS] for item in sublist]
        return pre_args

    def deploy(self):
        self.compile()
        dst_dir = f"{PLUGINDIR}/"
        os.makedirs(PLUGINDIR, exist_ok=True)
        self.cp_parents(dst_dir, PY_FILES)
        self.cp_parents(dst_dir, UI_FILES)
        self.cp_parents(dst_dir, COMPILED_RESOURCE_FILES)
        self.cp_parents(dst_dir, EXTRAS)
        dirs = [I18N] + EXTRA_DIRS
        for dr in dirs:
            print(f"cp -R --parents {dr} {dst_dir}")
            shutil.copytree(dr, os.path.join(PLUGINDIR, dr))

    def package(self):
        parser = ArgumentParser()
        parser.add_argument('--version', type=str, help="Version number of the tag (eg. --version v0.0.1")
        parser.add_argument('--tag', action='store_true',
                            help="Run git tag as well. REMEMBER to update metadata.txt with your version before this")
        parser.set_defaults(test=False)
        args = parser.parse_args(sys.argv[2:])
        if args.version is None:
            print("Give valid version number")
            parser.print_help()
            exit(1)

        if args.tag:
            self.run_command(["git", "tag", args.version])

        pkg_command = ["git", "archive", f"--prefix={PLUGINNAME}/", "-o", f"{PLUGINNAME}.zip", args.version]
        self.run_command(pkg_command)
        print(f"Created package: {PLUGINNAME}.zip")

    def test(self):
        self.compile()
        os.environ["PYTHONPATH"] = f"{os.path.abspath(os.path.dirname(__file__))}"
        os.environ["QGIS_DEBUG"] = "0"
        os.environ["QGIS_LOG_FILE"] = "/dev/null" if not is_windows() else "NUL"
        pytest.main(["-v", "test", "--cov=.", "test"])

    def transup(self):
        args = self._get_platform_args() + ["pylupdate5", f"{I18N}/translate.pro"]
        self.run_command(args)

    def transcompile(self):
        pre_args = self._get_platform_args()
        for locale in LOCALES:
            fil = os.path.join(I18N, f"{locale}.ts")
            print(f"Processing {fil}")
            args = pre_args + [LRELEASE, "-qt=qt5", fil]
            self.run_command(args)

    @staticmethod
    def run_command(args):
        print(" ".join(args))
        pros = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = pros.communicate()
        print(stdout)
        if len(stderr):
            raise ValueError("Stopping now due to error in stderr!")

    @staticmethod
    def cp_parents(target_dir, files):
        """https://stackoverflow.com/a/15340518"""
        dirs = []
        for file in files:
            dirs.append(os.path.dirname(file))
        dirs.sort(reverse=True)
        for i in range(len(dirs)):
            if not dirs[i] in dirs[i - 1]:
                need_dir = os.path.normpath(target_dir + dirs[i])
                print("mkdir", need_dir)
                os.makedirs(need_dir, exist_ok=True)
        for file in files:
            dest = os.path.normpath(target_dir + file)
            print(f"cp {file} {dest}")
            shutil.copy(file, dest)


if __name__ == '__main__':
    PluginMaker()
