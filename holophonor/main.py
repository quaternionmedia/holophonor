from holophonor.holospecs import Holophonor
from holophonor.freewheeling import Fweelin
from holophonor.qsynth import Qsynth
from holophonor.launchpadX import LaunchpadX
from holophonor.launchpadMK2 import LaunchpadMK2
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
    pm.register(
        Fweelin(
            pm.hook,
            'a2j:FreeWheeling',
            client_name='holo->fweelin',
        )
    )
    pm.register(
        LaunchpadX(
            pm.hook,
            'Launchpad X LPX MIDI In',
            client_name='holo->launchpadX',
        )
    )
    # pm.register(LaunchpadMK2(pm.hook, 'Launchpad MK2:Launchpad MK2 MIDI 1', client_name='holo->LaunchpadMK2'))
    pm.register(Qsynth(pm.hook, 'ElectricMayhem:midi_00', client_name='holo->qsynth'))
    return pm


if __name__ == '__main__':
    main()
