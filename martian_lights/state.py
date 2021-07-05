import json
import os

class State:
	def __init__(self, path):
		self._path = path
		self._store = {}
		self._load()

	def _load(self):
		with open(self._path) as f:
			self._store = json.load(f)

	def save(self):
		os.replace(self._path, f'{self._path}.backup')
		with open(self._path, 'w') as f:
			json.dump(self._store, f, indent=2)

	def get_resource_id(self, kind, name):
		return self._store.get(kind, {}).get(name)

	def store_resource_id(self, kind, name, id_):
		assert id_ is not None

		if kind not in self._store:
			self._store[kind] = {}

		self._store[kind][name] = id_

	def delete_resource(self, kind, name):
		del self._store[kind][name]

	def list_resources(self):
		for kind, resources in self._store.items():
			for name, id_ in resources.items():
				yield (kind, name, id_)
