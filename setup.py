from setuptools import setup

with open('README.rst') as readme_file:
    README = readme_file.read()

if __name__ == "__main__":
    setup(
        name='pseudomyth',
        description=(
            'A script with which to determine what order to watch anime episodes '
            'in'
        ),
        url='https://github.com/colons/pseudomyth',
        author='colons',
        author_email='pypi@colons.co',
        version='2.0.1',
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
