#!/bin/sh

rm -f ./cache/anon/*
rm -f ./cache/mble/*

cd /home/pahkey/project/wikidocs
/home/pahkey/virtualenv/wikidocs/bin/python /home/pahkey/project/wikidocs/book/cache.py clearall
