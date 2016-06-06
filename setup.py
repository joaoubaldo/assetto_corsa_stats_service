import os

from setuptools import setup, find_packages

from acss import VERSION

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'requirements.txt')) as f:
    requires = f.read().splitlines()

setup(name='acss',
      version=VERSION,
      description='acss',
      long_description=README + '\n',
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Joao Coutinho',
      author_email='me at joaoubaldo.com',
      url='https://b.joaoubaldo.com',
      keywords='web assetto-corsa dedicated server stats statistics timing',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="acss",
      entry_points={
        'console_scripts':
            ['acss_cron = acss.cli.cron:run',
            'acssd = acss.cli.wsgi_service:run']
        }
      )
