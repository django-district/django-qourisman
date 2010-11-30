from setuptools import setup, find_packages

setup(
    name='django-qourisman',
    version='0.0.1',
    url='https://github.com/django-district/django-qourisman',
    license='http://code.djangoproject.com/browser/django/trunk/LICENSE',
    packages=['qourisman', 'qourisman.filterspecs'],
    description='A collection of Django admin extensions',
    # test_suite="tests.all_tests",
)
