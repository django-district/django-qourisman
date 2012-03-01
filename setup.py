from setuptools import setup, find_packages

template_patterns = [
    'templates/*.html',
    'templates/*/*.html',
    'templates/*/*/*.html',
    ]

packages = find_packages()

setup(
    name='django-qourisman',
    version='0.0.5',
    url='https://github.com/django-district/django-qourisman',
    license='http://code.djangoproject.com/browser/django/trunk/LICENSE',
    packages=packages,
    package_data=dict( (package_name, template_patterns)
                   for package_name in packages ),
    description='A collection of Django admin extensions',
    # test_suite="tests.all_tests",
)
