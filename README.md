# pgsql-nginx-rest-generator
Generalized nginx conf generator to facilitate a REST service from nginx.

This project relies on the sql parser heavily to generate the configuration file for the table.

This project was inspired by [this](http://rny.io/nginx/postgresql/2013/07/26/simple-api-with-nginx-and-postgresql.html) and [this](https://ef.gy/using-postgresql-with-nginx) and [ASP.NET Queryable](http://www.asp.net/web-api/overview/odata-support-in-aspnet-web-api/supporting-odata-query-options).

Dependencies
------------

* nginx
* postgresql
* openresty
* sqlparse>=0.2.0 (python)

Mac
---
If you're on a mac, download the src from the [openresty site](https://openresty.org/).

Build it with these parameters:
```bash
> ./configure --help | grep without | grep lua | sed 's/disable.*//' | xargs ./configure --with-http_postgres_module && make -j6 && make install
```
Mac compilation bug: for some reason, without disabling lua completely, the openresty build (1.7.10.2) will break on x86_64 arch. (8-8-2015)

Usage: cat sql.txt | python pgsql-nginx-rest-gen.py

postgresql on mac
-----------------
* Install homebrew
* Hit the following commands:
```bash
> brew install postgresql
> echo "alias pgstart="pg_ctl -D ~/postgresql/ -l logfile start"" >>  ~/.bash_aliases
> mkdir -p ~/postgresql
> initdb ~/postgresql
```
* Try running it with the alias `pgstart`
