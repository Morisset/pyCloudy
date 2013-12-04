import os
import numpy as np
import pyCloudy as pc
from pyCloudy.utils.init import LIST_ELEM
from pyCloudy.utils.logging import my_logging
if pc.config.INSTALLED['MySQL']:
    import MySQLdb

import subprocess

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
                 connect = True):
        """
        This is the package to deal with MySQL OVN database. 
        You need to have installed the mysql client and the mysql-dev library in order to install 
        the MySQLdb python package.
        The dev libraries are named mysql15-dev in the fink distro. Check with 'fink list mysql' 
        that the dev and the client are the save version.
        
        Under pip, the MySQLdb package is named MySQL-python
        
        Latter, we will also use the ODBC connector. Install the connector from MySQl: http://dev.mysql.com/downloads/connector/odbc/
        and then use pyodbc with:
        cnxn = pyodbc.connect('DRIVER={MySQL ODBC 5.2 Driver};SERVER=132.248.1.102;DATABASE=OVN2;UID=OVN_admin2;PWD=oiii4363;SOCKET=/var/mysql/mysql.sock')
        
        """


        self.log_ = MdB.MdBlog_
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
        self.base_name = base_name
        self.tmp_base_name = tmp_base_name
        self.user_name = user_name
        if user_passwd == 'getenv':
            self.user_passwd = os.getenv('{0}_pass'.format(user_name))
        else:
            self.user_passwd = user_passwd
        self.port = port
        self.host = host
        self.unix_socket = unix_socket
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
            self._dB = MySQLdb.connect(host = self.host, user = self.user_name, passwd = self.user_passwd, 
                                        db = self.base_name, port = self.port, unix_socket = self.unix_socket)
            self._cursor = self._dB.cursor(MySQLdb.cursors.DictCursor)
            self._cursor_tuple = self._dB.cursor(MySQLdb.cursors.Cursor)
            self.connected = True
            self.log_.message('Connected to {0}'.format(self.host), calling = self.calling)
        except:
            self.log_.warn('Connection to {0} failed'.format(self.host), calling = self.calling)

    def use_dB(self, base_name = None):
        if not self.connected:
            pc.log_.error('Not connected to the database')
            return None        
        if base_name is None:
            self._dB.select_db(self.base_name)
        else:
            self._dB.select_db(base_name)
            
    def use_dB_tmp(self, tmp_base_name = None):
        if not self.connected:
            pc.log_.error('Not connected to the database')
            return None
        if tmp_base_name is None:
            self._dB.select_db(self.tmp_base_name)
        else:
            self._dB.select_db(tmp_base_name)
        
    def show_tables(self):
        print self.exec_dB('show tables')
        
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

    def exec_dB(self, command, format_ = 'dict'):
        if format_ not in ('dict', 'tuple', 'numpy', 'dict2'):
            self.log_.error('format"{0}" not recognized'.format(format_), calling = self.calling)
        if not self.connected:
            self.log_.error('Not connected to a database', calling = self.calling)
            return None
        self.log_.message('Command sent: {0}'.format(command), calling = self.calling)
        if format_[0:4] == 'dict':
            cursor = self._cursor
        else:
            cursor = self._cursor_tuple
        try:
            N = cursor.execute(command)
        except:
            self.log_.error('Error on executing {0}'.format(command), calling = self.calling)
        try:
            res = cursor.fetchall()
        except:
            self.log_.error('Error on reading result of {0}'.format(command), calling = self.calling)
        return res, N
            
    def select_dB(self, select_ = '*', from_ = 'OVN.tab1', where_ = None, order_ = None, group_ = None, limit_ = 1,
                  format_ = 'dict', dtype_ = None):
        """
        Usage:
            dd, n = mdb.select_dB(select_ = 'L_1, L_26, L_21', 
                        where_ = 'ref like "DIG12HR_"', 
                        limit_ = 100000, 
                        format_='numpy')
            loglog(dd['L_26']/dd['L_1'], dd['L_21']/dd['L_1'], 'r+')            
        """
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
        res, N = self.exec_dB(req, format_ = format_)
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
    
    def count_dB(self, from_ = 'OVN.tab1', where_ = None):
        req = 'SELECT count(*) FROM {0}'.format(from_)
        if where_ is not None:
            req += ' WHERE ({0})'.format(where_)
        res, N = self.exec_dB(req)
        return res[0]['count(*)']
    
    def get_fields(self, from_ = 'OVN.tab1'):
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
    
    def get_cols(self, select_ = '*', from_ = 'OVN.tab1'):
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
            res = ()
            for this_from in froms:
                res += self.get_cols(select_ = select_, from_ = this_from)
            return res
            
    def get_dtype(self, select_ = '*', from_ = 'OVN.tab1'):
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
                col = self.get_cols(select_ = field.strip(), from_ = from_)[0]
                name = col['Field']
                sqltype = col['Type']
                ntype = _sql2numpy(sqltype)
                if (name, ntype) not in dtype_list:
                    dtype_list.append((name, ntype))        
        return np.dtype(dtype_list)
            
    def print_all_refs(self, from_ = 'OVN.tab1'):
        res, N_ref = self.select_dB(select_ = 'distinct(ref), count(*)', from_ = from_, group_ = 'ref', limit_ = None)
        for row in res:
            print('The ref "{0:15}" counts {1:8d} entries.'.format(row['ref'], row['count(*)']))
        print('Number of distinct references = {0}'.format(N_ref))
        
    def print_all_lines(self, limit_ = None):
        lines, N_lines = self.select_dB(select_ = '*', from_ = 'OVN.lines', limit_ = limit_)
        for line in lines:
            print('N = {0[N]:3} id = {0[id]:4} label = {0[label]:5} wavelength = {0[lambda]:6} full name = {0[name]}'.format(line))

    def __repr__(self):
        if self.connected:
            return "<MdB connected to {0.base_name}@{0.host}>".format(self)
        else:
            return "<MdB disconnected from {0.base_name}@{0.host}>".format(self)
        
