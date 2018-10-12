from setuptools import setup, find_packages

install_requires = [
    'luigi',
    'numpy',
    'pandas',
    'wetb',
    'setuptools>=38.3'
]

tests_require = [
    'pytest',
    'tox'
]

extras_require = {
    'test': tests_require
}

setup(
    name='multiwindcalc',
    version='0.1',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require
)
