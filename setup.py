from setuptools import setup, find_packages


def readme_data():
    with open("README.md", "r") as fh:
        long_description = fh.read()
    return long_description


find_packages()

setup(name='allpoetry',
      version='0.0.1',
      description='Python API for allpoetry.com',
      long_description=readme_data(),
      long_description_content_type="text/markdown",
      url='https://github.com/arthurdjn/allpoetry',
      author='Arthur Dujardin',
      author_email='adujardin.contact@gmail.com',
      license='GNU 3',

      install_requires=['beautifulsoup4', 'lxml', 'requests'],
      packages=find_packages(),
      zip_safe=False,
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 5 - Production/Stable',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',

          # Pick your license as you wish (should match "license" above)

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python :: 3',
      ]
      )