class MdB_subproc(object):
    """
    Alternative way, when MySQLdb not available. Still in development.
    """
    def __init__(self, OVN_dic = None, base_name = 'OVN',tmp_base_name = 'OVN_tmp', 
                 user_name = 'OVN_user', user_passwd = 'getenv', 
                 host = 'localhost', unix_socket = '/var/mysql/mysql.sock', port = 3306,
                 connect = True):
        
        self.log_ = MdB.MdBlog_
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
        self.base_name = base_name
        self.tmp_base_name = tmp_base_name
        self.user_name = user_name
        if user_passwd == 'getenv':
            self.user_passwd = os.getenv('{0}_pass'.format(user_name))
        else:
            self.user_passwd = user_passwd
        self.port = port
        self.host = host
        self.unix_socket = unix_socket
        self._dB = None
        self._cursor = None
        self._cursor_tuple = None
        self.connected = True

    def connect_dB(self):
        pass
    
    def exec_dB(self, command, format_ = 'dict'):
        if format_ not in ('dict', 'tuple', 'numpy', 'dict2'):
            self.log_.error('format"{0}" not recognized'.format(format_), calling = self.calling)
        if not self.connected:
            self.log_.error('Not connected to a database', calling = self.calling)
            return None
        self.log_.message('Command sent: {0}'.format(command), calling = self.calling)


        proc = subprocess.Popen(["mysql", 
                                 "--host={0}".format(self.host),
                                 "--user={0}".format(self.user_name), 
                                 "--password={0}".format(self.user_passwd), 
                                 "{0}".format(self.base_name)],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        out, err = proc.communicate(command)
        try:
            out = out.split('\n')
        except:
            pass
        try:
            N = len(out)
        except:
            N = None
        return out, N

    def select_dB(self, select_ = '*', from_ = 'OVN.tab1', where_ = None, order_ = None, group_ = None, limit_ = 1,
                  format_ = 'dict', dtype_ = None):
        """
        Usage:
            dd, n = mdb.select_dB(select_ = 'L_1, L_26, L_21', 
                        where_ = 'ref like "DIG12HR_"', 
                        limit_ = 100000, 
                        format_='numpy')
            loglog(dd['L_26']/dd['L_1'], dd['L_21']/dd['L_1'], 'r+')            
        """
        req = 'SELECT {0} FROM {1} '.format(select_, from_)
        if where_ is not None:
            req += 'WHERE ({0}) '.format(where_)
        if order_ is not None:
            req += 'ORDER BY {0} '.format(order_)
        if group_ is not None:
            req += 'GROUP BY {0} '.format(group_)
        if limit_ is not None:
            req += 'LIMIT {0:d}'.format(limit_)
        res, N = self.exec_dB(req, format_ = format_)
        try:
            for i,line in enumerate(res):
                res[i] = line.split('\t')
        except:
            pass
        
    
    