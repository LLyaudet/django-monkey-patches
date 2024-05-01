#!/usr/bin/env bash
# This file is part of django-monkey-patches library.
#
# django-monkey-patches is free software:
# you can redistribute it and/or modify it under the terms
# of the GNU Lesser General Public License
# as published by the Free Software Foundation,
# either version 3 of the License,
# or (at your option) any later version.
#
# django-monkey-patches is distributed in the hope
# that it will be useful,
# but WITHOUT ANY WARRANTY;
# without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of
# the GNU Lesser General Public License
# along with django-monkey-patches.
# If not, see <http://www.gnu.org/licenses/>.
#
# ©Copyright 2023-2024 Laurent Lyaudet

echo "Building README.md"
personal="https://raw.githubusercontent.com/LLyaudet/"
script="DevOrSysAdminScripts/main/build_readme.sh"
correct_sha512="058b06a2b072107860982054201f925035810fd9a7331a5b58573"
correct_sha512+="5fdcd41b4ec63b85c17a6ecbb55d353c628655e51360a462f4b4"
correct_sha512+="460dbcc6c2ec6292157bf04"
if [[ ! -f "./build_readme.sh" ]];
then
  wget "$personal""$script"
fi
chmod +x ./build_readme.sh
present_sha512=`sha512sum ./build_readme.sh | cut -f1 -d' '`
if [[ "$present_sha512" != "$correct_sha512" ]];
then
  echo "build_readme.sh does not have correct sha512"
  echo "wanted $correct_sha512"
  echo "found $present_sha512"
  exit
fi
./build_readme.sh

echo "Running isort"
isort .

echo "Running black"
black .

echo "Running pylint"
pylint src/django_monkey_patches/

shopt -s globstar

echo "Analyzing too long lines"
personal="https://raw.githubusercontent.com/LLyaudet/"
script="DevOrSysAdminScripts/main/too_long_code_lines.sh"
correct_sha512="c2519bc1f63b7b13a7c8083e38f1fa245e485a169846386c50f6b"
correct_sha512+="639fa9d205dff35a4aa2125cb662434329011aaa714b6e1b2836"
correct_sha512+="69f42048eeddb8269f23259"
if [[ ! -f "./too_long_code_lines.sh" ]];
then
  wget "$personal""$script"
fi
chmod +x ./too_long_code_lines.sh
present_sha512=`sha512sum ./too_long_code_lines.sh | cut -f1 -d' '`
if [[ "$present_sha512" != "$correct_sha512" ]];
then
  echo "too_long_code_lines.sh does not have correct sha512"
  echo "wanted $correct_sha512"
  echo "found $present_sha512"
  exit
fi
source ./too_long_code_lines.sh
too_long_code_lines
