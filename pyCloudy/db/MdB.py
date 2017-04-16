import os
import subprocess
import numpy as np
from getpass import getpass
import pyCloudy as pc
from pyCloudy.utils.init import LIST_ELEM
from pyCloudy.utils.logging import my_logging
if pc.config.INSTALLED['pandas']:
    import pandas as pd
    import pandas.io.sql as psql
from io import StringIO   

def _sql2numpy(sqltype):
    if sqltype == 'float':
        return 'f4'
    if sqltype == 'double' or sqltype == 'real':
        return 'f8'
    if sqltype[0:7] == 'tinyint':
        return 'i1'
    if sqltype[0:5] == 'short' or sqltype[0:4] == 'int2':
        return 'i2'
    if sqltype[0:4] == 'int(' or sqltype[0:4] == 'int4':
        return 'i4'
    if sqltype[0:4] == 'int8' or sqltype[0:6] == 'bigint' or sqltype[0:4] == 'long':
        return 'i8'
    if sqltype[0:7] == 'varchar':
        return 'S{0}'.format(sqltype.split('(')[1].split(')')[0])
    if sqltype[0:8] == 'datetime':
        return 'S20'
    return 'S50'

class MdB(object):
    
    MdBlog_ = my_logging()
    
    def __init__(self, OVN_dic = None, base_name = 'OVN',tmp_base_name = 'OVN_tmp', 
                 user_name = 'OVN_user', user_passwd = 'getenv', 
                 host = 'localhost', unix_socket = '/var/mysql/mysql.sock', port = 3306,
                 connect = True, master_table='tab'):
        """
        This is the package to deal with MySQL OVN database. 
        You must have MySQL or PyMySQL library installed. The latest is easier to get working, as it comes with its own
        mysql client.
         
        Latter, we will also use the ODBC connector. Install the connector from MySQl: http://dev.mysql.com/downloads/connector/odbc/
        and then use pyodbc with:
        cnxn = pyodbc.connect('DRIVER={MySQL ODBC 5.2 Driver};SERVER=127.0.0.1;DATABASE=OVN;UID=OVN_user;PWD=oiii5007;SOCKET=/var/mysql/mysql.sock')
        
        """


        self.log_ = self.__class__.MdBlog_
        self.calling = 'MdB'
        if pc.config.db_connector =='MySQL' and pc.config.INSTALLED['MySQL']:
            import MySQLdb as SQLdb
        elif pc.config.db_connector =='PyMySQL' and pc.config.INSTALLED['PyMySQL']:
            import pymysql as SQLdb
        else:
            self.log_.error('No SQL connector available', calling='MdB')
        self.SQLdb = SQLdb
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
        elif user_passwd is 'getit':
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
            self._dB = self.SQLdb.connect(host = self.host, user = self.user_name, passwd = self.user_passwd, 
                                        db = self.base_name, port = self.port, unix_socket = self.unix_socket)
            self.connected = True
            self.log_.message('Connected to {0}'.format(self.host), calling = self.calling)
        except:
            self.log_.warn('Connection to {0} failed'.format(self.host), calling = self.calling)
        try:
            self._cursor = self._dB.cursor(self.SQLdb.cursors.DictCursor)
            self._cursor_tuple = self._dB.cursor(self.SQLdb.cursors.Cursor)
        except:
            self.log_.warn('Cursor to {0} failed'.format(self.host), calling = self.calling)
            
    def use_dB(self, base_name = None):
        if not self.connected:
            pc.log_.error('Not connected to the serevr')
            return None        
        if base_name is None:
            self._dB.select_db(self.base_name)
        else:
            self._dB.select_db(base_name)
            
    def use_dB_tmp(self, tmp_base_name = None):
        if not self.connected:
            pc.log_.error('Not connected to the server')
            return None
        if tmp_base_name is None:
            self._dB.select_db(self.tmp_base_name)
        else:
            self._dB.select_db(tmp_base_name)
        
    def show_tables(self):
        print(self.exec_dB('show tables'))
        
    def share_dB_cursor(self, m):
        self._dB = m._dB
        self._cursor = m._cursor
        self._cursor_tuple = m._cursor_tuple

    def close_dB(self):
        if self.connected:
            self._cursor.close()
            self._cursor_tuple.close()
            self._dB.close()
            self.connected = False
            self.log_.message('Disconnected', calling = self.calling)
        else:
            self.log_.warn('Not connected', calling = self.calling)

    def exec_dB(self, command, format_ = 'dict', return_descr=False, commit=False):
        if format_ not in ('dict', 'tuple', 'numpy', 'dict2', 'pandas', 'rec'):
            self.log_.error('format"{0}" not recognized'.format(format_), calling = self.calling)
        if not self.connected:
            self.log_.error('Not connected to a database', calling = self.calling)
            return None
        self.log_.message('Command sent: {0}'.format(command), calling = self.calling)
        if format_ == 'pandas':
            if pc.config.INSTALLED['pandas']:
                res = psql.frame_query(command, con=self._dB)
                return res, len(res)
            else:
                pc.log_.error('pandas is not available, use another format', calling=self.calling)
        if format_[0:4] == 'dict' or format_ == 'rec':
            cursor = self._cursor
        else:
            cursor = self._cursor_tuple
        try:
            N = cursor.execute(command)
        except:
            self.log_.error('Error on executing {0}'.format(command), calling = self.calling)
        if commit:
            try:
                self._dB.commit()
            except:
                self.log_.error('Error on commiting {0}'.format(command), calling = self.calling)
        try:
            res = cursor.fetchall()
        except:
            self.log_.error('Error on reading result of {0}'.format(command), calling = self.calling)
        if format_ == 'rec':
            res = np.rec.fromrecords([list(e.values()) for e in res], names = list(res[0].keys()))
        if return_descr:
            return res, N, cursor.description
        else:
            return res, N
            
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
        if (type(select_) == type(())) or (type(select_) == type([])):
            this_select = ''
            for w in select_:
                this_select += w + ', '
            this_select = this_select[:-2]
        else:
            this_select = select_

        if (type(where_) == type(())) or (type(where_) == type([])):
            this_where = ''
            for w in where_:
                this_where += w + ' and '
            this_where = this_where[:-5]
        else:
            this_where = where_

        if (type(from_) == type(())) or (type(from_) == type([])):
            this_from = ''
            for w in from_:
                this_from += w + ', '
            this_from = this_from[:-2]
        else:
            this_from = from_
            
        req = 'SELECT {0} FROM {1} '.format(this_select, this_from)
        if where_ is not None:
            req += 'WHERE ({0}) '.format(this_where)
        if order_ is not None:
            req += 'ORDER BY {0} '.format(order_)
        if group_ is not None:
            req += 'GROUP BY {0} '.format(group_)
        if limit_ is not None:
            req += 'LIMIT {0:d}'.format(limit_)
            
        if format_ == 'pandas':
            if not pc.config.INSTALLED['pandas']:
                pc.log_.error('pandas not installed', calling='MdB.select_dB')
            res = pd.read_sql(req, con=self._dB)
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
        res, N = self.exec_dB(req, commit=commit)
        return res[0]['count(*)']
    
    def get_fields(self, from_ = None):
        if from_ is None:
            from_ = self.table
        froms = from_.split(',')
        if len(froms) == 1:
            res, N = self.exec_dB('SHOW COLUMNS FROM {0}'.format(from_))
            fields = [res[i]['Field'] for i in range(len(res))]
            fields.sort()
            return fields
        else:
            fields = []
            for this_from in froms:
                fields.extend(self.get_fields(from_ = this_from))
            return fields
    
    def get_cols(self, select_ = '*', from_ = None):
        if from_ is None:
            from_ = self.table
        froms = from_.split(',')
        
        if len(froms) == 1:
            if select_ == '*':
                res, N = self.exec_dB('SHOW COLUMNS FROM {0}'.format(from_))
            else:
                req = 'SHOW COLUMNS FROM {0} WHERE'.format(from_)
                fields = select_.split(',')
                for field in fields:
                    req += ' FIELD = "{0}" OR'.format(field.strip())
                req = req[:-3]
                res, N = self.exec_dB(req)
            return res
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
        elif user_passwd is 'getit':
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
            
            
    