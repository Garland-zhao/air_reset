from collections import OrderedDict


class RegionLRUCache:
    """python 实现 LRU cache"""

    def __init__(self, maxsize=100):
        self.cache = OrderedDict()
        self.max_size = maxsize

    def __contains__(self, item):
        return item in self.cache

    def __getitem__(self, item):
        if item in self.cache:
            return self.cache[item]
        else:
            raise ValueError(f'{item} not in Cache')

    @property
    def cache_size(self):
        return self.max_size

    def update(self, key, value):
        if key not in self.cache and self.max_size <= len(self.cache):
            self.cache.popitem(last=False)
        self.cache[key] = value
