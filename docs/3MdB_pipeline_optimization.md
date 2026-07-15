# 3MdB Pipeline Optimization Report

**Branch:** `Fabel_3mdb_optimization`
**Date:** July 2026
**Scope:** `pyCloudy/db/` (MdB.py, use3MdB.py, initSQL.py), `pyCloudy/c1d/cloudy_model.py`, `pyCloudy/3MdB_17/make_PNe_20.py`, `pyCloudy/utils/Config.py`, `pyproject.toml`, new tests in `tests/`.

---

## 1. Background

The 3MdB pipeline has two phases:

1. **Populate** — the `3MdB_17/make_*.py` scripts insert 10⁴–10⁵ rows into a MySQL/MariaDB
   `pending` table through `use3MdB.writePending.insert_model()` (e.g. `make_PNe_20.py`
   generates ≈145,000 models).
2. **Run** — on several computers, `use3MdB.manage3MdB` spawns `runCloudyByThread` worker
   threads. Each thread loops: claim a pending model, write the Cloudy input file, run
   Cloudy (a subprocess that can last hours), read the outputs with `pc.CloudyModel`, and
   insert the results into the `tab`, `abion`, `teion` and `temis` tables through
   `use3MdB.writeTab.insert_model()` — once for the full model, then once per mass cut and
   per Hβ cut.

An audit of this pipeline found the bottlenecks and defects listed below; all of them are
fixed on this branch. The database layer was rebuilt on **SQLAlchemy Core** (user request),
keeping the public `MdB` API unchanged so that existing scripts and notebooks keep working.

### Decisions taken

| Decision | Choice |
|---|---|
| DB access layer | SQLAlchemy Core (engine + pool + `text()` + table reflection), driver still selected by `pc.config.db_connector` (PyMySQL or MySQLdb) |
| Populate batching | **Opt-in** (`buffer_size` keyword); default behavior identical to before |
| Target server | MariaDB (default `innodb_autoinc_lock_mode=1` → consecutive ids for multi-row INSERTs) |
| Verification | Mock tests only: in-memory SQLite + recording fakes + the real Cloudy outputs in `tests/models/M17.*`. No MySQL server or Cloudy binary needed. |
| Robustness fixes | Included (atomic claim, stale-claim requeue, parameterized SQL, error reporting) |

---

## 2. Bottlenecks found (with the original locations)

### Populate phase

- **3 individually committed round-trips per pending row** (`writePending.insert_model`):
  `INSERT` + `SELECT last_insert_id()` + `UPDATE ... SET FILE="name_N"` — the read-back and
  the UPDATE existed only because the file name embeds the auto-increment `N`. For a 145k
  grid this is ≈435,000 round-trips and 435,000 commits over the network.
- SQL values were interpolated into the command string **without escaping**: any `'` in a
  comment, ref or file name produced invalid SQL.

### Claim phase (`runCloudy.select_pending`)

- With priorities enabled, every claim attempt by every worker fetched **all** status=0
  rows (`SELECT N, priority ... limit_=None`) — up to 145k rows per poll, per thread,
  per machine.
- The claim itself was a non-atomic SELECT → UPDATE → verify-SELECT dance (3–4 queries);
  two workers could pick the same candidate and one wasted the cycle.
- A crashed/killed worker left its model stuck at `status=1` forever; `date_running` was
  recorded but never used to requeue.
- Empty-queue polling: fixed 10 s sleep, then the full multi-query dance again.

### Per-model insert phase (`writeTab`)

- A **new `writeTab` was constructed for every model** inside the worker loop → two
  `SHOW COLUMNS` (tab + pending) per model.
- Inside `insert_model`, `SHOW COLUMNS FROM abion` ran **on every call** — so once per cut —
  followed by string-parsing of every abion column. The code itself flagged it:
  `# ToDo : Loosing a lot of time in the following, check why`.
