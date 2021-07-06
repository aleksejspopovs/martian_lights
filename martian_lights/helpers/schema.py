def condition(address, operator, value=None):
	result = {
		'address': address,
		'operator': operator
	}

	if value is not None:
		result['value'] = value

	return result

def virtual_sensor(name):
	return {
		'name': name,
		'type': 'CLIPGenericStatus',
		'modelid': 'VARIABLE',
		'manufacturername': 'martian_lights',
		'swversion': '1.0',
		'uniqueid': '000000', # the bridge doesn't seem to care if these actually repeat
	}

def action_put(address, body):
	return {
		'address': address,
		'method': 'PUT',
		'body': body,
	}
