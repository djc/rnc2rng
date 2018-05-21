from setuptools import setup

setup(
    name='rnc2rng',
    version='2.6.1',
    url='https://github.com/djc/rnc2rng',
    author='David Mertz',
    description='RELAX NG Compact to regular syntax conversion library',
    maintainer='Dirkjan Ochtman',
    maintainer_email='dirkjan@ochtman.nl',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: Public Domain',
        'Topic :: Text Processing :: Markup :: XML',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    packages=['rnc2rng'],
    entry_points={
        'console_scripts': [
            'rnc2rng = rnc2rng.__main__:main',
        ],
    },
    use_2to3=True,
    install_requires=['rply'],
)