- The `lines` table was re-SELECTed on every `insert_model`.
- ≈9 status UPDATEs per `insert_model`, each with its own commit — multiplied by the number
  of cuts (e.g. `N_Mass_cut=4` → 5–6 `insert_model` calls per model).
- Latent bug: in the temis loop, the column name was appended **before** computing the value
  inside a `try`; an exception left a column without a value and broke the whole INSERT.
- `res`/`N` in `MdB.exec_dB` could be unbound or stale after a swallowed driver error, so
  callers proceeded on garbage; the `format_='pandas'` path used `psql.frame_query`, removed
  from pandas years ago (dead code).

### Output reading (`CloudyModel`)

- `read_outputs` used `np.genfromtxt` (pure-Python parser) for **~35 files per model**
  (30 `.ele_X` element files + `.rad`/`.phy`/`.emis`/`.cont`); the `.emis` file has hundreds
  of columns.
- `_i_emis` did a linear `np.argwhere` scan per label lookup. `lines2dic` and the temis loop
  call it for **every** emission label, once per cut → O(n²) label lookups per model.

---

## 3. Changes

### 3.1 `pyCloudy/db/MdB.py` — SQLAlchemy Core rewrite

The `MdB` class keeps its constructor signature and public API, but internally:

- `connect_dB()` builds `create_engine('mysql+pymysql://…')` (or `mysql+mysqldb` when
  `pc.config.db_connector == 'MySQL'`) with `pool_pre_ping=True` and `pool_recycle=3600`,
  and holds one `Connection` per `MdB` instance. Each worker thread already creates its own
  `MdB`, so the threading model is unchanged. **`pool_pre_ping` means a connection that idled
  through an hours-long Cloudy run is revalidated instead of dying with "MySQL server has
  gone away"** — a real reliability gain for this pipeline.
- `exec_dB(command, …, params=None)`:
  - raw SQL strings without `params` are executed **verbatim** via `exec_driver_sql()`
    (no bind-parameter parsing, so legacy string-built SQL is unaffected);
  - strings with `params` use named binds (`:name`) through `text()`;
  - SQLAlchemy executable objects (e.g. `Table.insert()`) are executed directly; a **list**
    of parameter dicts triggers an `executemany` (bulk) execution;
  - the auto-increment id of the last INSERT is stored in `self.last_rowid`, removing every
    `SELECT last_insert_id()` round-trip;
  - errors are rolled back and reported **with the driver's message**; `res`/`N` are
    initialized first (no more `UnboundLocalError` masking the real problem);
  - the `pandas` format uses `pd.read_sql` (the `psql.frame_query` dead code is gone).
- `get_fields(from_, refresh=False)` / `get_cols` use the SQLAlchemy inspector and are
  **cached per table per instance** — table schemas never change during a run; pass
  `refresh=True` after an ALTER.
- New `get_table(name)` returns a cached reflected `Table` used for bound-parameter inserts.
- New `use_engine(engine)` connects an `MdB` through an existing engine (used by the tests
  with in-memory SQLite).
- New `commit_dB()` commits the pending transaction explicitly.
- `_sql2numpy` also understands SQLAlchemy type strings (`integer`, `smallint`, …).
- `MdB_subproc` is untouched.

### 3.2 Populate: `writePending` buffering (opt-in)

```python
wP = use3MdB.writePending(MdB, OVN_dic, buffer_size=500)
for ...:
    wP.set_...(...)
    wP.insert_model()
wP.flush()          # send the remaining buffered models
```

- `buffer_size=1` (default) reproduces the previous semantics exactly: one committed model
  per `insert_model()` call, `wP.last_N` valid after each call — but even this path is
  cheaper (bound-parameter insert + `last_rowid`; the `SELECT last_insert_id()` round-trip
  and the third commit are gone).
