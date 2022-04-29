#!/usr/bin/python
"""
# Trecho da documentação sobre gerenciamento de energia kernel Linux.

https://www.kernel.org/doc/html/v4.14/driver-api/usb/power-management.html#
https://www.kernel.org/doc/html/v4.14/driver-api/usb/power-management.html#what-is-power-management

Dynamic suspends occur when the kernel decides to suspend an idle device. 
This is called autosuspend for short. In general, a device won’t be 
autosuspended unless it has been idle for some minimum period of time, 
the so-called idle-delay time.

(...)

If a device has been autosuspended and a program tries to use it, the 
kernel will automatically resume the device (autoresume).

(...)

power/control

    This file contains one of two words: on or auto. You can write those words to the file to change the device’s setting.

        on means that the device should be resumed and autosuspend is not allowed. (Of course, system suspends are still allowed.)
        auto is the normal state in which the kernel is allowed to autosuspend and autoresume the device.

    (In kernels up to 2.6.32, you could also specify suspend, meaning that the device should remain suspended and autoresume was not allowed. This setting is no longer supported.)

power/autosuspend_delay_ms

    This file contains an integer value, which is the number of milliseconds the device should remain idle before the kernel will autosuspend it (the idle-delay time). The default is 2000. 0 means to autosuspend as soon as the device becomes idle, and negative values mean never to autosuspend. You can write a number to the file to change the autosuspend idle-delay time.


Writing -1 to power/autosuspend_delay_ms and writing on to power/control 
do essentially the same thing – they both prevent the device from being 
autosuspended. 

https://www.kernel.org/doc/html/v4.14/driver-api/usb/power-management.html#changing-the-default-idle-delay-time


The default autosuspend idle-delay time (in seconds) is controlled by a module parameter in usbcore. You can specify the value when usbcore is loaded. For example, to set it to 5 seconds instead of 2 you would do:

modprobe usbcore autosuspend=5

Equivalently, you could add to a configuration file in /etc/modprobe.d a line saying:

options usbcore autosuspend=5

(...)

by default the kernel disables autosuspend (the power/control attribute is initialized to on) for all devices other than hubs.

"""

import subprocess
import sys

from pyudev import Context


def search_usb_devices(vendor_id, model_id):
    context = Context()
    # sysfs name structure for usb -> http://www.linux-usb.org/FAQ.html#i6
    # bus-port.port.port...
    for dev in context.list_devices(subsystem="usb"):
        # vendor_id in dev and model_id in dev ???
        if dev.get("ID_VENDOR_ID") == vendor_id and dev.get("ID_MODEL_ID") == model_id:
            # return bus-port
            return dev.sys_name


def write(device, file, param):
    sysfs_path = f"/sys/bus/usb/devices/{device}/power/{file}"
    subprocess.run(f"echo {param} > {sysfs_path}", shell=True)


def autosuspend(device, delay_ms):
    write(device, "autosuspend_delay_ms", delay_ms)


def control(device, delay=0):

    if delay > 0:
        autosuspend(device, delay * 1000)
    elif delay < 0:
        autosuspend(device, -1)
    else:
        autosuspend(device, 2 * 1000)


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "--idle-delay",
        type=int,
        help="The number of seconds the device should remain idle before \
        the kernel will autosuspend it (the idle-delay time). The default \
        is 2. 0 means to autosuspend as soon as the device becomes idle, \
        and negative values mean never to autosuspend." 
    )
    parser.add_argument(
        "--device",
        type=str,
        help="A device is composed of `vendor_id:model_id`. \
        In the terminal run `lsusb` to get them."
    )
    parser.add_argument(
        "--devices",
        nargs="*",
        type=str,
        help="List of devices, where each one is composed of `vendor_id:model_id`.\
        In the terminal run `lsusb` to get them."
    )
    args = parser.parse_args()
    usb_devices = []

    if args.devices is not None:
        usb_devices = [tuple(device.split(":")) for device in args.devices]
    else:
        usb_devices = [tuple(args.device.split(":"))]

    if args.idle_delay is not None:
        for device in usb_devices:
            device = search_usb_devices(*device)
            control(device=device, delay=args.idle_delay)
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
