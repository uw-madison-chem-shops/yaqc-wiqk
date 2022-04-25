__all__ = ["Config"]


import pathlib
import toml
import appdirs
from ._singleton import Singleton


class Config(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.path = pathlib.Path(appdirs.user_config_dir(appname="wiqk")) / "config.toml"
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.touch()

    def __getitem__(self, key):
        with open(self.path, "r") as f:
            out = toml.load(f)[key]
        return out

    def __setitem__(self, key, value):
        with open(self.path, "r") as f:
            out = toml.load(f)
        out[key] = value
        with open(self.path, "w") as f:
            toml.dump(out, f)
