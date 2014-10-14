#!/bin/sh

rm -f ./cache/anon/*
rm -f ./cache/mble/*

cd /home/ubuntu/project/wikidocs
/home/ubuntu/venvs/wikidocs/bin/python /home/ubuntu/project/wikidocs/book/cache.py clearall
