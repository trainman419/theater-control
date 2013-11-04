#!/usr/bin/env python

import os
import yaml
import argparse
import lirc
import cec

def main():
    parser = argparse.ArgumentParser(description='Control a home theater system')
    parser.add_argument('-c', '--config', help="Config File (yaml)",
            default="theater.yaml")
    parser.add_argument('-n', '--name', help="Lirc name", 
            default="theater_control")

    args = parser.parse_args()

    config = yaml.load(open(args.config)) 
    # CEC setup
    cec.init()

    devices = [ cec.Device(i) for i in config['other_devices'] ]

    tv = cec.Device(config['tv'])
    avr = cec.Device(config['avr'])

    # Lirc setup
    lircname = args.name

    lirctmp = os.tmpnam()
    print "Lirc config temporary: %s"%(lirctmp)
    
    with open(lirctmp, "w") as lircconf:
        lircconf.write("""begin
    button = %s
    prog = %s
    config = power
end
"""%(config['power_button'], lircname))
        lircconf.write("""begin
    button = %s
    prog = %s
    config = volup
end
"""%(config['volup_button'], lircname))
        lircconf.write("""begin
    button = %s
    prog = %s
    config = voldown
end
"""%(config['voldown_button'], lircname))
        lircconf.write("""begin
    button = %s
    prog = %s
    config = volmute
end
"""%(config['volmute_button'], lircname))
        for i in config['inputs']:
            print i
            lircconf.write("""begin
    button = %s
    prog = %s
    config = %s
end
"""%(i, lircname, i))

    lirc.init(lircname, lirctmp)

    inputs = config['inputs']

    print inputs

    while True:
        codes = lirc.nextcode()
        for code in codes:
            if code == 'power':
                if tv.is_on():
                    method = cec.Device.standby
                    print "TV is on; turning it off"
                else:
                    method = cec.Device.power_on
                    print "TV is off; turning it on"
                method(tv)
                method(avr)
                for d in devices:
                    method(d)
            elif code == 'volup':
                print "Volume up"
                cec.volume_up()     
            elif code == 'voldown':
                print "Volume down"
                cec.volume_down()     
            elif code == 'volmute':
                print "Volume mute toggle"
                cec.toggle_mute()     
            elif code in inputs:
                i = inputs[code]
                print i
                if 'av_input' in i:
                    avr.set_av_input(i['av_input'])
                if 'audio_input' in i:
                    avr.set_audio_input(i['audio_input'])

if __name__ == '__main__':
    main()
