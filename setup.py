from distutils.core import setup

majv = 1
minv = 0

setup(
	name = 'dictdiff',
	version = "%d.%d" %(majv,minv),
	description = "Python module to perform a diff on dictionaries",
	author = "Colin ML Burnett",
	author_email = "cmlburnett@gmail.com",
	url = "",
	packages = ['dictdiff'],
	package_data = {'dictdiff': ['dictdiff/__init__.py']},
	classifiers = [
		'Programming Language :: Python :: 3.5'
	]
)
