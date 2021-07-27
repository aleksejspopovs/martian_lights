import logging

from martian_lights.api_client import ApiClient, ApiError
from martian_lights.state import State


class Error(Exception):
	pass


class DuplicateResourceError(Error):
	pass


class MartianLights:
	def __init__(self, state_path, api_host, api_key):
		self._logger = logging.getLogger('martian_lights.execution')

		self._api = ApiClient(api_host, api_key)
		self._state = State(state_path)

		self._live_resources = set()

	def _mark_resource_live(self, kind, name):
		self._live_resources.add((kind, name))

	def _resource_is_live(self, kind, name):
		return (kind, name) in self._live_resources

	def _compute_differing_attributes(self, real, desired):
		result = []
		for key, desired_value in desired.items():
			if desired_value != real.get(key):
				result.append(key)
		return result

	def resource(self, kind, name, desired_attributes):
		log = lambda msg, *args: self._logger.info(f'{kind}.{name}: {msg}', *args)
		log_error = lambda msg, *args: self._logger.error(f'{kind}.{name}: {msg}', *args)

		if self._resource_is_live(kind, name):
			raise DuplicateResourceError(f'{kind}.{name}')
		self._mark_resource_live(kind, name)

		log('Refreshing.')

		id_ = self._state.get_resource_id(kind, name)
		real_attributes = None

		if id_ is not None:
			log('Found ID in state: %s', id_)

			try:
				real_attributes = self._api.read_resource(kind, id_)
			except ApiError as error:
				if error.is_resource_unavailable():
					log('ID does not exist any more, recreating.')
					id_ = None
				else:
					raise error

		if id_ is not None:
			diff_attributes = self._compute_differing_attributes(real_attributes, desired_attributes)
			if not diff_attributes:
				log('Resource is up to date, no action needed.')
			else:
				log('Attributes %s are incorrect, updating.', diff_attributes)
				attributes_to_set = {k:desired_attributes[k] for k in diff_attributes}

				try:
					self._api.update_resource(
						kind,
						id_,
						attributes_to_set
					)
				except ApiError as error:
					log_error('Could not update resource with attributes: %s', attributes_to_set)
					raise error

				log('Updated.')
		else:
			log('Creating.')

			try:
				id_ = self._api.create_resource(kind, desired_attributes)
			except ApiError as error:
				log_error('Could not create resource with attributes: %s', desired_attributes)
				raise error

			log('Created with ID %s.', id_)

			self._state.store_resource_id(kind, name, id_)

		return id_

	def read_resource(self, kind, id_):
		return self._api.read_resource(kind, id_)

	def namespace(self, namespace):
		return NamespacedML(self, namespace)

	def delete_ghost_resources(self):
		self._logger.info('Checking for ghost resources.')

		# Make a copy here to avoid changing the state while iterating over it.
		all_resources = list(self._state.list_resources())

		for kind, name, id_ in all_resources:
			if not self._resource_is_live(kind, name):
				self._logger.info('Resource %s.%s with ID %s is a ghost, deleting.', kind, name, id_)
				try:
					self._api.delete_resource(kind, id_)
				except ApiError as error:
					# Ignore "resource not found" errors.
					if not error.is_resource_unavailable():
						self._logger.info('Looks like it was already gone.')
						raise error

				self._state.delete_resource(kind, name)

	def save_state(self):
		self._logger.info('Updating local state.')
		self._state.save()


class NamespacedML:
	def __init__(self, ml, namespace):
		self._ml = ml
		self._namespace = namespace

	def resource(self, kind, name, desired_attributes):
		return self._ml.resource(
			kind,
			f'{self._namespace}/{name}',
			desired_attributes,
		)

	def read_resource(self, kind, id_):
		return self._ml.read_resource(kind, id_)

	def namespace(self, namespace):
		return NamespacedML(self._ml, f'{self._namespace}/{namespace}')
