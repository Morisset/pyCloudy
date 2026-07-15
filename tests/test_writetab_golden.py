"""
End-to-end test of writeTab.insert_model on the real Cloudy outputs of
tests/models/M17, against an in-memory SQLite database (no MySQL server,
no Cloudy binary needed). Checks that the values inserted into tab, abion,
teion and temis are the ones computed by CloudyModel, that the mass-cut
loop produces distinct rows, and that a reused writeTab does not leak
values from one model into the next.

Run with: pytest tests/test_writetab_golden.py
"""

import os
import numpy as np
import pytest
import sqlalchemy as sa
import pyCloudy as pc
from pyCloudy.db import use3MdB

pc.log_.level = 0

HERE = os.path.dirname(os.path.abspath(__file__))

OVN_dic = {'base_name': 'test',
           'user_name': 'test',
           'user_passwd': 'test',
           'host': 'localhost',
           'master_table': 'tab',
           'pending_table': 'pending',
           'lines_table': 'lines',
           'abion_table': 'abion',
           'teion_table': 'teion',
           'temis_table': 'temis',
           'list_elem': ['H', 'O']}

LINE_COLS = ['H__1_486133A', 'O__3_500684A']


def make_db():
    engine = sa.create_engine('sqlite://')
    mdb = pc.MdB(OVN_dic=OVN_dic, connect=False)
    mdb.use_engine(engine)
    mdb.exec_dB("""CREATE TABLE pending (
        N INTEGER PRIMARY KEY AUTOINCREMENT,
        date_submitted TIMESTAMP, date_running TIMESTAMP,
        ref VARCHAR(15), user VARCHAR(15), file VARCHAR(80), dir VARCHAR(80),
        com1 VARCHAR(45), radius DOUBLE, dens DOUBLE,
        status INT DEFAULT 0, priority INT DEFAULT 10, procID BIGINT DEFAULT -1)""")
    mdb.exec_dB("""CREATE TABLE tab (
        N INTEGER PRIMARY KEY AUTOINCREMENT,
        datetime TIMESTAMP, host VARCHAR(45),
        N_pending INT, ref VARCHAR(15), user VARCHAR(15), file VARCHAR(80), dir VARCHAR(80),
        com1 VARCHAR(45), radius DOUBLE, dens DOUBLE,
        N_zones INT, logQ DOUBLE, THp DOUBLE, MassFrac DOUBLE, HbFrac DOUBLE,
        H_mass DOUBLE, Hb_SB DOUBLE,
        {0})""".format(', '.join('`{0}` DOUBLE, `{0}_rad` DOUBLE'.format(c) for c in LINE_COLS)))
    mdb.exec_dB("""CREATE TABLE abion (
        N INT, ref VARCHAR(15),
        A_HYDROGEN_vol_1 DOUBLE, A_OXYGEN_vol_2 DOUBLE, A_OXYGEN_vol_3 DOUBLE,
        A_OXYGEN_rad_3 DOUBLE)""")
    mdb.exec_dB("""CREATE TABLE teion (
        N INT, ref VARCHAR(15),
        T_HYDROGEN_vol_1 DOUBLE, T_OXYGEN_vol_2 DOUBLE, T_OXYGEN_vol_3 DOUBLE,
        T_OXYGEN_rad_3 DOUBLE)""")
    mdb.exec_dB("""CREATE TABLE temis (
        N INT, ref VARCHAR(15),
        {0})""".format(', '.join('`T_{0}` DOUBLE'.format(c) for c in LINE_COLS)))
    mdb.exec_dB("""CREATE TABLE lines (
        id VARCHAR(20), lambda DOUBLE, label VARCHAR(15), name VARCHAR(40))""")
    mdb.exec_dB("INSERT INTO lines (id, lambda, label, name) "
                "VALUES ('O  3', 5006.84, 'O__3_500684A', 'O 3 5006.84A')", commit=True)
    mdb.exec_dB("INSERT INTO pending (ref, user, file, dir, com1, radius, dens, status) "
                "VALUES ('golden', 'tester', 'M17', 'models', 'first', 17.5, 2.0, 1)")
    mdb.exec_dB("INSERT INTO pending (ref, user, file, dir, radius, dens, status) "
                "VALUES ('golden', 'tester', 'M17', 'models', 18.5, 3.0, 1)", commit=True)
    return mdb


