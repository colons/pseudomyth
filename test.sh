#!/bin/sh -ex
for file in $(find . -name '*.py'); do python -m doctest -v $file; done
