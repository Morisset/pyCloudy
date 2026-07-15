import os
import sys
import subprocess
import numpy as np
from getpass import getpass
import pyCloudy as pc
from pyCloudy.utils.init import LIST_ELEM
from pyCloudy.utils.logging import my_logging
if pc.config.INSTALLED['pandas']:
    import pandas as pd
if pc.config.INSTALLED['sqlalchemy']:
    import sqlalchemy
    from sqlalchemy import create_engine, text, inspect as sqla_inspect, MetaData, Table
    from sqlalchemy.engine import URL
from io import StringIO

def _sql2numpy(sqltype):
    sqltype = sqltype.lower()
    if sqltype == 'float':
        return 'f4'
    if sqltype[:6] == 'double' or sqltype == 'real':
        return 'f8'
    if sqltype[:7] == 'tinyint':
        return 'i1'
    if sqltype[:5] == 'short' or sqltype[:4] == 'int2' or sqltype[:8] == 'smallint':
        return 'i2'
    if sqltype[:4] == 'int(' or sqltype[:4] == 'int4' or sqltype[:7] == 'integer' or sqltype == 'int':
        return 'i4'
    if sqltype[:4] == 'int8' or sqltype[:6] == 'bigint' or sqltype[:4] == 'long':
        return 'i8'
    if sqltype[:7] == 'varchar':
        return 'S{0}'.format(sqltype.split('(')[1].split(')')[0])
    if sqltype[:8] == 'datetime':
        return 'S20'
    return 'S50'

