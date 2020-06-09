Development of Qaava plugin
===========================

The code for the plugin is in the [Qaava](../Qaava) folder. Make sure you have required tools, such as
Qt with Qt Editor and Qt Linquist installed by following this 
[tutorial](https://www.qgistutorials.com/en/docs/3/building_a_python_plugin.html#get-the-tools). 

For building the plugin there are two options: using [Makefile](../Qaava/Makefile) or to use 
platform independent [build.py](../Qaava/build.py) script. 
These instructions are for the build script.

### Adding or editing  source files
If you create or edit source files make sure that:
* they contain relative imports
    ```python
    '''file Qaava/database_tools/db_initializer.py'''
    
    from ..utils import logger # Good
    
    from Qaava.utils import logger # Bad
    ```
* they will be found by [build.py](../Qaava/build.py) script (UI and QAAVA values)
* if they contain translatable content, they will be added to [translate.pro](../Qaava/i18n/translate.pro)
* you consider adding test files for the new functionality

### Deployment

Edit [build.py](../Qaava/build.py) to contain working values for PROFILE, LRELEASE and PYRCC.

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

#### Translating

The translation files are in [i18n](../Qaava/i18n) folder. [translate.pro](../Qaava/i18n/translate.pro) 
contains the lists of source files to have translatable content.
Translatable content in python files is code such as `tr(u"Hello World")`. 

To update language *.ts* files to contain newest lines to translate, run
```shell script
python build.py transup
```

You can then open the *.ts* files you wish to translate with Qt Linguist and make the changes.

Compile the translations to *.qm* files with:
```shell script
python build.py transcompile
```

### Creating a release
Follow these steps to create a release zip file and tag
* Increment version number in [metadata.txt](../Qaava/metadata.txt) (for example 0.0.1 -> 0.1.0).
* Make a new commit. (`git add -A && git commit -m "Release v0.1.0"`)
* Create new tag for it (`git tag v0.1.0`). You can also use --tag flag in next command to skip this step
* Create zipped plugin package:
    ```shell script
    python build.py package --version v0.1.0
    ``` 
* File **Qaava.zip** should appear in the [Qaava](../Qaava) folder