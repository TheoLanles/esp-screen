# ESP32 Modes Controller

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration to control ESP32 display modes over Wi-Fi.

## Features

- **Mode Select** – Switch between Mode 1, Mode 2, and Mode 3
- **Mode Sensor** – Displays the currently active mode
- **Reboot Button** – Remotely reboot the ESP32

## Installation

### HACS (recommended)

1. Open **HACS** → **Integrations** → **⋮** → **Custom repositories**
2. Add `https://github.com/TheoLanles/esp-screen` as an **Integration**
3. Search for **ESP32 Modes Controller** and install it
4. Restart Home Assistant

### Manual

1. Copy the `custom_components/esp32_modes` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for **ESP32 Modes Controller**
3. Enter the IP address of your ESP32

## ESP32 Firmware

The `main/` directory contains the Arduino sketch for the ESP32. Flash it using the Arduino IDE with ESP32 board support.