class MdB(object):

    MdBlog_ = my_logging()

    def __init__(self, OVN_dic = None, base_name = 'OVN',tmp_base_name = 'OVN_tmp',
                 user_name = 'OVN_user', user_passwd = 'getenv',
                 host = 'localhost', unix_socket = '/var/mysql/mysql.sock', port = 3306,
                 connect = True, master_table='tab'):
        """
        This is the package to deal with the MySQL/MariaDB OVN database.
        It is built on SQLAlchemy Core; the actual DBAPI driver is selected with
        pc.config.db_connector ('PyMySQL' or 'MySQL' for mysqlclient).
        """

        self.log_ = self.__class__.MdBlog_
        self.calling = 'MdB'
        if not pc.config.INSTALLED['sqlalchemy']:
            self.log_.error('SQLAlchemy is needed to connect to the database. Install it with e.g. "pip install sqlalchemy"',
                            calling='MdB')
        if pc.config.db_connector == 'MySQL' and pc.config.INSTALLED['MySQL']:
            self.drivername = 'mysql+mysqldb'
        elif pc.config.db_connector == 'PyMySQL' and pc.config.INSTALLED['PyMySQL']:
            self.drivername = 'mysql+pymysql'
        else:
            self.log_.error('No SQL connector available', calling='MdB')
        if OVN_dic is not None:
            if 'base_name' in OVN_dic:
                base_name = OVN_dic['base_name']
            if 'tmp_base_name' in OVN_dic:
                tmp_base_name = OVN_dic['tmp_base_name']
            if 'user_name' in OVN_dic:
                user_name = OVN_dic['user_name']
            if 'user_passwd' in OVN_dic:
                user_passwd = OVN_dic['user_passwd']
            if 'host' in OVN_dic:
                host = OVN_dic['host']
            if 'unix_socket' in OVN_dic:
                unix_socket = OVN_dic['unix_socket']
            if 'port' in OVN_dic:
                port = OVN_dic['port']
            if 'master_table' in OVN_dic:
                master_table = OVN_dic['master_table']
        else:
            OVN_dic = {'base_name': base_name,
                       'tmp_base_name': tmp_base_name,
                       'user_name': user_name,
                       'user_passwd': user_passwd,
                       'host': host,
                       'unix_socket': unix_socket,
                       'port': port,
                       'master_table': master_table}
        self.OVN_dic = OVN_dic
        self.base_name = base_name
        self.tmp_base_name = tmp_base_name
        self.user_name = user_name
        if user_passwd == 'getenv':
            self.user_passwd = os.getenv('{0}_pass'.format(user_name))
        elif user_passwd == 'getit':
            self.user_passwd = getpass()
        else:
            self.user_passwd = user_passwd
        self.port = port
        self.host = host
        self.unix_socket = unix_socket
        self.table = master_table
        self._engine = None
        self._conn = None
        self._fields_cache = {}
        self._cols_cache = {}
        self._table_cache = {}
        self._metadata = None
        self.last_rowid = None
        self.connected = False
        if connect:
            self.connect_dB()

    def __del__(self):
        if self.connected:
            self.close_dB()

    def connect_dB(self):
        if self.connected:
            self.log_.warn('Already connected', calling = self.calling)
            return None
        try:
            url = URL.create(drivername = self.drivername,
                             username = self.user_name,
                             password = self.user_passwd,
                             host = self.host,
                             port = self.port,
                             database = self.base_name)
            # pool_pre_ping revalidates connections so that long Cloudy runs do not
            # die on "MySQL server has gone away"
            self._engine = create_engine(url, pool_pre_ping=True, pool_recycle=3600)
            self._conn = self._engine.connect()
            self._metadata = MetaData()
            self.connected = True
            self.log_.message('Connected to {0}'.format(self.host), calling = self.calling)
        except Exception as ex:
            self.log_.warn('Connection to {0} failed with error <{1}>'.format(self.host, ex), calling = self.calling)

    def use_engine(self, engine):
        """
        Connect this MdB through an already-built SQLAlchemy engine
        (used for tests, e.g. with an in-memory SQLite engine).
        """
        self._engine = engine
        self._conn = engine.connect()
        self._metadata = MetaData()
        self.connected = True

    def use_dB(self, base_name = None):
        if not self.connected:
            pc.log_.error('Not connected to the server')
            return None
        if base_name is None:
            base_name = self.base_name
        self._conn.exec_driver_sql('USE {0}'.format(base_name))

    def use_dB_tmp(self, tmp_base_name = None):
        if not self.connected:
            pc.log_.error('Not connected to the server')
            return None
        if tmp_base_name is None:
            tmp_base_name = self.tmp_base_name
        self._conn.exec_driver_sql('USE {0}'.format(tmp_base_name))

    def show_tables(self):
        print(self.exec_dB('show tables'))

    def share_dB_cursor(self, m):
        self._engine = m._engine
        self._conn = m._conn
        self._metadata = m._metadata

    def close_dB(self):
        if self.connected:
            try:
                self._conn.close()
                self._engine.dispose()
            except Exception as ex:
                self.log_.warn('Error while disconnecting: <{0}>'.format(ex), calling = self.calling)
            self.connected = False
            self.log_.message('Disconnected', calling = self.calling)
        else:
            self.log_.warn('Not connected', calling = self.calling)

    def exec_dB(self, command, format_ = 'dict', return_descr=False, commit=False, params=None):
        """
        Execute an SQL command and return (result, N).

        Parameters:
            - command: a raw SQL string (executed verbatim when params is None),
                       a SQL string with named binds (:name) when params is given,
                       or any SQLAlchemy executable object (e.g. Table.insert()).
            - params: dict of bound parameters, or a list of dicts to trigger
                      an executemany (bulk) execution.
            - commit: if True, commit after the execution.

        The auto-increment id generated by the last INSERT (when available) is
        stored in self.last_rowid.
        """
        if format_ not in ('dict', 'tuple', 'numpy', 'dict2', 'pandas', 'rec'):
            self.log_.error('format"{0}" not recognized'.format(format_), calling = self.calling)
        if not self.connected:
            self.log_.error('Not connected to a database', calling = self.calling)
            return None
        self.log_.message('Command sent: {0}'.format(command), calling = self.calling)
        if format_ == 'pandas':
            if pc.config.INSTALLED['pandas']:
                res = pd.read_sql(text(command) if isinstance(command, str) else command, con=self._conn)
                return res, len(res)
            else:
                pc.log_.error('pandas is not available, use another format', calling=self.calling)
        res = None
        N = 0
        try:
            if not isinstance(command, str):
                if params is None:
                    result = self._conn.execute(command)
                else:
                    result = self._conn.execute(command, params)
            elif params is None:
                result = self._conn.exec_driver_sql(command)
            else:
                result = self._conn.execute(text(command), params)
        except Exception as ex:
            try:
                self._conn.rollback()
            except Exception:
                pass
            self.log_.error('Error <{1}> on executing {0}'.format(command, ex), calling = self.calling)
            return res, N
        try:
            self.last_rowid = result.lastrowid
        except Exception:
            self.last_rowid = None
        if result.returns_rows:
            if format_[:4] == 'dict' or format_ == 'rec':
                res = [dict(r) for r in result.mappings().all()]
            else:
                res = [tuple(r) for r in result.fetchall()]
            N = len(res)
        else:
            res = ()
            N = result.rowcount
        if commit:
            try:
                self._dB_commit()
            except Exception as ex:
                self.log_.error('Error <{1}> on commiting {0}'.format(command, ex), calling = self.calling)
        if format_ == 'rec':
            res = np.rec.fromrecords([list(e.values()) for e in res], names = list(res[0].keys()))
        if return_descr:
            return res, N, result.keys()
        else:
            return res, N

    def _dB_commit(self):
        self._conn.commit()

    def commit_dB(self):
        """
        Commit the pending transaction on this connection.
        """
        if not self.connected:
            self.log_.error('Not connected to a database', calling = self.calling)
            return None
        self._dB_commit()

    def get_table(self, name, refresh=False):
        """
        Return the SQLAlchemy reflected Table object for the given table name.
        Reflection is done once per MdB instance and cached; use refresh=True to re-reflect.
        """
        if not self.connected:
            self.log_.error('Not connected to a database', calling = self.calling)
            return None
        name = name.strip()
        if refresh or name not in self._table_cache:
            self._table_cache[name] = Table(name, self._metadata, autoload_with=self._engine,
                                            extend_existing=refresh)
        return self._table_cache[name]

    def select_dB(self, select_ = '*', from_ = None, where_ = None, order_ = None, group_ = None,
                  limit_ = 1, format_ = 'dict', dtype_ = None, commit=False):
        """
        Usage:
            dd, n = mdb.select_dB(select_ = 'L_1, L_26, L_21', from_='tab',
                        where_ = 'ref like "DIG12HR_"',
                        limit_ = 100000,
                        format_='numpy')
            loglog(dd['L_26']/dd['L_1'], dd['L_21']/dd['L_1'], 'r+')
        """
        if from_ is None:
            from_ = self.table
        if isinstance(select_, (tuple, list)):
            this_select = ''
            for w in select_:
                this_select += w + ', '
            this_select = this_select[:-2]
        else:
            this_select = select_

        if isinstance(where_, (tuple, list)):
            this_where = ''
            for w in where_:
                this_where += w + ' and '
            this_where = this_where[:-5]
        else:
            this_where = where_

        if isinstance(from_, (tuple, list)):
            this_from = ''
            for w in from_:
                this_from += w + ', '
            this_from = this_from[:-2]
        else:
            this_from = from_

        req = 'SELECT {0} FROM {1} '.format(this_select, this_from)
        if where_ is not None:
            req += 'WHERE ({0}) '.format(this_where)
        if group_ is not None:
            req += 'GROUP BY {0} '.format(group_)
        if order_ is not None:
            req += 'ORDER BY {0} '.format(order_)
        if limit_ is not None:
            req += 'LIMIT {0:d}'.format(limit_)

        if format_ == 'pandas':
            if not pc.config.INSTALLED['pandas']:
                pc.log_.error('pandas not installed', calling='MdB.select_dB')
            res = pd.read_sql(text(req), con=self._conn)
            N = len(res)
        else:
            res, N = self.exec_dB(req, format_ = format_, commit=commit)
        if N == 0:
            res = None
        elif format_ == 'numpy':
            if dtype_ is None:
                dtype_ = self.get_dtype(select_ = select_, from_ = from_)
            res = np.fromiter(res, dtype_)
        elif format_ == 'dict2':
            res2 = {}
            for key in res[0]:
                res2[key] = np.array([r[key] for r in res])
            res = res2
        return res, N

    def count_dB(self, from_ = None, where_ = None, commit=False):
        if from_ is None:
            from_ = self.table
        req = 'SELECT count(*) FROM {0}'.format(from_)
        if where_ is not None:
            req += ' WHERE ({0})'.format(where_)
        res, N = self.exec_dB(req, format_='tuple', commit=commit)
        return res[0][0]

    def get_fields(self, from_ = None, refresh=False):
        """
        Return the sorted list of column names of a table (or comma-separated tables).
        The schema is only inspected once per MdB instance; use refresh=True to re-inspect.
        """
        if from_ is None:
            from_ = self.table
        froms = from_.split(',')
        if len(froms) == 1:
            key = from_.strip()
            if refresh or key not in self._fields_cache:
                fields = [col['Field'] for col in self._get_all_cols(key, refresh=refresh)]
                fields.sort()
                self._fields_cache[key] = fields
            return list(self._fields_cache[key])
        else:
            fields = []
            for this_from in froms:
                fields.extend(self.get_fields(from_ = this_from, refresh=refresh))
        return fields

    def _get_all_cols(self, table, refresh=False):
        table = table.strip()
        if refresh or table not in self._cols_cache:
            cols = sqla_inspect(self._engine).get_columns(table)
            self._cols_cache[table] = [{'Field': col['name'], 'Type': str(col['type']).lower()}
                                       for col in cols]
        return self._cols_cache[table]

    def get_cols(self, select_ = '*', from_ = None):
        if from_ is None:
            from_ = self.table
        froms = from_.split(',')

        if len(froms) == 1:
            all_cols = self._get_all_cols(from_)
            if select_ == '*':
                res = list(all_cols)
            else:
                fields = [field.strip() for field in select_.split(',')]
                res = [col for col in all_cols if col['Field'] in fields]
        else:
            res = []
            for this_from in froms:
                res += self.get_cols(select_ = select_, from_ = this_from)
        return res

    def get_dtype(self, select_ = '*', from_ = None):
        if from_ is None:
            from_ = self.table
        dtype_list = []
        if select_ == '*':
            cols = self.get_cols(select_ = select_, from_ = from_)
            for col in cols:
                name = col['Field']
                sqltype = col['Type']
                ntype = _sql2numpy(sqltype)
                if (name, ntype) not in dtype_list:
                    dtype_list.append((name, ntype))
        else:
            fields = select_.split(',')
            for field in fields:
                name = None
                if "as" in field:
                    name = field.split('as')[1].strip()
                    field = field.split('as')[0].strip()
                col = self.get_cols(select_ = field.strip(), from_ = from_)[0]
                if name is None:
                    name = col['Field']
                sqltype = col['Type']
                ntype = _sql2numpy(sqltype)
                if (name, ntype) not in dtype_list:
                    dtype_list.append((name, ntype))
        return np.dtype(dtype_list)

    def __repr__(self):
        if self.connected:
            return "<MdB connected to {0.base_name}@{0.host}>".format(self)
        else:
            return "<MdB disconnected from {0.base_name}@{0.host}>".format(self)

