Inu-NC: G-Code orientated IoT framework
=======================================
This is a sister project to the `Inu-Py` framework, but where the original Inu-Py framework is NATS-based, this framework operates using G-Code over a permanent TCP connection. 

Inu-Py is intended for a wide range of single-purpose devices. Inu-NC has a robotics focus and trades the robust NATS message stream history for a fire-and-forget approach. Missed messages will be ignored, however device state will be updated upon reconnection.

| Inu-NC                             | Inu-Py                                                          |
| ---------------------------------- | --------------------------------------------------------------- |
| Client-Server TCP architecture     | Decentralised with streams                                      |
| Missed messages lost               | Can recover (but doesn't) from missing events                   |
| Requires a control plane           | Devices can listen to other devices without centralisation      |
| Robotics focus                     | Sensor focus                                                    |
| Multiple entities per device       | Single-purpose devices                                          |

Control Planes
--------------
Inu-NC is useless without a control plane. Where Inu-Py could allow a device to listen directly to another device, Inu-NC relies on a centralised control plane to communicate between devices.

Any control plane implementation should be configured with a list of devices and their respective configuration. This includes all G-Code required to execute robotics on the devices. The control plane should be the centralised source for configuration.

### Home Assistant
There is a `hass` component which is the default implementation for a Inu-NC control plane. Using Home Assistant is the intended (but not required) use of this project.

See the `hass/` folder for more on the Home Assistant component.


G-Code Support
--------------
The Home Assistant control plane has support for the bundled ESP32 implementation, along with support for grbl and grblHAL devices. This allows you to interact with robotics devices in the same manner you would interact with a CNC machine.