- With `buffer_size > 1`, each flush sends **one bulk `executemany` INSERT** on the reflected
  pending table, then **one server-side rename per distinct base file name**:
  `UPDATE pending SET FILE = CONCAT(FILE, "_", N) WHERE N >= first_N AND FILE = :basename`
  — this reproduces the old `"file_N"` naming without the client ever knowing the ids, and
  stays correct even if concurrent populate jobs interleave auto-increment ids. One commit
  per batch.
- The buffer auto-flushes when full **or when the set of fields changes** (bulk inserts need
  uniform columns; the populate scripts set the same keys every iteration, so batches stay
  large).
- `wP.last_N` is only valid after `flush()` in buffered mode; `first_N` comes from
  `last_rowid`, with a dialect-aware `SELECT LAST_INSERT_ID()` fallback (MariaDB returns the
  *first* id of a multi-row INSERT).
- All values are sent as bound parameters → quotes in comments/refs can no longer break the
  SQL. `insert_SED` was parameterized the same way.
- `make_PNe_20.py` was updated as the reference example (`buffer_size=500` + final `flush()`).
  The other `make_*.py` scripts work unchanged (default `buffer_size=1`).

### 3.3 Worker loop: `writeTab` reuse and precomputation

- `runCloudyByThread.run()` now builds **one `writeTab` per thread** (next to `runCloudy`)
  and reuses it for every model. `writeTab.read_pending()` resets `self._dic = {}` so values
  can never leak from one model into the next.
- New `writeTab._init_static_dB_info()` fetches **once** what never changes during a run:
  - the `lines` table (was: one SELECT per `insert_model`);
  - `self.abion_cols` = the parsed `(field, elem, ion, integ)` list of the abion columns
    (was: `SHOW COLUMNS FROM abion` + string parsing per `insert_model`, i.e. per cut —
    the `# ToDo : Loosing a lot of time` block);
  - the set of temis column names.
- `insert_model` builds plain dicts and inserts them through the reflected tables with bound
  parameters (tab, abion, teion, temis). `SELECT last_insert_id()` is replaced by
  `last_rowid`. The per-cut physics (`get_ab_ion_*`, `get_T0_*`, `get_emis_vol/rad`) is still
  recomputed for every cut — those values genuinely depend on the cut radius.
- The temis latent bug is fixed structurally: a column key is only added together with its
  value, and labels that have no `T_<label>` column in the temis table are skipped instead of
  breaking the whole INSERT.
- New `status_mode` keyword on `writeTab` / `runCloudyByThread` / `manage3MdB`:
  - `'all'` (default): every status UPDATE committed individually — identical to before;
  - `'batched'`: intermediate statuses are sent without commit and everything is committed
    with the final `'Master table updated'` (status 50, the one the monitoring relies on).

### 3.4 Atomic claim: `runCloudy.select_pending`

The SELECT → UPDATE → verify dance is replaced by a **single atomic statement**:

```sql
UPDATE pending SET N = LAST_INSERT_ID(N), procID = <id>, status = 1, date_running = now()
WHERE status = 0 [AND priority = <p>] ORDER BY N LIMIT 1
```

- `rowcount = 0` ⇒ queue empty; otherwise the claimed `N` is read from
  `last_rowid`/`SELECT LAST_INSERT_ID()` on the same connection (a connection-scoped MySQL
  idiom — safe because every thread owns its `MdB`).
- Two workers on two machines **cannot** claim the same model: InnoDB row locking makes the
  UPDATE re-evaluate `status = 0` after any lock wait.
- Priority weighting is preserved: one cheap
  `SELECT priority, count(*) ... WHERE status = 0 GROUP BY priority` reproduces the exact
  row-level weighting of the old code (weight ∝ count × 4^(Pmax−P)); if the chosen priority
  drains between the two statements, one retry without the filter follows. Net cost:
  **4 queries + a full-table fetch → 2 queries.** Within a priority, models are now claimed
  in FIFO (`ORDER BY N`) order instead of random order — the set of executed models is
  unchanged.
