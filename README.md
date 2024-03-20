# django-monkey-patches

[![pypi-version]][pypi]
[![Downloads](https://img.shields.io/pypi/dm/django-monkey-patches)](https://pypistats.org/packages/django-monkey-patches)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![CodeFactor](https://www.codefactor.io/repository/github/llyaudet/django-monkey-patches/badge)](https://www.codefactor.io/repository/github/llyaudet/django-monkey-patches)
[![CodeClimateMaintainability](https://api.codeclimate.com/v1/badges/c928d2b8b724abcb2913/maintainability)](https://codeclimate.com/github/LLyaudet/django-monkey-patches/maintainability)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/de6280433b32447684458fb655c3a4b3)](https://app.codacy.com/gh/LLyaudet/django-monkey-patches/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
![GitHub top language](https://img.shields.io/github/languages/top/llyaudet/django-monkey-patches)
![GitHub License](https://img.shields.io/github/license/llyaudet/django-monkey-patches)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-monkey-patches)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/llyaudet/django-monkey-patches)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/LLyaudet)](https://github.com/sponsors/LLyaudet)

|     **A collection of monkey patches to improve Django framework**     |


## Use

Each monkey-patch `beautiful_patch` should be available with a function `apply_beautiful_patch()`.
Hence, all you have to do is:

```python
from django_monkey_patches.django__beautiful_class__beautiful_patch import apply_beautiful_patch

apply_beautiful_patch()
```

For example, you can do it in your Django settings.py file or in a file imported in settings.py.


## Choosing a patch

Look at the source code on GitHub.
The rational behind each patch is given in the source code file.
If you cannot bother reading the source code of a patch of ten or twenty lines,
you probably should not apply it anyway ;).


## F.A.Q.

### Why does the version not follow Django versions?

Because I plan to add monkey-patches for other packages around Django itself.
For example, Django Rest Framework (DRF) is in "maintenance mode only".
It does not accept new features and is only updated to keep compatibility with new versions of Django.
Moreover, many patches wil be plainly compatible with most versions of Django,
and I don't see the need of multiplying versions.
So instead, I use semantic versioning relative to the proposed patches.

### Why is Django not a dependency?

See previous question.

### Why is there no tests folder?

See previous question.

[pypi-version]: https://img.shields.io/pypi/v/django-monkey-patches.svg
[pypi]: https://pypi.org/project/django-monkey-patches/
