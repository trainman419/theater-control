#!/usr/bin/env python

import os
import yaml
import argparse
import lirc
import cec
import tempfile
import subprocess
import threading
import time

def main():
    parser = argparse.ArgumentParser(description='Control a home theater system')
    parser.add_argument('-c', '--config', help="Config File (yaml)",
            default="theater.yaml")
    parser.add_argument('-n', '--name', help="Lirc name", 
            default="theater_control")
    parser.add_argument('-w', '--wait', help='time in seconds to wait before stating', default='0.0')

    args = parser.parse_args()

    timeout = float(args.wait)
    if timeout:
        print("Waiting '{0}' seconds before starting...".format(timeout))
        time.sleep(timeout)

    print("Loading config file from '{0}'...".format(args.config))
    config = yaml.load(open(args.config)) 
    # CEC setup
    print("Initializing CEC...")
    cec.init()

    if 'avr_port' in config:
      cec.set_port(config['avr'], config['avr_port'])

    devices = [ cec.Device(i) for i in config['other_devices'] ]

    tv = cec.Device(config['tv'])
    avr = cec.Device(config['avr'])

    # Lirc setup
    lircname = args.name

    lirctmp = os.path.join(tempfile.mkdtemp(), 'lirc.conf')
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
    config = home
end
"""%(config['home'], lircname))
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

    p = None

    subprocess.Popen(os.path.join(os.path.dirname(__file__), 'notify.py'), shell=True)
    os.environ['XBMC_HOME'] = "/opt/plexhometheater/share/XBMC"

    while True:
        print("here")
        codes = lirc.nextcode()
        for code in codes:
            print code
            if code == 'power':
                tv_is_on = False
                try:
                    tv_is_on = tv.is_on()
                except IOError as exc:
                    print('%s' % exc)
                    continue
                if tv_is_on:
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
            elif code == 'home':
                if p is not None:
                    print("killing plex")
                    p.terminate()
                    if p.poll() is None:
                        threading.Timer(3.0, p.kill).start()
                    p.wait()
                    p = None
                else:
                    print("starting new plex")
                    p = subprocess.Popen(['/opt/plexhometheater/bin/plexhometheater'], shell=False)

if __name__ == '__main__':
    main()

