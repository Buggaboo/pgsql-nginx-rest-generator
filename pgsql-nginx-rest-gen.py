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

template = """ \

# WARNING: DO NOT USE IN PRODUCTON AS-IS. For security's sake, at least use BasicAuth.
worker_processes 8;

events {}

http {
  upstream database {
    # TODO also determine from the command-line: localhost? dbname? auth?
    postgres_server 127.0.0.1 dbname=articledb user=username password=yourpass;
  }
  
  server {
    # TODO see previous comment
    # TODO steal the best ideas from OData
    listen       8080;
    server_name  localhost;

    location /{table_name} {
      postgres_pass database;
      rds_json on;
      postgres_query    HEAD GET  "SELECT * FROM {table_name}";
      
      {escape_select_args}

      # TODO figure out which have a default value
      postgres_query
        POST "INSERT INTO {table_name} {select_args} VALUES{prefixed_select_args} RETURNING *";
      postgres_rewrite  POST changes 201;
    }

    location ~ /{table_name}/(?<id>\d+) {
      postgres_pass database;
      rds_json  on;
      # TODO determine if id is the actual default id name # do the primary key check info I dumped...
      postgres_escape $escaped_id $id;
      postgres_query    HEAD GET  "SELECT * FROM {table_name} WHERE id=$escaped_id";
      postgres_rewrite  HEAD GET  no_rows 410;

      {escape_select_args}
      
      postgres_query
        PUT "UPDATE articles SET {update_args} WHERE id=$escaped_id RETURNING *";
      postgres_rewrite  PUT no_changes 410;

      postgres_query    DELETE  "DELETE FROM {table_name} WHERE id=$escaped_id";
      postgres_rewrite  DELETE  no_changes 410;
      postgres_rewrite  DELETE  changes 204;
    }
  }
}
"""

import sys
import sqlparse


def format_template(_table_name, column_names):
	_escape_select_args = '\n'.join([ 'postgres_escape ${name} $arg_{name};'.format(name=c) for c in column_names ])
	_select_args = '(%s)' % ', '.join(column_names)
        _prefixed_select_args = '(%s)' % ', '.join([ '$' + c for c in column_names ])
        _update_args = ', '.join([ "{name}=${name}".format(name=c) for c in column_names ])
	instance = template.format(table_name=_table_name, escape_select_args=_select_args, select_args=_select_args, prefixed_select_args=_prefixed_select_args, update_args=_update_args)
	print instance
	

def generate_nginx_conf(create_statement):
	group_token = str([ t for t in create_statement.tokens if not t.is_whitespace() and t.is_group() ][0]).split('\n')
	table_name = group_token[0]
	# skip '('
	column_dict = {}
	parsed_columns = [ column_def.strip().split(' ')[0] for column_def in group_token[2:] if not column_def == ')']
	column_names = [ c for c in parsed_columns if not c == 'CONSTRAINT' ] # TODO
	format_template(table_name, column_names)
			

def main(av):
	sql_statements = ''.join(sys.stdin.readlines())

	fsql_statements = sqlparse.format(sql_statements, keyword_case='upper')
	p = sqlparse.parse(fsql_statements)
	for t in p:
		if str(t.get_type()) == 'CREATE':
			generate_nginx_conf(t)

if __name__ == '__main__':
	from sys import argv as av
	main(av)