class MdB_subproc(object):
    """
    Alternative way, when MySQLdb not available. Still in development.
    """
    MdBlog_ = my_logging()
    def __init__(self, OVN_dic = None, base_name = 'OVN',tmp_base_name = 'OVN_tmp',
                 user_name = 'OVN_user', user_passwd = 'getenv',
                 host = 'localhost', unix_socket = '/var/mysql/mysql.sock', port = 3306,
                 connect = True, master_table=None):

        self.log_ = self.__class__.MdBlog_
        self.calling = 'MdB'
        if OVN_dic is not None:
            if 'base_name' in OVN_dic:
                base_name = OVN_dic['base_name']
            if 'tmp_base_name' in OVN_dic:
                tmp_base_name = OVN_dic['tmp_base_name']
            if 'user_name' in OVN_dic:
                user_name = OVN_dic['user_name']
            if 'user_passwd' in OVN_dic:
                user_passwd = OVN_dic['user_passwd']
            if 'host' in OVN_dic:
                host = OVN_dic['host']
            if 'unix_socket' in OVN_dic:
                unix_socket = OVN_dic['unix_socket']
            if 'port' in OVN_dic:
                port = OVN_dic['port']
            if 'master_table' in OVN_dic:
                master_table = OVN_dic['master_table']
        self.base_name = base_name
        self.tmp_base_name = tmp_base_name
        self.user_name = user_name
        if user_passwd == 'getenv':
            self.user_passwd = os.getenv('{0}_pass'.format(user_name))
        elif user_passwd == 'getit':
            self.user_passwd = getpass()
        else:
            self.user_passwd = user_passwd
        self.port = port
        self.host = host
        self.unix_socket = unix_socket
        self.table = master_table
        self._dB = None
        self._cursor = None
        self._cursor_tuple = None
        self.connected = True

    def connect_dB(self):
        pass

    def close_dB(self):
        pass

    def exec_dB(self, command, outfile=None):
        if not self.connected:
            self.log_.error('Not connected to a database', calling = self.calling)
            return None
        self.log_.message('Command sent: {0}'.format(command), calling = self.calling)

        if outfile is None:
            stdout=subprocess.PIPE
        else:
            stdout=file(outfile, 'w')
        proc = subprocess.Popen(["mysql",
                                 "--host={0}".format(self.host),
                                 "--user={0}".format(self.user_name),
                                 "--password={0}".format(self.user_passwd),
                                 "--port={0}".format(self.port),
                                 "{0}".format(self.base_name)],
                                stdin=subprocess.PIPE,
                                stdout=stdout)
        out, err = proc.communicate(command)
        if outfile is not None:
            stdout.close()
        try:
            N = len(out)
        except:
            N = None
        return out, N

    def select_dB(self, select_ = '*', from_ = None, where_ = None, order_ = None, group_ = None, limit_ = 1,
                  format_ = 'dict2', dtype_ = None, outfile=None):
        """
        Usage:
            dd, n = mdb.select_dB(select_ = 'L_1, L_26, L_21', from_='tab,'
                        where_ = 'ref like "DIG12HR_"',
                        limit_ = 100000,
                        format_='numpy')
            loglog(dd['L_26']/dd['L_1'], dd['L_21']/dd['L_1'], 'r+')
        """
        if from_ is None:
            from_ = self.table
        req = 'SELECT {0} FROM {1} '.format(select_, from_)
        if where_ is not None:
            req += 'WHERE ({0}) '.format(where_)
        if order_ is not None:
            req += 'ORDER BY {0} '.format(order_)
        if group_ is not None:
            req += 'GROUP BY {0} '.format(group_)
        if limit_ is not None:
            req += 'LIMIT {0:d}'.format(limit_)
        res_tmp, N = self.exec_dB(req, outfile=outfile)

        if N == 0 or N is None:
            res = None
        else:
            res = np.genfromtxt(StringIO(res_tmp[0]), names=True, delimiter='\\t')
            N = len(res)
        """
        if format_ in ('dict', 'dict2'):
            res = {}
            resnp = np.array(res_tmp[1:-1])
            for i, key in enumerate(res_tmp[0]):
                try:
                    res[key] = np.array(resnp[:,i], dtype='float')
                except:
                    res[key] = resnp[:,i]
        """
        if outfile is not None:
            return res, N



