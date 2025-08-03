
import Config

class ConfigContext():
    def __init__(self):
        self.serverconfig = Config.Config(self)

class ServerState:
    def __init__(self, configcontext):
        self._configcontext = configcontext

    # PLUGIN STATUS
    plugins = None

    @property
    def info_dict(self):
        return {
        }

