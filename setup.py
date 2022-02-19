from setuptools import setup

setup(
    name='parse_realestate',
    version='0.1',
    install_requires=[
        'requests',
        'BeautifulSoup4',
        'pandas',
        'tqdm',
        'build'
    ],
    entry_points={
        'console_scripts': [
            'parse_realestate = parse_realestate:main',
        ],
    }
)