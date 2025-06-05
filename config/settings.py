import os
import yaml
import logging


def get_settings(path):
    return Settings(path)


# Open config file, check config local
def open_settings_file(name):
    main_file = name

    if os.path.isfile(main_file):
        return open(main_file)

    logging.info("not contain file")
    return None  # Take care if the file is not exists


class Settings:
    def __init__(self, path):
        self.path = path
        self.settings = yaml.safe_load(open_settings_file(self.path))
        self._update_os_environ()

    def _update_os_environ(self):
        for env_name, env_value in os.environ.items():
            env_name_lower = env_name.lower()
            self._update_settings(env_name_lower, env_value)

    def __getitem__(self, name):
        hierarchy_names = name.lower().split("__")
        local_settings = self.settings
        for name in hierarchy_names:
            local_settings = local_settings.get(name)
            if not local_settings:
                break
        return local_settings

    def _update_settings(self, env_name, env_value):
        hierarchy_names = env_name.split('__')
        prev_settings = None
        prev_key = None
        local_settings = self.settings
        while hierarchy_names:
            if len(hierarchy_names) == 1:
                name = hierarchy_names.pop(0)
                if env_value.lower() in ['true', 'yes']:
                    env_value = True
                elif env_value.lower() in ['false', 'no']:
                    env_value = False
                local_settings[name] = env_value
            else:
                name = hierarchy_names.pop(0)
                if name in local_settings:
                    if not isinstance(local_settings[name], dict) and len(hierarchy_names) == 1:
                        prev_settings[prev_key][name] = {}
                        prev_settings = local_settings
                        prev_key = name
                        local_settings = local_settings[name]
                    else:
                        prev_settings = local_settings
                        prev_key = name
                        local_settings = local_settings[name]
                else:
                    local_settings[name] = {}
                    prev_settings = local_settings
                    prev_key = name
                    local_settings = local_settings[name]