******
Eleran
******

Simple & fast sass compiler and javascript minifier with hot reloading 

Install
=======

Install using pip::

    pip install eleran

Usage
=====

Command::

    eleran <command> <path> --mode=<mode>

**commad:**

- watch

- validate

- generate

**--mode:**

- debug

Example, generate eleran.json to example directory::

    eleran generate example

Watch::

    eleran watch example

Configuration File
==================

eleran.json::

    [
        {
            "sass": {
                "source": "sass/style.scss",
                "output": "style.min.css",
                "output_style": "compressed",
                "source_comments": false
            }
        },
        {
            "js": {
                "include": [
                    "js/foo.js",
                    "js/bar.js"
                ],
            "output": "script.min.js"
	    }
        }
    ]

**Sass - output_style:**

- compact

- compressed

- expanded 

- nested