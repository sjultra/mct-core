import setuptools

setuptools.setup(
    name='mct',
    author='Madalin Bivolan',
    author_email='madalin@sjultra.com',
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    python_requires='>=3.6',
    extras_require={
        'dev': ['check-manifest'],
    }
)