- New module-level utility (manual — never automatic):

  ```python
  use3MdB.requeue_stale(MdB=..., older_than_hours=48, statuses=(1,))
  ```

  puts crashed workers' models back to `status=0, procID=-1` when `date_running` is older
  than the horizon. Choose a horizon much larger than the longest Cloudy run.
- Optional empty-queue backoff: `manage3MdB(..., max_sleep_time=...)` doubles the poll sleep
  on consecutive empty polls up to the maximum, and resets on success. Default = fixed 10 s,
  as before.
- `runCloudy.get_ID` uses `last_rowid` instead of a `SELECT last_insert_id()`.

### 3.5 Schema suggestion (`initSQL.py`)

New pending tables are created with a composite index serving both the priority scan and the
claim UPDATE. For **existing** deployments run once:

```sql
ALTER TABLE <pending_table> ADD KEY `status_priority` (`status`, `priority`);
```

(Optional — the pipeline is correct without it, just slower on large pending tables.)

### 3.6 `CloudyModel` reading (`c1d/cloudy_model.py`)

- **`_i_emis`**: label → index lookups now use a dict, lazily rebuilt whenever
  `len(emis_labels)` changes (blend labels are appended after the model is read). Lookup
  precedence (`emis_labels_13` first, then `_17`) is preserved. O(n²) → O(n) per
  `insert_model`, per cut.
- **`read_outputs`**: a pandas fast path (`_read_outputs_pandas`) handles the standard call
  shapes (`names=True` or an explicit name string; `usecols`, `case_sensitive`,
  `skip_header`) and falls back to the untouched `np.genfromtxt` path on any doubt or error.
  The fast path is **bit-identical** to genfromtxt:
  - column names go through numpy's own `NameValidator` (same sanitization: `#` deleted,
    spaces → `_`, `case_sensitive='upper'` for `.emis`/`.lin`);
  - `float_precision='round_trip'` reproduces Python's float parsing exactly (the default
    pandas C parser differs in the last bit);
  - single-row files yield the same 0-d structured array; empty files yield the same
    warning + `None`.
- **Element trimming (opt-in)**: `OVN_dic['list_elem']` restricts which `.ele_X` files
  `writeTab.read_model` loads. The default remains `LIST_ALL_ELEM` because the standard
  abion/teion tables cover all 30 elements.

### 3.7 Packaging

- `pyproject.toml`: `sqlalchemy>=2.0` added to the `mysql`/`full` extras and a new `db`
  extra (`pip install pyCloudy[db]`).
- `Config.py` detects `INSTALLED['sqlalchemy']`; `MdB` raises a clear error if SQLAlchemy is
  missing.

---

## 4. Measured results

All measurements on this machine (SQLite in-memory for SQL counts; the network gain on a
real MariaDB is much larger since every eliminated statement was a WAN round-trip).

| Hot spot | Before | After |
|---|---|---|
| Populate 1,000 pending models | 2,001 SQL statements, 1,000 commits, 1.25 s (old code: 3,000 statements / 3,000 commits) | **7 statements, 2 commits, 0.02 s** (`buffer_size=500`) |
| Populate a 145k grid (extrapolated round-trips) | ≈435,000 | **≈600** |
| Claim one model (priorities on) | 4 queries incl. a fetch of *all* pending rows | **2 queries, atomic, no bulk fetch** |
| Schema queries per model (5 cuts) | ≈8 `SHOW COLUMNS` + 6 lines-table SELECTs | **0** (all cached per thread) |
| Emission-label lookups (300 lines × 7 cuts) | 26 ms (`np.argwhere` scans) | **2.7 ms (≈10×)** |
| Reading a 2000-zone × 300-line `.emis` | 0.37 s (`genfromtxt`) | **0.30 s, bit-identical** (≈1.3×; ≈3× available with `float_precision='high'` at the cost of last-bit differences) |
| Worker crash while holding a model | stuck at status=1 forever | `requeue_stale()` recovers it |
| `'` in a comment/ref/filename | broken SQL statement | handled (bound parameters) |

