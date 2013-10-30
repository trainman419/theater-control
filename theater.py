#!/usr/bin/env python

import os
import yaml
import argparse
import lirc

def main():
    parser = argparse.ArgumentParser(description='Control a home theater system')
    parser.add_argument('-c', '--config', help="Config File (yaml)",
            default="theater.yaml")
    parser.add_argument('-n', '--name', help="Lirc name", 
            default="theater_control")

    args = parser.parse_args()

    config = yaml.load(open(args.config)) 
    lircname = args.name

    lirctmp = os.tmpnam()
    print "Lirc config temporary: %s"%(lirctmp)
    
    with open(lirctmp, "w") as lircconf:
        for i in config['inputs']:
            print i
            lircconf.write("""begin
    button = %s
    prog = %s
    config = %s
end
"""%(i['button'], lircname, i['button']))

    lirc.init(lircname, lirctmp)

    while True:
        print lirc.nextcode()

if __name__ == '__main__':
    main()
