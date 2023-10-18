######################################################
# By deafult use sqlite3 for user data store
# set OD_USE_PG_HOST env for use postgresql database
# example:
# export OD_USE_PG_HOST=pghost.example.com
######################################################
import os
if os.getenv('OD_USE_PG_HOST'):
    from db_pgsql import DB
else:
    from db_sqlite import DB
