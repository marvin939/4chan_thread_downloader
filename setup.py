from distutils.core import setup

with open('README.MD') as f:
    long_description = f.read()

setup(
    name='thread_files',
    packages=['thread_files'],
    version='1.0.0',
    description='A 4chan thread downloader',
    long_description=long_description,
    author='Marvin Muyargas',
    author_email='',
    license='MIT',
    url='https://github.com/marvin939/thread_files',
    python_requires='>=3.5',
    keywords=['automation', '4chan threads', 'download', 'synchronise'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        'beautifulsoup4>=4.6.0',
        'lxml>=4.1.1',
        'requests>=2.18.4',
    ],
)