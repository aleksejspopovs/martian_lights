def merged_switch(
	ml,
	source_switch_ids,
	display_name='Merged switch'
):
	"""
	Creates a virtual switch that reports the same event as the source switches.

	Because the conditions in Hue's rules only support ANDs, not ORs, this is
	helpful for creating actions that can be performed by any of a group
	of switches.
	"""
	merged_switch_id = ml.resource(
		'sensor',
		'switch',
		{
			'name': display_name,
			'type': 'CLIPSwitch',
			'modelid': 'MERGED',
			'manufacturername': 'martian_lights',
			'swversion': '1.0',
			'uniqueid': '000000',
		},
	)

	for source_switch_id in source_switch_ids:
		ml.resource(
			'rule',
			f'from_{source_switch_id}',
			{
				'name': f'{display_name} from {source_switch_id}'
			}
		)

	return merged_switch_id
