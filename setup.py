from setuptools import setup, find_packages

install_requires = [
    'luigi',
    'numpy'
]

tests_require = [
    'pytest'
]

extras_require = {
    'tests': tests_require
}

setup(
    name='multiwindcalc',
    version='0.1',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require
)
