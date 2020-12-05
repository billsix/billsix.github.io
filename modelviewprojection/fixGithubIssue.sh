#!/bin/bash

find . -iname '*.rst.txt' | xargs sed -i -e 's/_static\//static\//g'
find . -iname '*.rst.txt' | xargs sed -i -e 's/_images\//images\//g'

find . -iname '*.html' | xargs sed -i -e 's/_static\//static\//g'
find . -iname '*.html' | xargs sed -i -e 's/_images\//images\//g'

find . -iname '*.inv' | xargs sed -i -e 's/_static\//static\//g'
find . -iname '*.inv' | xargs sed -i -e 's/_images\//images\//g'

find . -iname '*.js' | xargs sed -i -e 's/_static\//static\//g'
find . -iname '*.js' | xargs sed -i -e 's/_images\//images\//g'
