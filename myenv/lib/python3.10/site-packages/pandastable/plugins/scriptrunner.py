#!/usr/bin/env python
"""
    DataExplore pluin differential expression using R
    Created June 2017
    Copyright (C) Damien Farrell

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 3
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from __future__ import absolute_import, division, print_function
import sys,os
import subprocess
import numpy as np
from pandastable.plugin import Plugin
from pandastable import core, plotting, dialogs
try:
    from tkinter import *
    from tkinter.ttk import *
except:
    from Tkinter import *
    from ttk import *
import pandas as pd
import pylab as plt
from collections import OrderedDict

class ScriptRunnerPlugin(Plugin):
    """Plugin for DataExplore"""

    capabilities = ['gui','uses_sidepane']
    requires = ['']
    menuentry = 'Run Script'
    gui_methods = {}
    version = '0.1'

    def __init__(self):
        self.result = None
        return

    def main(self, parent):

        if parent==None:
            return
        self.parent = parent
        self._doFrame()
        w = self.mainwin
        fr = Frame(w)
        fr.pack(side=LEFT,fill=BOTH)
        self.ed = ed = dialogs.SimpleEditor(fr, width=60, height=25)
        ed.pack(in_=fr, fill=BOTH, expand=Y)
        ed.text.insert(END, '#run code here')

        bf = Frame(w, padding=2)
        bf.pack(side=LEFT,fill=BOTH)
        b = Button(bf, text="Run", command=self.run)
        b.pack(side=TOP,fill=X,pady=2)
        b = Button(bf, text="Close", command=self.quit)
        b.pack(side=TOP,fill=X,pady=2)
        b = Button(bf, text="Help", command=self.online_help)
        b.pack(side=TOP,fill=X,pady=2)

        #self.update()
        sheet = self.parent.getCurrentSheet()
        #reference to parent frame in sheet
        pw = self.parent.sheetframes[sheet]
        self.pf = self.table.pf

        return

    def run(self):
        """Run chosen method"""

        df = self.table.model.df
        safe_dict = {'df':df}

        code = self.ed.text.get(1.0, END).splitlines()
        for line in code:
            print (line)
            eval(line, {"__builtins__" : None }, safe_dict)

        return

    def createMethod(self, lines):
        def func(cls, x):
            return x
        setattr(self.__class__, 'func', func)

    def update(self):

        t = core.Table(fr, dataframe=df, showtoolbar=True)
        t.show()
        return

    def quit(self, evt=None):
        """Override this to handle pane closing"""

        self.mainwin.destroy()
        return

    def online_help(self,event=None):
        """Open the online documentation"""
        import webbrowser
        link='https://github.com/dmnfarrell/pandastable/wiki'
        webbrowser.open(link,autoraise=1)
        return


