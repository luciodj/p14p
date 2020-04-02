 SERIAL_PORT=`python -m serial.tools.list_ports 03eb:2175 -q`
 src/tools/ipm.py -s $SERIAL_PORT -f src/platform/avr_da/pmfeatures.py
 