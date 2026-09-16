import copy
import uuid


def _matches(doc, query):
    for key, expected in query.items():
        actual = doc.get(key)
        if isinstance(expected, dict):
            if "$exists" in expected and (key in doc) != bool(expected["$exists"]):
                return False
            if "$in" in expected and actual not in expected["$in"]:
                return False
        elif actual != expected:
            return False
    return True


class _InsertResult:
    def __init__(self, inserted_id): self.inserted_id = inserted_id


class InMemoryCollection:
    def __init__(self): self.rows = []
    def find_one(self, query, projection=None):
        for row in self.rows:
            if _matches(row, query):
                return _project(row, projection)
        return None
    def find(self, query=None, projection=None):
        query = query or {}
        return [_project(row, projection) for row in self.rows if _matches(row, query)]
    def replace_one(self, query, replacement, upsert=False):
        for i, row in enumerate(self.rows):
            if _matches(row, query):
                self.rows[i] = copy.deepcopy(replacement)
                return
        if upsert: self.rows.append(copy.deepcopy(replacement))
    def delete_many(self, query):
        self.rows = [row for row in self.rows if not _matches(row, query)]
    def insert_one(self, document):
        item = copy.deepcopy(document)
        item.setdefault("_id", uuid.uuid4().hex)
        self.rows.append(item)
        return _InsertResult(item["_id"])
    def aggregate(self, pipeline):
        raise RuntimeError("Atlas aggregation unavailable in local memory mode")


def _project(row, projection):
    item = copy.deepcopy(row)
    if not projection: return item
    excludes = [key for key, value in projection.items() if value == 0]
    includes = [key for key, value in projection.items() if value == 1]
    if includes:
        return {key: item[key] for key in includes if key in item}
    for key in excludes: item.pop(key, None)
    return item


class InMemoryDB:
    def __init__(self): self._collections = {}
    def __getitem__(self, name):
        return self.__getattr__(name)

    def __getattr__(self, name):
        if name.startswith("_"): raise AttributeError(name)
        self._collections.setdefault(name, InMemoryCollection())
        return self._collections[name]
