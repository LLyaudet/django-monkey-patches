#!/bin/bash
echo "Building README.md"
./build_readme.sh

echo "Running isort"
isort .

echo "Running black"
black .

echo "Running pylint"
pylint src/django_monkey_patches/

shopt -s globstar

too_long_code_lines() {
  grep -r '.\{71\}' **/*.c
  grep -r '.\{71\}' **/*.css
  grep -r '.\{71\}' **/*.h
  grep -r '.\{71\}' **/*.htm
  grep -r '.\{71\}' **/*.html
  grep -r '.\{71\}' **/*.js
  grep -r '.\{71\}' **/*.json
  grep -r '.\{71\}' **/*.md
  grep -r '.\{71\}' **/*.php
  grep -r '.\{71\}' **/*.py
  grep -r '.\{71\}' **/*.sql
  grep -r '.\{71\}' **/*.tex
  grep -r '.\{71\}' **/*.toml
  grep -r '.\{71\}' **/*.ts
  grep -r '.\{71\}' **/*.txt
  grep -r '.\{71\}' **/*.yml
  grep -r '.\{71\}' **/COPYING
  grep -r '.\{71\}' **/COPYING.LESSER
}

echo "Analyzing too long lines"
too_long_code_lines

