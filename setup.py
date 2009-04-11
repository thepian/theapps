from setuptools import setup

setup(name='theapps',
      version=__import__('theapps').__version__,
      description="The Thepian Django Apps",
      long_description="""\
""",
      keywords='thepian theapps django',
      author='Henrik Vendelbo',
      author_email='hvendelbo.dev@googlemail.com',
      url='www.thepian.org',
      license='GPL',
      packages= ['theapps'],
      include_package_data=True,
      zip_safe=False,
      setup_requires=['setuptools',],
      entry_points= {
        'console_scripts':[
            'theapps-admin = theapps:execute_from_command_line',
        ],
      },
      classifiers=[
        'Development Status :: Alpha',
        'Environment :: Web Environment',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: JavaScript',
        ], 
      )