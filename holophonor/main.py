from holophonor.holospecs import Holophonor
from holophonor.freewheeling import Fweelin
from holophonor.launchpadX import LaunchpadX
from pluggy import PluginManager


def main():
    pm = get_plugin_manager()
    try:
        while True:
            input()
    except Exception as e:
        print(e)
    finally:
        pm.hook.close()

def get_plugin_manager():
    pm = PluginManager('holophonor')
    pm.add_hookspecs(Holophonor)
    pm.register(Fweelin(pm.hook, 'FreeWheeling:FreeWheeling IN 1', client_name='holo->fweelin'))
    pm.register(LaunchpadX(pm.hook, 'Launchpad X:Launchpad X MIDI 2', client_name='holo->launchpadX'))
    return pm


if __name__ == '__main__':
    main()