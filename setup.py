# -*- coding: UTF-8 -*-

from distutils.core import setup
import py2exe

setup(
    windows = [{
            "script" : "DocuWorks Converter.pyw",
    		"name" : "DocuWorks Converter",
            "icon_resources" : [(1,"options\\image\\convert.ico")],
    		"version" : "1.0.3",
    		}],
    zipfile = "lib/library.zip")
