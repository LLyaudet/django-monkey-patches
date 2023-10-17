# django-monkey-patches

A collection of monkey patches to improve Django framework


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

