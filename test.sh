#!/bin/sh

export DEVELOPMENT=1
python -W ignore::DeprecationWarning manage.py test
