import psycopg2
import os
import sys

from .cloud           import Cloud
from .network_service import NetworkService


class DB:
    def __init__(self, user_id: str = None, _conn = None):
        self.user_id = user_id
        
        if self.user_id == None:
            self.user_id = 'db'

        if _conn != None:
            #print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Using a previously established connection")
            self.__database = _conn
        else:
            self.pghost  = os.getenv('OD_USE_PG_HOST')
            if self.pghost:
                try:
                    self.__database = psycopg2.connect(
                        host=self.pghost,
                        database=mk_db_name(self.user_id),
                        user=mk_user_name(self.user_id),
                        password=self.user_id,
                        connect_timeout=3)
                    self.__upgrade_database_schema()
                    #print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Connected to existent database: {mk_db_name(self.user_id)}")
                except psycopg2.Error as e:
                    print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] DB error: {e}")
                    if e != 'timeout expired':
                        print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Database {mk_db_name(self.user_id)} not exist, try create")
                        self.__create_database_user()
                        self.__create_database()
                        self.__database = psycopg2.connect(
                            host=self.pghost,
                            database=mk_db_name(self.user_id),
                            user=mk_user_name(self.user_id),
                            password=self.user_id,
                            connect_timeout=3)
                        print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Connected to new database: {mk_db_name(self.user_id)}")
                        self.__create_database_schema()
            else:
                print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Error: Database host (OD_USE_PG_HOST) not set")
                raise Exception("Error: Database host (OD_USE_PG_HOST) not set")


    def __create_database_user(self):
        dbpass = os.getenv('OD_PG_SU_PASS')
        if dbpass == None:
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Error: Postgres user password (OD_PG_SU_PASS) not set")
            raise Exception("Error: Postgres user password (OD_PG_SU_PASS) not set")
        try:
            db = psycopg2.connect(
                host=self.pghost,
                database='template1',
                user='postgres',
                password=dbpass,
                connect_timeout=3)
            #print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Connected to 'template1' database as user 'postgres'")
            with db.cursor() as cursor:
                sql = f"create user {mk_user_name(self.user_id)} CREATEDB PASSWORD '{self.user_id}';"
                cursor.execute(sql)
            db.commit()
            db.close()
        except psycopg2.Error as e:
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] DB error: {e}")
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Error create database owner user: {mk_user_name(self.user_id)}")
            raise Exception(f"Error create new database owner {mk_user_name(self.user_id)}")
        return

    def __create_database(self):
        if self.pghost == None:
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Error: Database host (OD_USE_PG_HOST) not set")
            raise Exception("Error: Database host (OD_USE_PG_HOST) not set")
        try:
            db = psycopg2.connect(
                host=self.pghost,
                database='template1',
                user=mk_user_name(self.user_id),
                password=self.user_id,
                connect_timeout=3)
            #print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Connected to 'template1' database as user '{mk_user_name(self.user_id)}'")
            db.autocommit = True
            with db.cursor() as cursor:
                sql = f"create database {mk_db_name(self.user_id)};"
                cursor.execute(sql)
            db.close()
        except psycopg2.Error as e:
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] DB error: {e}")
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Error create new database: {mk_db_name(self.user_id)}")
            raise Exception(f"Error create new database: {mk_db_name(self.user_id)}")
        return

    def __create_database_schema(self):
        try:
            with self.__database.cursor() as cursor:
                cursor.execute('''CREATE TABLE IF NOT EXISTS clouds
                    (
                        id   serial PRIMARY KEY,
                        name TEXT UNIQUE not null, -- Cloud name (show in gui)
                        cloud_type TEXT not null,  -- AWS or AZURE
                        aws_region TEXT,     -- AWS region
                        aws_key TEXT,        -- AWS key
                        aws_secret_key TEXT, -- AWS secret-key
                        azure_tenant_id TEXT,      -- Azure tenant-id
                        azure_client_id TEXT,      -- Azure client-id
                        azure_client_secret TEXT,  -- Azure client-secret
                        azure_subscription_id TEXT, -- Azure only subscription-id
                        sync_state integer not null default 0, -- 0 - synced, 1 - in sync
                        sync_start timestamptz, -- write current_timestamp on sync start
                        sync_stop  timestamptz, -- write current_timestamp on sync complite
                        sync_msg  text,         -- error messge or null
                        last_successful_sync timestamptz -- actual cloud state date
                    )''')
                cursor.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS clouds_test_unique_aws_index ON clouds(aws_region, aws_key, aws_secret_key)")
                cursor.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS clouds_test_unique_azure_index ON clouds(azure_tenant_id, azure_client_id, azure_client_secret, azure_subscription_id)")
                
                cursor.execute('''
                    CREATE or replace FUNCTION on_sync_tg_function() RETURNS trigger AS $on_sync_tg_function$
                        BEGIN
                            IF NEW.sync_state = 1 THEN
                                IF OLD.sync_state = 1 THEN
                                    IF EXTRACT(epoch from current_timestamp-OLD.sync_start)::int < 960 THEN
                                        RAISE EXCEPTION 'Sync allready in progress...';
                                    ELSE
                                        RAISE NOTICE 'Dead sync found, sync restart allowed';
                                    END IF;
                                END IF;
                                NEW.sync_start := current_timestamp;
                                NEW.sync_stop := NULL;
                                NEW.sync_msg := NULL;
                            ELSE
                                IF OLD.sync_state = 1 THEN
                                    IF NEW.sync_msg is NULL THEN
                                        OLD.sync_msg := NULL;
                                        NEW.sync_stop := current_timestamp;
                                        NEW.last_successful_sync := NEW.sync_stop;
                                    ELSE
                                        NEW.sync_stop := current_timestamp;
                                    END IF;
                                END IF;
                            END IF;
                            RETURN NEW;
                        END;
                    $on_sync_tg_function$ LANGUAGE plpgsql;''')
                cursor.execute("CREATE or replace TRIGGER on_sync_tg BEFORE UPDATE ON clouds FOR EACH ROW EXECUTE FUNCTION on_sync_tg_function();")

                cursor.execute('''CREATE TABLE IF NOT EXISTS vpcs(
                    id      serial PRIMARY KEY,
                    name    TEXT UNIQUE not null,
                    network TEXT,
                    cloud_id integer REFERENCES clouds (id),
                    note    TEXT)''')
                cursor.execute("CREATE INDEX IF NOT EXISTS vpc_name_idx ON vpcs(name);")

                cursor.execute('''CREATE TABLE IF NOT EXISTS subnets(
                    id      serial PRIMARY KEY,
                    name    TEXT UNIQUE not null,
                    arn     TEXT,
                    network TEXT,
                    azone   TEXT,
                    note    TEXT,
                    vpc_id  text REFERENCES vpcs(name),
                    cloud_id integer REFERENCES clouds(id))''')
                cursor.execute("CREATE INDEX IF NOT EXISTS subnets_name_idx ON subnets(name);")

                cursor.execute('''CREATE TABLE IF NOT EXISTS nodes(
                    id        serial PRIMARY KEY,
                    type      TEXT,
                    vpc_id    text, -- REFERENCES vpcs(name),
                    azone     TEXT,
                    subnet_id text, -- REFERENCES subnets(name),
                    name      TEXT,
                    privdn    TEXT,
                    privip    TEXT,
                    pubdn     TEXT,
                    pubip     TEXT,
                    note      TEXT,
                    os        TEXT,
                    state     TEXT,
                    mac       TEXT,
                    if_id     TEXT, -- UNIQUE not null,
                    cloud_id integer REFERENCES clouds(id))''')
                cursor.execute("CREATE INDEX IF NOT EXISTS nodes_vpc_id_idx    ON nodes(vpc_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS nodes_subnet_id_idx ON nodes(subnet_id);")

                cursor.execute('''CREATE TABLE IF NOT EXISTS rule_groups(
                    id        serial PRIMARY KEY,
                    if_id     text, -- REFERENCES nodes(if_id),
                    subnet_id text, -- REFERENCES subnets(name),
                    name      TEXT,
                    type      TEXT,
                    cloud_id  integer REFERENCES clouds(id))''')
                cursor.execute("CREATE INDEX IF NOT EXISTS rule_groups_if_id_idx     ON rule_groups(if_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS rule_groups_subnet_id_idx ON rule_groups(subnet_id);")
                cursor.execute("CREATE INDEX IF NOT EXISTS rule_groups_name_idx      ON rule_groups(name);")

                cursor.execute('''CREATE TABLE IF NOT EXISTS rules(
                    id        serial PRIMARY KEY,
                    group_id  text, -- REFERENCES rule_groups(name),
                    rule_id   TEXT,
                    egress    TEXT,
                    proto     TEXT,
                    port_from TEXT,
                    port_to   TEXT,
                    naddr     TEXT,
                    cloud_id  integer REFERENCES clouds(id),
                    ports     TEXT,
                    action    TEXT,
                    priority  INTEGER)''')
                cursor.execute("CREATE INDEX IF NOT EXISTS rules_group_id_idx ON rules(group_id);")

                cursor.execute('''CREATE TABLE IF NOT EXISTS network_services(
                    id    serial PRIMARY KEY,
                    name  TEXT,
                    proto TEXT,
                    port  TEXT)''')
                self.__import_network_services()
                cursor.execute("CREATE INDEX IF NOT EXISTS network_services_name_idx  ON network_services(name);")
                cursor.execute("CREATE INDEX IF NOT EXISTS network_services_proto_idx ON network_services(proto);")
                cursor.execute("CREATE INDEX IF NOT EXISTS network_services_port_idx  ON network_services(port);")

                cursor.execute('''CREATE TABLE IF NOT EXISTS s3_buckets(
                    id        serial PRIMARY KEY,
                    name      TEXT,
                    public_access_block_enabled TEXT,
                    acl_enabled                 TEXT,
                    cloud_id  integer REFERENCES clouds(id));''')
                self.__database.commit()

                # Not used now
                # cursor.execute('''CREATE TABLE IF NOT EXISTS routes(
                #    id        serial PRIMARY KEY,
                #    cloud_id  integer REFERENCES clouds(id),
                #    vpc_id    integer REFERENCES vpcs(id),
                #    subnet_id integer REFERENCES subnets(id),
                #    route   TEXT,
                #    note    TEXT,
                #    naddr   TEXT,
                #    gw      TEXT)''')
        except psycopg2.Error as e:
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] DB error: {e}")
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Error create new database schema: {mk_db_name(self.user_id)}")
            raise Exception(f"Error create new database schema: {self.dbname}")
        except:
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Unknown error while create new database schema: {mk_db_name(self.user_id)}")
            raise Exception(f"Unknown error while create new database schema: {mk_db_name(self.user_id)}")
    

    def __upgrade_database_schema(self):
        try:
            with self.__database.cursor() as cursor:
                # Check new column at s3_buckets table
                try:
                    cursor.execute('select public_access_block_enabled, acl_enabled from s3_buckets where cloud_id = 0')
                except psycopg2.Error as e:
                    print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] DB error: '{e}' - s3_buckets Need Upgrade")
                    self.__database.rollback()
                    cursor.execute("alter table s3_buckets add column IF NOT EXISTS public_access_block_enabled TEXT;")
                    cursor.execute("alter table s3_buckets add column IF NOT EXISTS acl_enabled TEXT;")
                    print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] s3_buckets - Upgrade Complete")
            self.__database.commit()
        except psycopg2.Error as e:
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] DB error: {e}")
        except:
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Unknown error while upgrade database schema")


    def add_cloud(self, cloud: Cloud) -> int:
        with self.__database.cursor() as cursor:
            try:
                if cloud.cloud_type == 'AWS':
                    cursor.execute("""
                        INSERT INTO clouds (name, cloud_type, aws_region, aws_key, aws_secret_key)
                        VALUES (%s, %s, %s, %s, %s) RETURNING id;
                        """,
                        (cloud.name, cloud.cloud_type, cloud.aws_region, cloud.aws_key, cloud.aws_secret_key))
                    cloud.id = cursor.fetchone()[0]
                    self.__database.commit()
                elif cloud.cloud_type == 'AZURE':
                    cursor.execute("""
                        INSERT INTO clouds (name, cloud_type, azure_tenant_id, azure_client_id, azure_client_secret, azure_subscription_id)
                        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
                    """, (cloud.name, cloud.cloud_type, cloud.azure_tenant_id, cloud.azure_client_id, cloud.azure_client_secret, cloud.azure_subscription_id))
                    cloud.id = cursor.fetchone()[0]
                    self.__database.commit()
                else:
                    print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Unsupported Cloud Type: '{cloud.cloud_type}'")
            except psycopg2.Error as e:
                print(f"DB error: {e}")
        return cloud.id

    def delete_cloud(self, cloud_id):
        with self.__database.cursor() as cursor:
            self.sync_cloud(cloud_id)
            sql = f"DELETE FROM clouds WHERE id = {cloud_id}"
            cursor.execute(sql)
            self.__database.commit()
        return

    def sync_cloud(self, cloud_id: int):
        with self.__database.cursor() as cursor:
            sql = f"DELETE FROM rules WHERE cloud_id = {cloud_id}"
            cursor.execute(sql)
            sql = f"DELETE FROM rule_groups WHERE cloud_id = {cloud_id}"
            cursor.execute(sql)
            sql = f"DELETE FROM subnets WHERE cloud_id = {cloud_id}"
            cursor.execute(sql)
            sql = f"DELETE FROM nodes WHERE cloud_id = {cloud_id}"
            cursor.execute(sql)
            sql = f"DELETE FROM vpcs WHERE cloud_id = {cloud_id}"
            cursor.execute(sql)
            sql = f"DELETE FROM s3_buckets WHERE cloud_id = {cloud_id}"
            cursor.execute(sql)
            self.__database.commit()
        return

    def delete_group_rules(self, cloud_id: str, group_id: str):
        with self.__database.cursor() as cursor:
            sql = f"DELETE FROM rules WHERE cloud_id = {cloud_id} and group_id = '{group_id}'"
            cursor.execute(sql)
            self.__database.commit()
        return

    def get_clouds(self) -> list[Cloud]:
        with self.__database.cursor() as cursor:
            cursor.execute("""
                SELECT id, name, cloud_type,
                    aws_region, aws_key, aws_secret_key, 
                    azure_tenant_id, azure_client_id, azure_client_secret, azure_subscription_id,
                    case when sync_state=0 then 0 else case when EXTRACT(epoch from current_timestamp-sync_start)::int > 960 then 0 else 1 end end as sync_state,
                    case when sync_start is null then null else sync_start::text end as sync_start,
                    case when sync_stop is null then (case when EXTRACT(epoch from current_timestamp-sync_start)::int > 960 then (sync_start+interval '960 second')::text else null end) else sync_stop::text end as sync_stop,
                    case when sync_state=0 then sync_msg else (case when EXTRACT(epoch from current_timestamp-sync_start)::int > 960 then 'Error: dead sync job' else sync_msg end) end as sync_msg,
                    case when last_successful_sync is null then null else last_successful_sync::text end as last_successful_sync
                FROM clouds ORDER by name
            """)
            rows = cursor.fetchall()
        return [
            Cloud(id=r[0],
                  name=r[1],
                  cloud_type=r[2],
                  aws_region=r[3],
                  aws_key=r[4],
                  aws_secret_key=r[5],
                  azure_tenant_id=r[6],
                  azure_client_id=r[7],
                  azure_client_secret=r[8],
                  azure_subscription_id=r[9],
                  sync_state=r[10],
                  sync_start=r[11],
                  sync_stop=r[12],
                  synk_msg=r[13],
                  last_successful_sync=r[14]) for r in rows
        ]

    def get_clouds_short(self) -> list[Cloud]:
        with self.__database.cursor() as cursor:
            cursor.execute(
                """SELECT id, name, cloud_type FROM clouds ORDER by name""")
            return cursor.fetchall()

    def get_vms_info(self, subnet_id: str) -> list[str]:
        sql = f"SELECT id, type, vpc_id, azone, subnet_id, name, privdn, privip, pubdn, pubip, note, os, state, mac, if_id, cloud_id FROM nodes WHERE type = 'VM' and subnet_id = '{subnet_id}' order by note"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_all_nodes_info(self) -> list[list[str]]:
        sql = f"SELECT id, type, vpc_id, azone, subnet_id, name, privdn, privip, pubdn, pubip, note, os, state, mac, if_id, cloud_id FROM nodes order by note"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_subnets_info(self, vpc_id: str) -> list[str]:
        sql = f"SELECT id, name, arn, network, azone, note, vpc_id, cloud_id FROM subnets WHERE vpc_id = '{vpc_id}' order by note"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_vpcs_info(self) -> list[str]:
        sql = f"SELECT vpcs.id, vpcs.name, vpcs.network, (clouds.name || ' | ' || vpcs.note) cv, cloud_id, note FROM vpcs, clouds where vpcs.cloud_id=clouds.id order by cv"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_internet_nodes(self) -> list[str]:
        sql = "select \
                   distinct naddr \
               from rules \
               where \
                   naddr is not null and \
                   naddr not in (select distinct (pubip||'/32')  from nodes where type = 'VM' and pubip is not null) and \
                   naddr not in (SELECT distinct (privip||'/32') FROM nodes WHERE type = 'VM' and privip is not NULL) and \
                   naddr not in (select distinct (pubip)         from nodes where type = 'VM' and pubip is not null) and \
                   naddr not in (SELECT distinct (privip) FROM nodes        WHERE type = 'VM' and privip is not NULL) and \
                   naddr not in (select network from vpcs) and \
                   naddr not in (select network from subnets) \
                order by naddr"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_networks(self) -> list[str]:
        sql = "SELECT \
                distinct naddr \
               FROM \
                rules \
               WHERE \
                naddr is not null and \
                naddr not in (SELECT distinct (privip||'/32') FROM nodes        WHERE type = 'VM' and privip is not NULL) and \
                naddr not in (SELECT distinct (pubip||'/32')  FROM nodes        WHERE type = 'VM' and pubip is not null)  and \
                naddr not in (SELECT distinct (privip)        FROM nodes        WHERE type = 'VM' and privip is not NULL) and \
                naddr not in (SELECT distinct (pubip)         FROM nodes        WHERE type = 'VM' and pubip is not null)  and \
                naddr not in (SELECT network                  FROM vpcs)                                                  and \
                naddr not in (SELECT network                  FROM subnets)"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return [f"'{r[0]}'" for r in cursor.fetchall()]

    def get_vms(self) -> list[str]:
        sql = "select privip from nodes where type = 'VM' union select pubip from nodes where type = 'VM' and pubip is not null"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return [r[0] for r in cursor.fetchall()]

    def get_subnets(self) -> list[str]:
        sql = "select network from subnets"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return [r[0] for r in cursor.fetchall()]

    def get_vpcs(self) -> list[str]:
        sql = "select network from vpcs"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return [r[0] for r in cursor.fetchall()]

    def get_link_networks(self, id) -> list[str]:
        nets = f"({', '.join(self.get_networks())})"
        sql = f"SELECT \
                    n.id, r.egress, r.proto, r.naddr, r.ports \
                FROM \
                    nodes n, rule_groups g, rules r \
                WHERE \
                    n.type = 'VM' and \
                    n.id = {id} and \
                    r.group_id = g.name and \
                    g.if_id = n.if_id and \
                    r.naddr in {nets} \
                ORDER by r.naddr"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_link_vpcs(self, id) -> list[int]:
        sql = f"SELECT \
                    v.id, r.egress, r.proto, r.naddr, r.ports \
                FROM \
                    nodes n, rules r, rule_groups g, vpcs v \
                WHERE \
                    n.type = 'VM' and \
                    n.id = {id} and \
                    r.group_id = g.name and \
                    g.if_id = n.if_id and \
                    r.naddr = v.network \
                ORDER \
                    by r.naddr"
        with self.__database.cursor() as cursor:
            try:
                cursor.execute(sql)
            except psycopg2.Error as e:
                print(f"DB error: {e}")
            return cursor.fetchall()

    def get_link_subnets(self, id) -> list[int]:
        sql = f"SELECT  s.id, r.egress, r.proto, r.naddr, r.ports FROM nodes n, rules r, rule_groups g, subnets s \
                WHERE n.type = 'VM' and n.id = {id} and r.group_id = g.name and g.if_id = n.if_id and r.naddr = s.network \
                ORDER by r.naddr"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_link_vms(self, id) -> list[int]:
        sql = f"select * from (SELECT \
                    nip.id, r.egress, r.proto, r.naddr, r.ports \
                FROM \
                    nodes n, rules r, rule_groups g, nodes nip \
                WHERE \
                    nip.type = 'VM' and \
                    n.type = 'VM' and \
                    n.id = {id} and \
                    r.group_id = g.name and \
                    g.if_id = n.if_id and \
                    r.naddr = nip.privip||'/32' \
                UNION \
                SELECT \
                    nip.id, r.egress, r.proto, r.naddr, r.ports \
                FROM \
                    nodes n, rules r, rule_groups g, nodes nip \
                WHERE \
                    nip.type = 'VM' and \
                    n.type = 'VM' and \
                    n.id = {id} and \
                    r.group_id = g.name and \
                    g.if_id = n.if_id and \
                    nip.pubip is not null and \
                    nip.pubip != '' and \
                    r.naddr = nip.pubip||'/32') as unsurted_rezult \
                ORDER by naddr"
        with self.__database.cursor() as cursor:
            try:
                cursor.execute(sql)
            except psycopg2.Error as e:
                print(f"DB error: {e}")
            return cursor.fetchall()

    def get_cloud_vm_info(self, vm_id: str) -> list[str]:
        sql = f"select c.cloud_type, g.name, c.id from clouds c, nodes n, rule_groups g where g.if_id = n.if_id and n.cloud_id = c.id and n.id = {vm_id}"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_aws_credentials(self, cloud_id: str) -> list[str]:
        sql = f"SELECT aws_region, aws_key, aws_secret_key FROM clouds WHERE id = {cloud_id} and cloud_type = 'AWS';"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_azure_credentials(self, cloud_id: str) -> list[str]:
        sql = f"SELECT azure_tenant_id, azure_client_id, azure_client_secret, azure_subscription_id FROM clouds WHERE id = {cloud_id} and cloud_type = 'AZURE'"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def add_vpc(self, vpc: dict) -> int:
        sql = f"INSERT INTO vpcs (name, network, cloud_id, note) VALUES ('{vpc['name']}', '{vpc['network']}', {vpc['cloud_id']}, '{vpc['note']}')"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            self.__database.commit()
        return cursor.lastrowid

    def add_subnet(self, subnet: dict) -> int:
        sql = f"INSERT INTO subnets (name, arn, network, azone, note, vpc_id, cloud_id) \
                    VALUES ('{subnet['name']}', '{subnet['arn']}', '{subnet['network']}', \
                        '{subnet['azone']}', '{subnet['note']}', '{subnet['vpc_id']}', {subnet['cloud_id']})"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            self.__database.commit()
        return cursor.lastrowid

    def add_instance(self, instance: dict) -> int:
        ret:int = -1
        with self.__database.cursor() as cursor:
            cursor.execute("""
                INSERT INTO nodes (type, vpc_id, azone, subnet_id, name, privdn, privip, pubdn, pubip, note, os, state, mac, if_id, cloud_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)  RETURNING id;
                """,
                        (instance['type'], instance['vpc_id'], instance['azone'], instance['subnet_id'], instance['name'],
                            instance['privdn'], instance['privip'], instance['pubdn'], instance['pubip'], instance['note'],
                            instance['os'], instance['state'], instance['mac'], instance['if_id'], instance['cloud_id']))
            ret = cursor.fetchone()[0]
            self.__database.commit()
        return ret

    def add_rule_group(self, rule_group: dict) -> int:
        sql:str = ''
        if rule_group['if_id'] == '':
            sql = f"INSERT INTO rule_groups (name, type, cloud_id, subnet_id) \
            VALUES ('{rule_group['name']}', '{rule_group['type']}', {rule_group['cloud_id']}, '{rule_group['subnet_id']}')"
        else:
            sql = f"INSERT INTO rule_groups (if_id, name, type, cloud_id, subnet_id) \
            VALUES ('{rule_group['if_id']}', '{rule_group['name']}', '{rule_group['type']}', {rule_group['cloud_id']}, '{rule_group['subnet_id']}')"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            self.__database.commit()
        return cursor.lastrowid

    def add_rule(self, rule: dict) -> int:
        sql = f"INSERT INTO rules (group_id, rule_id, egress, proto, port_from, port_to, naddr, cloud_id, ports, action, priority)\
                   VALUES ('{rule['group_id']}', '{rule['rule_id']}', '{rule['egress']}',\
                           '{rule['proto']}', '{rule['port_from']}', '{rule['port_to']}',\
                           '{rule['naddr']}', {rule['cloud_id']}, '{rule['ports']}', '{rule['action']}', {rule['priority']})"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            self.__database.commit()
        return cursor.lastrowid

    def get_vm_rules(self, vm_id: int) -> list[str]:
        sql = f"select r.* from rules r, rule_groups rg, nodes n where r.group_id = rg.name and rg.if_id = n.if_id and n.id = {vm_id} order by r.id"
        with self.__database.cursor() as cursor:
            try:
                cursor.execute(sql)
            except psycopg2.Error as e:
                print(f"DB error: {e}")
            return cursor.fetchall()

    def detect_service(self, proto, port_from, port_to):
        ret: str = ''
        sql: str = f"select trim(name) as name from network_services where trim(proto)='{proto.lower().strip()}' and port='{port_from}'"
        if (port_from) == '*' or (port_from == '0'):
            pass
        else:
            if (port_to == '') or (port_from == port_to):
                with self.__database.cursor() as cursor:
                    cursor.execute(sql)
                    for row in cursor.fetchall():
                        ret = row[0]  # .upper()
                        break
        return ret

    def get_service_names(self) -> list[str]:
        sql = f"select distinct trim(name) as name from network_services where trim(proto) in ('tcp', 'udp', 'icmp')  order by name"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
        return [row[0] for row in cursor.fetchall()]

    def get_all_rule_groups(self) -> list[str]:
        sql = f"select id, if_id, subnet_id, name, type, cloud_id from rule_groups"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_all_rules(self) -> list[str]:
        sql = f"select id,group_id,rule_id,egress,proto,port_from,port_to,naddr,cloud_id,ports,action,priority from rules"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_services_by_name(self, name) -> list[NetworkService]:
        sql = f"select distinct id, name, proto, port from network_services where trim(name)='{name.strip()}' order by name"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return [NetworkService(id=row[0],
                                name=row[1].replace('\t', ' ').strip(),
                                proto=row[2].replace('\t', ' ').strip(),
                                port=row[3].replace('\t', ' ').strip())
                    for row in cursor.fetchall()]

    def __import_network_services(self):
        sql = f"select count(*) from network_services"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            row_count = cursor.fetchall()
            if row_count[0][0] == 0:
                sql = f"insert into network_services(name, proto, port) values('http', 'tcp', '80')"
                sql = f"insert into network_services(name, proto, port) values('https', 'tcp', '443')"
                sql = f"insert into network_services(name, proto, port) values('smtp', 'tcp', '25')"
                sql = f"insert into network_services(name, proto, port) values('postgresql', 'tcp', '5432')"
                sql = f"insert into network_services(name, proto, port) values('dns', 'udp', '54')"
                cursor.execute(sql)
                self.__database.commit()
        return

    def add_s3_bucket(self, bucket: dict) -> int:
        sql = f"INSERT INTO s3_buckets(name, cloud_id, public_access_block_enabled, acl_enabled) \
            VALUES ('{bucket['name']}', {bucket['cloud_id']}, '{bucket['public_access_block_enabled']}', '{bucket['acl_enabled']}')"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            self.__database.commit()
        return cursor.lastrowid

    def get_s3_buckets(self, cloud_id: int) -> list[str]:
        sql = f"select id, name, cloud_id, public_access_block_enabled, acl_enabled from s3_buckets where cloud_id = {cloud_id} order by name"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def get_asg_nodes(self, asg_id: str, cloud_id: int) -> list[str]:
        sql = f"select distinct n.privip from nodes n, rule_groups g where n.cloud_id={cloud_id} and n.type='VM' and g.type='ASG' and g.name='{asg_id}' and n.privip is not null and n.privip != '' and n.if_id=g.if_id union select distinct n.pubip from nodes n, rule_groups g where n.cloud_id={cloud_id} and n.type='VM' and g.type='ASG' and g.name='{asg_id}' and n.pubip is not null and n.pubip !='' and n.if_id = g.if_id"
        with self.__database.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def lock_sync_cloud(self, cloud_id):
        status:int = 0
        msg:str    = None
        try:
            with self.__database.cursor() as cursor:
                sql = f"update clouds set sync_state=1 where id = {cloud_id}"
                cursor.execute(sql)
                self.__database.commit()
        except psycopg2.Error as e:
            print(f"DB error: {e}")
            status = 1
            msg = e
        return status, msg

    def unlock_sync_cloud(self, cloud_id, msg:str = None):
        status:int = 0
        msg:str    = None
        sql:str    = None
        try:
            with self.__database.cursor() as cursor:
                if msg == None:
                    sql = f"update clouds set sync_state=0 where id = {cloud_id}"
                else:
                    sql = f"update clouds set sync_state=0, last_successful_sync={msg} where id = {cloud_id}"
                cursor.execute(sql)
                self.__database.commit()
        except psycopg2.Error as e:
            print(f"DB error: {e}")
            status = 1
            msg = e
        return status, msg

def mk_user_name(_userid: str = None):
    ret = _userid
    if ret == None:
        ret = 'db'
    else:
        ret = f"u{_userid.replace('-', '')}"
    return ret

def mk_db_name(user_id: str = None):
    return mk_user_name(user_id)

def db_exist(_userid: str = None):
    ret:bool = False
    db       = None
    userid:str = _userid
    if userid == None:
        userid = 'db'
    pghost = os.getenv('OD_USE_PG_HOST')
    if pghost:
        try:
            db = psycopg2.connect(
                host=pghost,
                database=mk_db_name(userid),
                user=mk_user_name(userid),
                password=userid,
                connect_timeout=3)
            #print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Connected to existent database")
            ret = True
        except psycopg2.Error as e:
            db = None
            print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] DB error: {e}")
    else:
        print(f"[{__file__}:{sys._getframe().f_code.co_name}:{sys._getframe().f_lineno}] Error: Database host (OD_USE_PG_HOST) not set")
    return ret, db
