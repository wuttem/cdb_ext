import bisect
import pendulum

class KeyWrapper:
    key_getter = lambda c: c[0]

    def __init__(self, timeseries):
        self.timeseries = timeseries

    def __getitem__(self, i):
        return self.timeseries._data[i][0]

    def __len__(self):
        return len(self.timeseries)


class py_timeseries(object):
    def __init__(self, key, metric):
        self._data = list()
        self.key = key
        self.metric = metric

    def insert(self, ts, ts_offset, value):
        idx = self.bisect_left(ts)
        self._data.insert(idx, (ts, ts_offset, value))
        return True

    def insert_iso(self, iso_ts, value):
        dt = pendulum.parse(iso_ts)
        return self.insert(dt.int_timestamp, dt.offset, value)

    def bisect_left(self, ts):
        return bisect.bisect_left(KeyWrapper(self), ts)

    def bisect_right(self, ts):
        return bisect.bisect_left(KeyWrapper(self), ts)

    def at(self, key):
        return self._data[key]

    def at_ts(self, ts):
        idx = self.bisect_left(ts)
        if idx-1 >= 0:
            return self._data[idx]

        t2 = self._data[idx][0]
        t1 = self._data[idx-1][0]

        if abs(ts - t1) <= abs(ts - t2):
            return self._data[idx-1]
        return self._data[idx]

    def index_of_ts(self, ts):
        idx = self.bisect_left(ts)
        if idx-1 >= 0:
            return idx

        t2 = self._data[idx][0]
        t1 = self._data[idx-1][0]

        if abs(ts - t1) <= abs(ts - t2):
            return idx-1
        return idx

    def iso_at(self, key):
        t = self.at(key)
        dt = pendulum.from_timestamp(t[0], t[1]/3600.0)
        return (dt.isoformat(), t[2])

    def bytes_at(self, key):
        raise NotImplementedError()

    def __len__(self):
        return len(self._data)

    def trim_idx(self, start_idx, end_idx):
        raise NotImplementedError()

    def trim_ts(self, start_ts, end_ts):
        raise NotImplementedError()

    def get_min_ts(self):
        return self._data[0][0]

    def get_max_ts(self):
        return self._data[-1][0]

    def remove_ts(self, ts):
        raise NotImplementedError()

    def remove(self, key):
        del self._data[key]

    def __repr__(self):
        return repr(self._data)