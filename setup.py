# spawn
# Copyright (C) 2018, Simmovation Ltd.
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
from setuptools import setup, Command

class ApplyLicenseCommand(Command):
    user_options = [
        ('check=', None, 'Perform a license check')
    ]

    GPL_V3_LICENSE = """{description}
    {copyright}

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software Foundation,
    Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA"""

    def initialize_options(self):
        self.check = False

    def finalize_options(self):
        pass

    def run(self):
        import spawn
        from glob import glob

        name = spawn.__name__
        copyright_ = spawn.__copyright__

        license_header = ['# ' + line.strip() + '\n' for line in self.GPL_V3_LICENSE.format(description=name, copyright=copyright_).split('\n')]

        files_modified = []

        for file_name in glob('**/*.py', recursive=True):
            with open(file_name) as fp:
                lines = fp.readlines()
            
            old_header, lines = self._split_header(lines)
            if old_header != license_header:
                if not self.check:
                    with open(file_name, 'w') as fp:
                        fp.writelines(license_header + lines)
                files_modified.append(file_name)
        
        if self.check and files_modified:
            raise RuntimeError('License needs to be updated in the following files: ' + ', '.join(files_modified))

    @staticmethod
    def _split_header(lines):
        for line_number, line in enumerate(lines):
            if not line or line[0] != '#':
                return lines[:line_number], lines[line_number:]
        # Every line is commented
        return lines, []

install_requires = [
    'luigi==2.8.2',
    'setuptools>=38.3',
    'click==7.0',
    'appdirs==1.4.3'
]

tests_require = [
    'pytest',
    'pytest-mock',
    'pytest-cov',
    'pylint',
    'numpy',
    'pandas',
    'tox'
]

extras_require = {
    'test': tests_require,
    'docs': ['sphinx', 'sphinx-click', 'm2r'],
}

setup(
    name='spawn-core',
    version='0.1',
    packages=['spawn'],
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    cmdclass={
        'apply_license': ApplyLicenseCommand
    }
)
