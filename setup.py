from setuptools import setup

with open('README.md') as readme_file:
    README = readme_file.read()

setup(
    name='pseudomyth',
    description=(
        'A script with which to determine what order to watch anime episodes '
        'in'
    ),
    url='https://github.com/colons/pseudomyth',
    author='Iain Dawson',
    author_email='pypi@colons.co',
    version='1.0.3',
    license="BSD",
    platforms=['any'],
    packages=['pseudomyth'],
    scripts=['scripts/pseudomyth'],
    long_description=README,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
)
