from importlib.machinery import SourceFileLoader
from pathlib import Path
from setuptools import setup

THIS_DIR			= Path(__file__).resolve().parent
long_description	= THIS_DIR.joinpath('README.rst').read_text()
version				= SourceFileLoader('version', 'eleran/version.py').load_module()

setup(
	name='eleran',
	version=str(version.VERSION),
	description='Simple, fast sass compiler and javascript minifier with hot reloading',
	long_description=long_description,
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: MIT License',
		'Operating System :: Unix',
		'Operating System :: POSIX :: Linux',
		'Environment :: MacOS X',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
	author='Bapakode Open Source',
	author_email='opensource@bapakode.com',
	url='https://github.com/bapakode/eleran',
	entry_points="""
		[console_scripts]
		eleran=eleran.main:cli
	""",
	install_requires=[
		'click==6.7',
		'libsass==0.14.5',
		'watchgod==0.2',
		'jsmin==2.2.2'
	],
	license='MIT',
	packages=['eleran'],
	python_requires='>=3.5',
	zip_safe=True,
)