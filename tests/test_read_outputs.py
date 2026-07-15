"""
Equivalence tests between the pandas fast path of CloudyModel.read_outputs
and the historical np.genfromtxt reader, using the real Cloudy outputs in
tests/models/M17.*. No database or Cloudy binary needed.

Run with: pytest tests/test_read_outputs.py
"""

import os
import glob
import numpy as np
import pytest
import pyCloudy as pc

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, 'models', 'M17')

pc.log_.level = 0


def genfromtxt_kwargs(ext):
    kw = {'delimiter': '\t', 'comments': ';', 'names': True}
    if ext in ('emis', 'lin'):
        kw['case_sensitive'] = 'upper'
    if ext == 'cont':
        kw['usecols'] = (0, 1, 2, 3, 4, 5, 6)
    return kw


def pipeline_extensions():
    exts = ['rad', 'phy', 'cont', 'emis']
    exts.extend(sorted(os.path.basename(f).split('M17.')[1]
                       for f in glob.glob(MODEL + '.ele_*')))
    return exts


@pytest.fixture(scope='module')
def CM():
    return pc.CloudyModel(MODEL, read_all_ext=False)


@pytest.mark.parametrize('ext', pipeline_extensions())
def test_pandas_reader_equivalent_to_genfromtxt(CM, ext):
    file_ = MODEL + '.' + ext
    kw = genfromtxt_kwargs(ext)
    old = np.genfromtxt(file_, **kw)
    kw.pop('delimiter')
    kw.pop('comments')
    kw.pop('names')
    new = CM._read_outputs_pandas(file_, **kw)
    assert new is not None
    assert old.dtype.names == new.dtype.names
    assert old.shape == new.shape
    assert old.size == new.size
    for name in old.dtype.names:
        assert np.array_equal(np.atleast_1d(old[name]), np.atleast_1d(new[name]),
                              equal_nan=True), 'column {0} differs'.format(name)


def test_single_row_file_is_0d(CM, tmp_path):
    with open(MODEL + '.rad') as fh:
        lines = fh.readlines()
    one = tmp_path / 'one.rad'
    one.write_text(''.join(lines[:2]))
    old = np.genfromtxt(str(one), delimiter='\t', comments=';', names=True)
    new = CM._read_outputs_pandas(str(one))
    assert old.shape == new.shape == ()
    assert old.size == new.size == 1
    for name in old.dtype.names:
        assert old[name] == new[name]


def test_empty_file_returns_none(CM, tmp_path):
    with open(MODEL + '.rad') as fh:
        header = fh.readline()
    empty = tmp_path / 'empty.rad'
    empty.write_text(header)
    saved = CM.model_name
    CM.model_name = str(tmp_path / 'empty')
    try:
        assert CM.read_outputs('rad') is None
    finally:
        CM.model_name = saved


def test_read_outputs_uses_fast_path(CM):
    res = CM.read_outputs('rad')
    assert res is not None
    assert res.dtype.names == ('NZONE', 'radius', 'depth', 'dr')


@pytest.fixture(scope='module')
def full_model():
    return pc.CloudyModel(MODEL, read_cont=True, list_elem=['H', 'O'])


def test_i_emis_matches_argwhere(full_model):
    m = full_model
    for label in m.emis_labels:
        expected = np.argwhere(np.asarray(m.emis_labels_17) == label)
        if expected.size == 0:
            expected = np.argwhere(np.asarray(m.emis_labels_13) == label)
        assert m._i_emis(label) == expected[0][0]


def test_i_emis_unknown_label(full_model):
    assert full_model._i_emis('NOT_A_LINE_1234A') is None


def test_i_emis_cache_rebuilds_after_append(full_model):
    m = full_model
    m._i_emis(m.emis_labels[0])  # populate the cache
    new_label = 'BLND_9999A'
    m.emis_labels = np.append(m.emis_labels, new_label)
    m.emis_labels_17 = m.emis_labels
    m.emis_full = np.vstack([m.emis_full, np.zeros((1, m.emis_full.shape[1]))])
    m.n_emis += 1
    assert m._i_emis(new_label) == len(m.emis_labels) - 1


def test_model_spot_checks(full_model):
    m = full_model
    assert m.n_zones_full > 1
    assert np.isfinite(m.Hbeta_full[-1]) and m.Hbeta_full[-1] > 0
    ev = m.get_emis_vol('O__3_500684A')
    assert np.isfinite(ev) and ev > 0
    assert np.isfinite(m.get_T0_emis('O__3_500684A'))
    assert m.is_valid_ion('O', 2)
