# PNGTuber Audio Reactive App

This project is a **PNGTuber-like application** that reacts to audio levels from a specified application. It alternates between two images based on audio input and allows for easy customization using a `config.json` file. The project includes the source code, images, and configuration file for setup.

---

## Features

- **Audio Monitoring**: Reacts to the audio levels of a target application.
- **Dynamic Image Switching**: Alternates between two images based on the audio volume threshold.
- **Customizable Settings**: Includes a `config.json` file to adjust settings without modifying the code.
- **Resizable Images**: Allows resizing images using mouse scroll or hotkeys.

---

## What's Included

This repository includes the following files:

- **`script.py`**: The source code of the project.
- **`script.exe`**: The runnable executable of the projectt.
- **`config.json`**: A configuration file to customize settings.
- **`640px-Neurofumo.png`**: Image displayed when audio levels are high.
- **`640px-Neurofumodark.png`**: Image displayed when audio levels are low.

## Configuration Guide

The `config.json` file allows users to customize the app's behavior. Below is an explanation of each setting:

| Key                  | Description                                                                                  | Default Value          |
|----------------------|----------------------------------------------------------------------------------------------|------------------------|
| `TARGET_APP`         | Name of the application whose audio levels will be monitored.                                | `"EDCoPilot.exe"`      |
| `VOLUME_THRESHOLD`   | The volume level threshold for switching images. Accepts values between `0.0` and `1.0`.    | `0.2`                  |
| `IMAGE_HIGH_VOLUME`  | Path to the image displayed when audio levels are above the threshold.                       | `"640px-Neurofumo.png"`|
| `IMAGE_LOW_VOLUME`   | Path to the image displayed when audio levels are below the threshold.                       | `"640px-Neurofumodark.png"`|
| `MAX_IMAGE_SIZE`     | The maximum size (in pixels) for the displayed images.                                       | `700`                  |
| `INCREASE_SIZE_KEY`  | Hotkey to increase the image size.                                                           | `"Up"`                 |
| `DECREASE_SIZE_KEY`  | Hotkey to decrease the image size.                                                           | `"Down"`               |

### Example `config.json`

```json
{
    "TARGET_APP": "YourApp.exe",
    "VOLUME_THRESHOLD": 0.3,
    "IMAGE_HIGH_VOLUME": "images/high_volume.png",
    "IMAGE_LOW_VOLUME": "images/low_volume.png",
    "MAX_IMAGE_SIZE": 800,
    "INCREASE_SIZE_KEY": "Up",
    "DECREASE_SIZE_KEY": "Down"
}