from distutils.core import setup
setup(name='remcall',
      version='0.1.0',
      description='remcall - ipc using remote method calls and object proxying between different programming languages',
      author='luphord',
      author_email='luphord@protonmail.com',
      license="MIT license",
      url='https://github.com/luphord/remcall',
      packages=['remcall', 'remcall.codec', 'remcall.schema', 'remcall.communication'],
     )
