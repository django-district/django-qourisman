from setuptools import setup, find_packages

packages = find_packages()

setup(
    name='django-qourisman',
    version='0.0.6',
    url='https://github.com/django-district/django-qourisman',
    license='http://code.djangoproject.com/browser/django/trunk/LICENSE',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    description='A collection of Django admin extensions',
    # test_suite="tests.all_tests",
)
