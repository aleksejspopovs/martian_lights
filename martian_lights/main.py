import importlib.util
import logging
import os
import sys

from martian_lights.core import MartianLights

def load_config(config_path):
	spec = importlib.util.spec_from_file_location('config', config_path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module

def read_config_value(config, name, env_var):
	if env_var in os.environ:
		return os.environ[env_var]
	if hasattr(config, name):
		return getattr(config, name)

	logging.error(
		(
			'Configuration value %s not found, please supply by setting it in '
			'the config file or in the environment variable %s.'
		),
		name,
		env_var,
	)
	sys.exit(1)

def initialize_ml(config):
	state_path = read_config_value(config, 'state_path', 'HUE_STATE_PATH')
	bridge_addr = read_config_value(config, 'bridge_addr', 'HUE_BRIDGE_ADDR')
	bridge_username = read_config_value(config, 'bridge_username', 'HUE_BRIDGE_USERNAME')
	return MartianLights(state_path, bridge_addr, bridge_username)

def main():
	if len(sys.argv) != 2:
		print('USAGE:')
		print(f'{sys.argv[0]} config.py')
		sys.exit(1)

	logging.basicConfig(
		level=logging.INFO,
		format='[%(levelname)s] %(message)s'
	)

	config_path = sys.argv[1]
	config = load_config(config_path)
	ml = initialize_ml(config)

	ran_cleanly = True

	try:
		config.run(ml)
	except Exception as error:
		ran_cleanly = False
		logging.error(repr(error))

	if ran_cleanly:
		ml.delete_ghost_resources()

	ml.save_state()

	if not ran_cleanly:
		sys.exit(1)

if __name__ == '__main__':
	main()
