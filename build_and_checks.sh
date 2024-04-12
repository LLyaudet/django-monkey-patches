#!/bin/bash
echo "Building README.md"
./build_readme.sh

echo "Running isort"
isort .

echo "Running black"
black .

echo "Running pylint"
pylint src/django_monkey_patches/

too_long_code_lines() {
  grep -r '.\{71\}' {./**.c,./**.css,./**.h,./**.html,./**.js,./**.json,./**.md,./**.php,./**.py,./**.sql,./**.tex,./**.toml,./**.ts,./**.txt,./**.yml,./**COPYING,./**COPYING.LESSER}
}

echo "Analyzing too long lines"
too_long_code_lines

