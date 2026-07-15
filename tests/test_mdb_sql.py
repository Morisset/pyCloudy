"""
Tests of the SQLAlchemy-based MdB layer and of the writePending buffering,
using an in-memory SQLite engine (no MySQL server needed). The MySQL-specific
statements (atomic claim, requeue_stale) are checked at the SQL-text level
with a recording fake.

Run with: pytest tests/test_mdb_sql.py
"""

import numpy as np
import pytest
import sqlalchemy as sa
import pyCloudy as pc
from pyCloudy.db import use3MdB

pc.log_.level = 0

OVN_dic = {'base_name': 'test',
           'user_name': 'test',
           'user_passwd': 'test',
           'host': 'localhost',
           'master_table': 'tab',
           'pending_table': 'pending',
           'lines_table': 'lines'}


def make_mdb():
    engine = sa.create_engine('sqlite://')
    mdb = pc.MdB(OVN_dic=OVN_dic, connect=False)
    mdb.use_engine(engine)
    return mdb


def make_pending(mdb):
    mdb.exec_dB("""CREATE TABLE pending (
        N INTEGER PRIMARY KEY AUTOINCREMENT,
        date_submitted TIMESTAMP,
        date_running TIMESTAMP,
        ref VARCHAR(15),
        user VARCHAR(15),
        file VARCHAR(80),
        dir VARCHAR(80),
        com1 VARCHAR(45),
        radius DOUBLE,
        dens DOUBLE,
        status INT DEFAULT 0,
        priority INT DEFAULT 10,
        procID BIGINT DEFAULT -1)""", commit=True)


class TestMdB:

    def test_exec_params_and_lastrowid(self):
        mdb = make_mdb()
        make_pending(mdb)
        res, N = mdb.exec_dB('INSERT INTO pending (ref, radius) VALUES (:ref, :radius)',
                             params={'ref': "with 'quote'", 'radius': 17.5}, commit=True)
        assert N == 1
        assert mdb.last_rowid == 1
        res, N = mdb.select_dB(select_='*', from_='pending', where_='N = 1')
        assert N == 1
        assert res[0]['ref'] == "with 'quote'"
        assert res[0]['radius'] == 17.5

    def test_select_formats(self):
        mdb = make_mdb()
        make_pending(mdb)
        for i in range(3):
            mdb.exec_dB('INSERT INTO pending (ref, radius) VALUES (:r, :v)',
                        params={'r': 'ref{0}'.format(i), 'v': float(i)}, commit=True)
        res, N = mdb.select_dB(select_='N, radius', from_='pending', limit_=None,
                               format_='numpy', dtype_=[('N', 'i4'), ('radius', 'f8')])
        assert N == 3
        assert np.array_equal(res['radius'], [0., 1., 2.])
        res, N = mdb.select_dB(select_='*', from_='pending', limit_=None, format_='dict2')
        assert np.array_equal(res['N'], [1, 2, 3])
        assert mdb.count_dB(from_='pending') == 3

    def test_get_fields_cached(self):
        mdb = make_mdb()
        make_pending(mdb)
        fields = mdb.get_fields(from_='pending')
        assert 'ref' in fields and 'status' in fields
        mdb.exec_dB('ALTER TABLE pending ADD COLUMN extra DOUBLE', commit=True)
        assert 'extra' not in mdb.get_fields(from_='pending')  # cached
        assert 'extra' in mdb.get_fields(from_='pending', refresh=True)

    def test_get_dtype(self):
        mdb = make_mdb()
        make_pending(mdb)
        dt = mdb.get_dtype(select_='N, radius, ref', from_='pending')
        assert dt['N'].kind == 'i'
        assert dt['radius'] == np.dtype('f8')

    def test_error_reports_driver_message(self):
        mdb = make_mdb()
        make_pending(mdb)
        with pytest.raises(Exception):
            mdb.exec_dB('INSERT INTO no_such_table (x) VALUES (1)')
        # the connection must stay usable after a failed statement
        res, N = mdb.select_dB(select_='*', from_='pending', limit_=None)
        assert N == 0


