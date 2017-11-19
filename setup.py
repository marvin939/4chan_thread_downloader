from distutils.core import setup

with open('README.MD') as f:
    long_description = f.read()

setup(
    name='thread_files',
    packages=['thread_files'],
    version='1.0.0',
    description=long_description,
    author='Marvin Muyargas',
    author_email='',
    url='https://github.com/marvin939/4chan_thread_downloader',
    python_requires='>=3.5',
    install_requires=[

    ],
)