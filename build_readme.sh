#!/bin/bash
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

sed -Ez 's/(\[[a-zA-Z0-9:-]*\]: [^\n\\]*)\\\n/\1/Mg'\
  README_printable.md > README_temp.md
sed -Ez 's/(\[[a-zA-Z0-9:-]*\]: [^\n\\]*)\\\n/\1/Mg'\
  README_temp.md > README.md
rm -f README_temp.md

