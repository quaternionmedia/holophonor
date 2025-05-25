from holophonor.holospecs import Holophonor
from holophonor.freewheeling import Fweelin
from holophonor.qsynth import Qsynth
from holophonor.launchpadX import LaunchpadX
from holophonor.launchpadMK2 import LaunchpadMK2
from holophonor.pipewire import Pipewire
from pluggy import PluginManager
from loguru import logger as log


def main():
    from sys import stderr

    log.configure(handlers=[{'sink': stderr, 'level': 'TRACE'}])
    pm = get_plugin_manager()
    log.success('Holophonor: ready!')
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
    # pm.register(
    #     Fweelin(
    #         pm.hook,
    #         'a2j:FreeWheeling',
    #         client_name='holo->fweelin',
    #     )
    # )
    pm.register(
        LaunchpadX(
            pm.hook,
            'Launchpad X LPX MIDI In',
            client_name='holo->launchpadX',
        )
    )
    # pm.register(Qsynth(pm.hook, 'ElectricMayhem:midi_00', client_name='holo->qsynth'))
    pm.register(Pipewire(pm.hook, 'Pipewire', client_name='holo->pipewire'))
    return pm


if __name__ == '__main__':
    main()
