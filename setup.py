import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='audiapi',
    version='1.0.0',
    author='davidgiga1993',
    author_email='david@dev-core.org',
    description='Provides access to the Audi Connect API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/davidgiga1993/AudiAPI',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries'
    ],
)
