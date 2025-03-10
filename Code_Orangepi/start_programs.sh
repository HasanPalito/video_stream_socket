#!/bin/bash
/usr/bin/python3 /root/program/mqtt/video1.py &
/usr/bin/python3 /root/program/mqtt/servo_kanan.py &
/usr/bin/python3 /root/program/mqtt/servo_kiri.py &
/usr/bin/python3 /root/program/mqtt/sensor.py &
/usr/bin/python3 /root/program/mqtt/motor.py &
wait
