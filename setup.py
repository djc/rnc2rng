from setuptools import setup

setup(
    name='rnc2rng',
    version='1.7',
    url='https://github.com/djc/rnc2rng',
    author='David Mertz',
    maintainer='Dirkjan Ochtman',
    maintainer_email='dirkjan@ochtman.nl',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=['rnc2rng'],
    entry_points={
        'console_scripts': [
            'rnc2rng = rnc2rng.__main__:main',
        ],
    },
    use_2to3=True,
)