class TestWritePending:

    def fill(self, wP, i):
        wP.set_ref('test_ref')
        wP.set_user('tester')
        wP.set_file('grid')
        wP.set_dir('models/')
        wP.set_radius(17. + i)
        wP.set_priority(10)

    def test_unbuffered(self):
        mdb = make_mdb()
        make_pending(mdb)
        wP = use3MdB.writePending(mdb, OVN_dic)
        for i in range(3):
            self.fill(wP, i)
            wP.insert_model()
            assert wP.last_N == i + 1
        res, N = mdb.select_dB(select_='N, file, radius', from_='pending', limit_=None)
        assert N == 3
        for row in res:
            assert row['file'] == 'grid_{0}'.format(row['N'])

    def test_buffered(self):
        mdb = make_mdb()
        make_pending(mdb)
        wP = use3MdB.writePending(mdb, OVN_dic, buffer_size=2)
        for i in range(5):
            self.fill(wP, i)
            wP.insert_model()
        # two auto-flushes of 2, one model still buffered
        assert mdb.count_dB(from_='pending') == 4
        wP.flush()
        assert mdb.count_dB(from_='pending') == 5
        assert wP.last_N == 5
        res, N = mdb.select_dB(select_='N, file, radius', from_='pending', limit_=None)
        for row in res:
            assert row['file'] == 'grid_{0}'.format(row['N'])
        assert sorted(r['radius'] for r in res) == [17., 18., 19., 20., 21.]

    def test_buffer_flushes_on_key_change(self):
        mdb = make_mdb()
        make_pending(mdb)
        wP = use3MdB.writePending(mdb, OVN_dic, buffer_size=100)
        self.fill(wP, 0)
        wP.set_comments('a comment', i_com=0)
        wP.insert_model()
        self.fill(wP, 1)
        wP.set_comments(None, i_com=0)  # different key set: forces a flush
        wP.insert_model()
        assert mdb.count_dB(from_='pending') == 1
        wP.flush()
        assert mdb.count_dB(from_='pending') == 2
        res, N = mdb.select_dB(select_='*', from_='pending', where_='N = 2')
        assert res[0]['com1'] is None


class RecordingMdB(object):
    """Fake MdB recording the executed commands, for MySQL-only statements."""

    def __init__(self, script=None):
        self.commands = []
        self.connected = True
        self.script = script or {}
        self.last_rowid = None
        self.OVN_dic = OVN_dic

    def exec_dB(self, command, format_='dict', commit=False, params=None):
        self.commands.append(str(command))
        for key, (res, N, rowid) in self.script.items():
            if key in str(command):
                self.last_rowid = rowid
                return res, N
        return (), 0

    def select_dB(self, select_='*', from_=None, where_=None, order_=None, group_=None,
                  limit_=1, format_='dict', dtype_=None, commit=False):
        command = 'SELECT {0} FROM {1} WHERE {2} GROUP BY {3}'.format(select_, from_, where_, group_)
        self.commands.append(command)
        for key, (res, N, rowid) in self.script.items():
            if key in command:
                return res, N
        return None, 0


class TestClaim:

    def make_rc(self, mdb, check_priority=True):
        rc = use3MdB.runCloudy.__new__(use3MdB.runCloudy)
        rc.log_ = pc.log_
        rc.calling = 'runCloudy'
        rc.MdB = mdb
        rc.OVN_dic = OVN_dic
        rc.pending_table = 'pending'
        rc.procID = 7
        rc.check_priority = check_priority
        return rc

    def test_claim_sql_shape(self):
        mdb = RecordingMdB(script={'priority, count(*)': ([(10, 5)], 1, None),
                                   'UPDATE pending SET N = LAST_INSERT_ID(N)': ((), 1, 42)})
        rc = self.make_rc(mdb)
        rc.select_pending()
        assert rc.selectedN == 42
        claim = [c for c in mdb.commands if 'LAST_INSERT_ID(N)' in c]
        assert len(claim) == 1
        assert 'WHERE status = 0' in claim[0]
        assert 'ORDER BY N LIMIT 1' in claim[0]
        assert '`procID`=7' in claim[0]
        # single priority: no priority filter in the claim
        assert 'AND priority' not in claim[0]

    def test_claim_with_priorities(self):
        mdb = RecordingMdB(script={'priority, count(*)': ([(10, 5), (12, 3)], 2, None),
                                   'UPDATE pending SET N = LAST_INSERT_ID(N)': ((), 1, 11)})
        rc = self.make_rc(mdb)
        np.random.seed(0)
        rc.select_pending()
        assert rc.selectedN == 11
        claim = [c for c in mdb.commands if 'LAST_INSERT_ID(N)' in c][0]
        assert 'AND priority =' in claim

    def test_empty_queue(self):
        mdb = RecordingMdB(script={'priority, count(*)': (None, 0, None),
                                   'UPDATE pending SET N = LAST_INSERT_ID(N)': ((), 0, None)})
        rc = self.make_rc(mdb)
        rc.select_pending()
        assert rc.selectedN is None


def test_requeue_stale_sql():
    mdb = RecordingMdB(script={'UPDATE pending SET `status` = 0': ((), 3, None)})
    N = use3MdB.requeue_stale(MdB=mdb, older_than_hours=72, statuses=(1, 2))
    assert N == 3
    cmd = mdb.commands[0]
    assert '`status` IN (1, 2)' in cmd
    assert 'INTERVAL 72 HOUR' in cmd
    assert '`procID` = -1' in cmd
