from martian_lights.helpers.schema import action_put, condition

def group_toggle(
	ml,
	group_id,
	conditions,
	display_name='Toggle'
):
	"""
	A behavior that makes a button cycle turn a group on or off.
	"""
	any_on_addr = f'/groups/{group_id}/state/any_on'
	group_action_addr = f'/groups/{group_id}/action'

	for cond_i, cond in enumerate(conditions):
		ml.resource(
			'rules',
			f'on_{cond_i}',
			{
				'name': f'{display_name} on',
				'conditions': cond + [condition(any_on_addr, 'eq', 'false')],
				'actions': [action_put(group_action_addr, {'on': True})]
			}
		)

		ml.resource(
			'rules',
			f'off_{cond_i}',
			{
				'name': f'{display_name} off',
				'conditions': cond + [condition(any_on_addr, 'eq', 'true')],
				'actions': [action_put(group_action_addr, {'on': False})]
			}
		)
