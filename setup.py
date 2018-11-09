from setuptools import setup, find_packages

install_requires = [
    'luigi',
    'numpy',
    'pandas',
    'wetb',
    'setuptools>=38.3',
    'click',
    'appdirs'
]

tests_require = [
    'pytest',
    'pytest-mock',
    'pylint',
    'tox'
]

extras_require = {
    'test': tests_require,
    'docs': ['sphinx', 'sphinx-click']
}

setup(
    name='multiwindcalc',
    version='0.1',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require
)
