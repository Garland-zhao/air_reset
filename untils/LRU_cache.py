from collections import OrderedDict


class RegionLruCache:
    """python 实现 LRU cache"""

    def __init__(self, maxsize=1000):
        self.cache = OrderedDict()
        self.max_size = maxsize

    def __contains__(self, key):
        return key in self.cache

    def __getitem__(self, key):
        return self.cache[key]

    def get_cache_size(self):
        return self.max_size

    def update_cache(self, key, value):
        if key not in self.cache and self.max_size <= len(self.cache):
            self.cache.popitem(last=False)
        self.cache[key] = value
