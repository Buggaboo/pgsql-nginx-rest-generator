#!/usr/bin/env python
# coding=UTF-8

'''
The MIT License (MIT)

Copyright (c) 2015 Jasm Sison

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

"""
This project was inspired by [this](http://rny.io/nginx/postgresql/2013/07/26/simple-api-with-nginx-and-postgresql.html) and [this](https://ef.gy/using-postgresql-with-nginx) and [ASP.NET Queryable](http://www.asp.net/web-api/overview/odata-support-in-aspnet-web-api/supporting-odata-query-options).

Dependencies:

* nginx
* postgresql
* openresty
* sqlparse (python)

If you're on a mac, download the src from the [openresty site](https://openresty.org/).

Build it with these parameters:
'''bash
# ./configure --help | grep without | grep lua | sed 's/disable.*//' | xargs ./configure --with-http_postgres_module && make -j6 && make install
'''

Compilation Bug: for some reason, without disabling lua completely, the openresty build (1.7.10.2) will break on x86_64 arch. (8-8-2015)

Usage: cat sql.txt | python pgsql-nginx-rest-gen.py

"""


import sys
import sqlparse

def generate_nginx_conf(create_statement):
	print str(create_statement.get_token_at_offset(3))

def main(av):
	sql_statements = ''.join(sys.stdin.readlines())

	fsql_statements = sqlparse.format(sql_statements, keyword_case='upper')
	p = sqlparse.parse(fsql_statements)
	for t in p:
		if str(t.token_first()) == 'CREATE':
			generate_nginx_conf(t)

if __name__ == '__main__':
	from sys import argv as av
	main(av)
