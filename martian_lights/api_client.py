import requests

class ApiError(Exception):
	def __init__(self, error, address, description):
		self.error = error
		self.address = address
		self.description = description

	def __str__(self):
		return f'API error {self.error} on {self.address}: {self.description}'

	def is_resource_unavailable(self):
		return self.error == 3

class ApiClient:
	def __init__(self, host, api_key):
		self._host = host
		self._api_key = api_key
		self._session = requests.Session()

	def _resource_path(self, kind, id_=None):
		path = f'http://{self._host}/api/{self._api_key}/{kind}'
		if id_ is not None:
			path += f'/{id_}'
		return path

	def _request(self, method, resource_kind, resource_id=None, body=None):
		path = self._resource_path(resource_kind, resource_id)
		responses = self._session.request(method, path, json=body).json()

		# Bridge API response are generally of the form
		# `[{"success": body}]` or `[{"error": body}]`.
		# However, when requesting a particular resource, success
		# responses just give you the actual resource, not wrapped
		# in any way. Errors are still wrapped the same way though.
		if (method == 'GET') and isinstance(responses, dict):
			return responses

		errors = [r['error'] for r in responses if 'error' in r]
		if errors:
			# Oops we'll just disregard all the others.
			first = errors[0]
			raise ApiError(first.get('type'), first.get('address'), first.get('description'))

		return [r['success'] for r in responses]

	def create_resource(self, kind, attributes):
		response = self._request('POST', kind, body=attributes)
		assert len(response) == 1
		return response[0]['id']

	def read_resource(self, kind, id_):
		return self._request('GET', kind, id_)

	def update_resource(self, kind, id_, attributes):
		self._request('PUT', kind, id_, body=attributes)

	def delete_resource(self, kind, id_):
		self._request('DELETE', kind, id_)
