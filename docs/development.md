Development of Qaava plugin
===========================

The code for the plugin is in the [Qaava](../Qaava) folder. Make sure you have required tools, such as
Qt with Qt Editor and Qt Linquist installed by following this 
[tutorial](https://www.qgistutorials.com/en/docs/3/building_a_python_plugin.html#get-the-tools). 

For building the plugin use platform independent [build.py](../Qaava/build.py) script. 

### Adding or editing  source files
If you create or edit source files make sure that:
* they contain relative imports
    ```python
    '''file Qaava/database_tools/db_initializer.py'''
    
    from ..utils.exceptions import QaavaAuthConfigException # Good
    
    from Qaava.utils.exceptions import QaavaAuthConfigException # Bad
    ```
* they will be found by [build.py](../Qaava/build.py) script (`py_files` and `ui_files` values)
* you consider adding test files for the new functionality

### Deployment

Edit [build.py](../Qaava/build.py) to contain working values for *profile*, *lrelease* and *pyrcc*. 
If you are running on Windows, make sure the value *QGIS_INSTALLATION_DIR* points to right folder

Run the deployment with:
```shell script
python build.py deploy
```

After deploying and restarting QGIS you should see the plugin in the QGIS installed plugins
where you have to activate it.

#### Testing
Install Docker, docker-compose and python packages listed in [requirements.txt](requirements.txt) 
to run tests with:

```shell script
python build.py test
```

#### Translating with transifex

Fill in `transifex_coordinator` (Transifex username) and `transifex_organization`
in [.qgis-plugin-ci](../.qgis-plugin-ci) to use Transifex translation.

##### Pushing / creating new translations
* First install [Transifex CLI](https://docs.transifex.com/client/installing-the-client) and
  [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci)
* Run `qgis-plugin-ci push-translation <your-transifex-token>`
* Go to your Transifex site, add some languages and start translating
* Copy [push_translations.yml](push_translations.yml) file to [workflows](../.github/workflows) folder
    to enable automatic pushing after commits to master
* Add this badge ![](https://github.com/<organization>/<repo>/workflows/Translations/badge.svg) to the [README](../README.md)

##### Pulling
There is no need to pull if you configure `--transifex-token` into your
[release](../.github/workflows/release.yml) workflow (remember to use Github Secrets).
You can however pull manually to test the process.
* Run `qgis-plugin-ci pull-translation --compile <your-transifex-token>`

### Creating a release
Follow these steps to create a release
* Add changelog information to [CHANGELOG.md](../CHANGELOG.md) using this
[format](https://raw.githubusercontent.com/opengisch/qgis-plugin-ci/master/CHANGELOG.md)
* Make a new commit. (`git add -A && git commit -m "Release v0.1.0"`)
* Create new tag for it (`git tag -a v0.1.0 -m "Version 0.1.0"`)
* Push tag to Github using `git push --follow-tags`
* Create Github release
* [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci) adds release zip automatically as an asset
