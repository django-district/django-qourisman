from setuptools import setup, find_packages
import glob

template_files = glob.glob("qourisman/templates/admin/*")
print template_files

setup(
    name='django-qourisman',
    version='0.0.5',
    url='https://github.com/django-district/django-qourisman',
    license='http://code.djangoproject.com/browser/django/trunk/LICENSE',
    packages=find_packages(),
    data_files=[('qourisman/templates/admin', template_files)],
    description='A collection of Django admin extensions',
    # test_suite="tests.all_tests",
)
