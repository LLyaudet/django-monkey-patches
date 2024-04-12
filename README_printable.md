# django-monkey-patches

[![PyPI-version-badge]][PyPI-package-page]
[![Downloads-badge]][PyPIStats-package-page]
[![Code-style:black:badge]][Black-GitHub.com]
[![Imports:isort:badge]][Isort-GitHub.io]
[![Linting:pylint:badge]][Pylint-GitHub.com]
[![CodeFactor-badge]][CodeFactor-package-page]
[![CodeClimateMaintainability-badge]][CodeClimateM13y-package-page]
[![Codacy-badge]][Codacy-package-page]
![GitHub-top-language-badge]
![GitHub-license-badge]
![PyPI-python-version-badge]
![GitHub-code-size-in-bytes-badge]
[![GitHub-sponsors-badge]][GitHub-sponsors-page]

| **A collection of monkey patches to improve Django framework** |


## Use

Each monkey-patch `beautiful_patch` should be available
with a function `apply_beautiful_patch()`.
Hence, all you have to do is:

```python
from django_monkey_patches.django__beautiful_class__beautiful_patch\
    import apply_beautiful_patch

apply_beautiful_patch()
```

For example, you can do it in your Django settings.py file
or in a file imported in settings.py.


## Choosing a patch

Look at the source code on GitHub.
The rational behind each patch is given in the source code file.
If you cannot bother reading the source code
of a patch of ten or twenty lines,
you probably should not apply it anyway ;).


## F.A.Q.

### Why does the version not follow Django versions?

Because I plan to add monkey-patches for other packages
around Django itself.
For example, Django Rest Framework (DRF)
is in "maintenance mode only".
It does not accept new features
and is only updated to keep compatibility
with new versions of Django.
Moreover,
many patches wil be plainly compatible with most versions of Django,
and I don't see the need of multiplying versions.
So instead,
I use semantic versioning relative to the proposed patches.

### Why is Django not a dependency?

See previous question.

### Why is there no tests folder?

See previous question.

[PyPI-version-badge]: https://img.shields.io/pypi/v/\
django-monkey-patches.svg

[PyPI-package-page]: https://pypi.org/project/django-monkey-patches/

[Downloads-badge]: https://img.shields.io/pypi/dm/\
django-monkey-patches

[PyPIStats-package-page]: https://pypistats.org/packages/\
django-monkey-patches

[Code-style:black:badge]: https://img.shields.io/badge/\
code%20style-black-000000.svg

[Black-GitHub.com]: https://github.com/psf/black

[Imports:isort:badge]: https://img.shields.io/badge/\
%20imports-isort-%231674b1?style=flat&labelColor=ef8336

[Isort-GitHub.io]: https://pycqa.github.io/isort/

[Linting:pylint:badge]: https://img.shields.io/badge/\
linting-pylint-yellowgreen

[Pylint-GitHub.com]: https://github.com/pylint-dev/pylint

[CodeFactor-badge]: https://www.codefactor.io/repository/github/\
llyaudet/django-monkey-patches/badge

[CodeFactor-package-page]: https://www.codefactor.io/repository/\
github/llyaudet/django-monkey-patches

[CodeClimateMaintainability-badge]: https://api.codeclimate.com/v1/\
badges/c928d2b8b724abcb2913/maintainability

[CodeClimateM13y-package-page]: https://codeclimate.com/\
github/LLyaudet/django-monkey-patches/maintainability

[Codacy-badge]: https://app.codacy.com/project/badge/Grade/\
de6280433b32447684458fb655c3a4b3

[Codacy-package-page]: https://app.codacy.com/gh/LLyaudet/\
django-monkey-patches/dashboard?utm_source=gh&utm_medium=referral\
&utm_content=&utm_campaign=Badge_grade

[GitHub-top-language-badge]: https://img.shields.io/github/\
languages/top/llyaudet/django-monkey-patches

[GitHub-license-badge]: https://img.shields.io/github/license/\
llyaudet/django-monkey-patches

[PyPI-python-version-badge]: https://img.shields.io/pypi/pyversions/\
django-monkey-patches

[GitHub-code-size-in-bytes-badge]: https://img.shields.io/github/\
languages/code-size/llyaudet/django-monkey-patches

[GitHub-sponsors-badge]: https://img.shields.io/github/sponsors/\
LLyaudet

[GitHub-sponsors-page]: https://github.com/sponsors/LLyaudet
