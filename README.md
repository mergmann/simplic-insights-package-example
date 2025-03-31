# Simplic Insights example sensor package

This is an example sensor package for
[simplic-insights-collector](https://github.com/simplic/simplic-insights-collector)

You can use this as a template for creating sensor packages

## Creating a sensor package

1. Give your package a unique id
2. Create a new folder `sensors/<id>/`
3. Create `__init__.py` and `manifest.json`
4. Add id, version, name, description and dependencies to `manifest.json`
5. For each sensor:
   - Create and implement a Settings class derived from SettingsBase
   - Create and implement a Sensor class derived from SensorBase
6. Register all sensors in your `__init__.py` like this:  
    ```py
    SENSORS = [
      SensorDef('my-sensor', MySensor, MySettings),
    ]
    ```

## Publishing the sensor package

1. Put your code on GitHub
2. Create a release with tag `v<maj>.<min>.<patch>`
3. Add your manifest.json
4. Add sensors.zip containing  
   `sensors.zip/__init__.py`  
   `sensors.zip/<...other files...>`  

## Using the sensor package
Add this to your `settings.json` to install this package from GitHub releases:
```json
"packages": [
    {
        "type": "github",
        "pkg": "example",
        "repo": "simplic/simplic-insights-package-example",
        "version": "latest"
    }
]
```