def skip_blends(CM):
    """The M17 model does not contain the auroral lines used to build the c17
    blends, so we pre-add the guard label to skip the blend-building branch."""
    CM.emis_labels = np.append(CM.emis_labels, 'BLND_575500A')
    CM.emis_labels_17 = CM.emis_labels
    CM.emis_full = np.vstack([CM.emis_full, np.zeros((1, CM.emis_full.shape[1]))])
    CM.n_emis += 1


@pytest.fixture(scope='module')
def wT():
    mdb = make_db()
    wT = use3MdB.writeTab(mdb, models_dir=HERE)
    wT.read_pending(1)
    assert wT.read_model()
    skip_blends(wT.CloudyModel)
    wT.insert_model()
    return wT


def get_row(wT, table, N):
    res, n = wT.MdB.select_dB(select_='*', from_=table, where_='N = {0}'.format(N))
    assert n == 1
    return res[0]


class TestGoldenValues:

    def test_tab_row(self, wT):
        CM = wT.CloudyModel
        row = get_row(wT, 'tab', 1)
        assert row['ref'] == 'golden'
        assert row['N_pending'] == 1
        assert row['com1'] == 'first'
        assert row['radius'] == 17.5
        assert row['N_zones'] == CM.n_zones
        assert np.isclose(row['H__1_486133A'], CM.get_emis_vol('H__1_486133A'))
        assert np.isclose(row['O__3_500684A'], CM.get_emis_vol('O__3_500684A'))
        assert np.isclose(row['O__3_500684A_rad'], CM.get_emis_rad('O__3_500684A'))
        assert np.isclose(row['THp'], CM.get_T0_ion_vol_ne(elem='H', ion=1))
        assert np.isclose(row['H_mass'], CM.H_mass)

    def test_abion_teion_rows(self, wT):
        CM = wT.CloudyModel
        ab = get_row(wT, 'abion', 1)
        te = get_row(wT, 'teion', 1)
        assert ab['ref'] == te['ref'] == 'golden'
        assert np.isclose(ab['A_HYDROGEN_vol_1'], CM.get_ab_ion_vol_ne('H', 1))
        assert np.isclose(ab['A_OXYGEN_vol_3'], CM.get_ab_ion_vol_ne('O', 3))
        assert np.isclose(ab['A_OXYGEN_rad_3'], CM.get_ab_ion_rad_ne('O', 3))
        assert np.isclose(te['T_OXYGEN_vol_3'], CM.get_T0_ion_vol_ne('O', 3))
        assert np.isclose(te['T_OXYGEN_rad_3'], CM.get_T0_ion_rad_ne('O', 3))

    def test_temis_row(self, wT):
        CM = wT.CloudyModel
        tem = get_row(wT, 'temis', 1)
        assert np.isclose(tem['T_O__3_500684A'], CM.get_T0_emis('O__3_500684A'))
        assert np.isclose(tem['T_H__1_486133A'], CM.get_T0_emis('H__1_486133A'))

    def test_status_updated(self, wT):
        row = get_row(wT, 'pending', 1)
        assert row['status'] == 50  # 'Master table updated'


class TestCutsAndReuse:

    def test_mass_cut_inserts_smaller_model(self, wT):
        CM = wT.CloudyModel
        CM.H_mass_cut = 0.5 * CM.H_mass_full[-1]
        wT.insert_model()
        assert wT.last_N == 2
        full = get_row(wT, 'tab', 1)
        cut = get_row(wT, 'tab', 2)
        assert cut['MassFrac'] < 1.0
        assert cut['MassFrac'] < full['MassFrac']
        assert cut['H__1_486133A'] < full['H__1_486133A']
        assert np.isclose(cut['H__1_486133A'], CM.get_emis_vol('H__1_486133A'))
        # restore the full model
        CM.H_mass_cut = CM.H_mass_full[-1]

    def test_reuse_does_not_leak_previous_model(self, wT):
        wT.read_pending(2)
        assert wT.read_model()
        skip_blends(wT.CloudyModel)
        wT.insert_model()
        row = get_row(wT, 'tab', wT.last_N)
        assert row['N_pending'] == 2
        assert row['radius'] == 18.5
        assert row['com1'] is None  # would be 'first' if _dic leaked
        assert get_row(wT, 'pending', 2)['status'] == 50
