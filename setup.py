from distutils.core import setup

setup(
    name='gamma',
    version='0.1.0',
    packages=['gamma'],
    entry_points={
        'console_scripts': [
            'gamma = gamma.__main__:main'
        ]
    },
    license='GPLv3',
    long_description=open('README').read(),
)