---

## 5. Tests

Three new test files, runnable without MySQL, Cloudy, or network access:

```bash
pytest tests/test_mdb_sql.py tests/test_writetab_golden.py tests/test_read_outputs.py
# 40 passed
```

- **`tests/test_mdb_sql.py`** — the `MdB` layer against in-memory SQLite
  (`use_engine()`): bound params, `last_rowid`, all select formats, `get_fields` caching
  (verified with an `ALTER TABLE`), error handling leaves the connection usable;
  `writePending` unbuffered vs buffered (row counts, `FILE = name_N` renaming, `last_N`,
  flush-on-key-change). The MySQL-only statements (atomic claim, `requeue_stale`) are
  asserted at the SQL-text level with a recording fake: claim shape
  (`LAST_INSERT_ID(N)`, `ORDER BY N LIMIT 1`, priority filter), empty-queue path,
  `INTERVAL ... HOUR` requeue.
- **`tests/test_writetab_golden.py`** — end-to-end `writeTab.insert_model` on the real
  Cloudy outputs `tests/models/M17` against a SQLite schema: every inserted value is checked
  against the corresponding `CloudyModel` computation (`get_emis_vol/rad`, `get_ab_ion_*`,
  `get_T0_*`), the mass-cut loop produces a distinct smaller row, the final pending status
  is 50, and a **reused** `writeTab` does not leak values (a field set for model 1 comes out
  NULL for model 2).
- **`tests/test_read_outputs.py`** — pandas-vs-genfromtxt equivalence on every pipeline
  fixture (`.rad`, `.phy`, `.cont`, `.emis`, all `.ele_X`): identical dtype names, shapes,
  and **exact** values; single-row 0-d case; empty-file `None` case; `_i_emis` dict vs
  `argwhere` equivalence, unknown-label warning, cache rebuild after appending a blend
  label; spot checks of a fully read model.

---

## 6. Migration notes / operational checklist

1. **Dependencies**: `pip install sqlalchemy>=2.0` (plus `pymysql` as before), or
   `pip install pyCloudy[db]`.
2. **Nothing else is mandatory.** All behavior-affecting features are opt-in; a deployment
   that changes nothing gets the caching, the atomic claim, the connection-drop resilience
   and the faster reader for free.
3. Recommended first contact with the production DB: run a few read-only `select_dB`
   queries through the new `MdB`, then a small populate **without** `buffer_size` (identical
   semantics), then a batched populate.
4. Optional, per deployment:
   - `ALTER TABLE <pending> ADD KEY status_priority (status, priority);`
   - `writePending(..., buffer_size=500)` + `flush()` in populate scripts;
   - `manage3MdB(..., status_mode='batched', max_sleep_time=300)`;
   - a periodic manual `requeue_stale(...)` after machine crashes;
   - `OVN_dic['list_elem']` for custom schemas that don't store all 30 elements;
   - `CloudyModel._read_outputs_pandas` uses `float_precision='round_trip'` (bit-identical
     to genfromtxt); the pandas `'high'` parser is ~2× faster on reads with last-bit
     (1e-16 relative) differences, but is not exposed as an option.

### Behavior changes to be aware of

| Change | Impact |
|---|---|
| Atomic claim | Strictly safer; within a priority, models are claimed FIFO instead of random order; the "currentID != procID" warning no longer exists (the race it detected is impossible now). |
| Buffered populate | Rows become visible to workers per batch, not per row; `last_N` valid only after `flush()`. Opt-in. |
| temis insert | Labels without a matching `T_<label>` column are skipped (before: the whole temis INSERT failed). |
| `exec_dB` errors | The real driver error is raised through the logger (before: sometimes a confusing `UnboundLocalError`). |
| `format_='pandas'` | Works again (`pd.read_sql`); the old code crashed with any modern pandas. |
