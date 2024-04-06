import toml

current_config = {}


def current_config(section:str=None) -> dict:
    if section is None :
        return current_config
    else:
        if section in current_config:
            return current_config[section]
        else:
            raise ValueError("Config section '{section}' not found".format(section=section))


def load_config(path:str) -> dict:
    global current_config
    with open(path, 'r') as f:
        current_config = toml.load(f)
    return current_config


