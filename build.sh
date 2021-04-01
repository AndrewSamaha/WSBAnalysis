#!/bin/bash
pweave -f markdown README.pmd;cat README.md
git add .
git commit -m "$1"
git push