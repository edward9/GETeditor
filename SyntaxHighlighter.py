# -*- coding: utf-8 -*-
# part of code is borrowed from spyderlib(https://code.google.com/p/spyderlib/)
#
# Copyright © 2009-2010 Pierre Raybaut
# Licensed under the terms of the MIT License
# (see spyderlib/__init__.py for details)

import re
import keyword
import __builtin__

from PySide.QtGui import *
from PySide.QtCore import *



## My code for parenthesis matching #############################



class ParenthesisData():
    def __init__(self, character, position):
        self.character = character
        self.position  = position
        
    def getChar(self):
        return self.character
    
    def getPos(self):
        return self.position

class MyTextBlockData(QTextBlockUserData):
    def __init__(self, parent=None):
        super(MyTextBlockData,self).__init__(parent)
        self.parentheses     = {}
        self.sorted_position = []
        
    def getParentheses(self):
        return self.parentheses
    
    def getSortedPosition(self):
        return self.sorted_position
    
    def setData(self, text):
        
        counter = 0
        for i in range(len(text)):
            if text[i] in '([{)]}':
                self.sorted_position.append(i)
                self.parentheses[i] = (text[i], counter)
                counter += 1
            



#################################################################

COLOR_SCHEME_KEYS = ("background", "currentline", "occurence",
                     "ctrlclick", "sideareas", "matched_p", "unmatched_p",
                     "normal", "keyword", "builtin", "definition",
                     "comment", "string", "number", "instance")
COLORS = {
          'IDLE':
          {#  Name          Color    Bold   Italic
           "background":  "#ffffff",
           "currentline": "#eeffdd",
           "occurence":   "#e8f2fe",
           "ctrlclick":   "#0000ff",
           "sideareas":   "#efefef",
           "matched_p":   "#99ff99",
           "unmatched_p": "#ff9999",
           "normal":     ("#000000", False, False),
           "keyword":    ("#ff7700", True,  False),
           "builtin":    ("#900090", False, False),
           "definition": ("#0000ff", False, False),
           "comment":    ("#dd0000", False, True),
           "string":     ("#00aa00", False, False),
           "number":     ("#924900", False, False),
           "instance":   ("#777777", True,  True),
           },
          'Pydev':
          {#  Name          Color    Bold   Italic
           "background":  "#ffffff",
           "currentline": "#e8f2fe",
           "occurence":   "#ffff99",
           "ctrlclick":   "#0000ff",
           "sideareas":   "#efefef",
           "matched_p":   "#99ff99",
           "unmatched_p": "#ff9999",
           "normal":     ("#000000", False, False),
           "keyword":    ("#0000ff", False, False),
           "builtin":    ("#900090", False, False),
           "definition": ("#000000", True,  False),
           "comment":    ("#c0c0c0", False, False),
           "string":     ("#00aa00", False, True),
           "number":     ("#800000", False, False),
           "instance":   ("#000000", False, True),
           },
          'Emacs':
          {#  Name          Color    Bold   Italic
           "background":  "#000000",
           "currentline": "#2b2b43",
           "occurence":   "#abab67",
           "ctrlclick":   "#0000ff",
           "sideareas":   "#555555",
           "matched_p":   "#009800",
           "unmatched_p": "#c80000",
           "normal":     ("#ffffff", False, False),
           "keyword":    ("#3c51e8", False, False),
           "builtin":    ("#900090", False, False),
           "definition": ("#ff8040", True,  False),
           "comment":    ("#005100", False, False),
           "string":     ("#00aa00", False, True),
           "number":     ("#800000", False, False),
           "instance":   ("#ffffff", False, True),
           },
          'Scintilla':
          {#  Name          Color    Bold   Italic
           "background":  "#ffffff",
           "currentline": "#eeffdd",
           "occurence":   "#ffff99",
           "ctrlclick":   "#0000ff",
           "sideareas":   "#efefef",
           "matched_p":   "#99ff99",
           "unmatched_p": "#ff9999",
           "normal":     ("#000000", False, False),
           "keyword":    ("#00007f", True,  False),
           "builtin":    ("#000000", False, False),
           "definition": ("#007f7f", True,  False),
           "comment":    ("#007f00", False, False),
           "string":     ("#7f007f", False, False),
           "number":     ("#007f7f", False, False),
           "instance":   ("#000000", False, True),
           },
          'Spyder':
          {#  Name          Color    Bold   Italic
           "background":  "#ffffff",
           "currentline": "#feefff",
           "occurence":   "#ffff99",
           "ctrlclick":   "#0000ff",
           "sideareas":   "#efefef",
           "matched_p":   "#99ff99",
           "unmatched_p": "#ff9999",
           "normal":     ("#000000", False, False),
           "keyword":    ("#0000ff", False, False),
           "builtin":    ("#900090", False, False),
           "definition": ("#000000", True,  False),
           "comment":    ("#adadad", False, True),
           "string":     ("#00aa00", False, False),
           "number":     ("#800000", False, False),
           "instance":   ("#924900", False, True),
           },
          'Spyder/Dark':
          {#  Name          Color    Bold   Italic
           "background":  "#131926",
           "currentline": "#2b2b43",
           "occurence":   "#abab67",
           "ctrlclick":   "#0000ff",
           "sideareas":   "#282828",
           "matched_p":   "#009800",
           "unmatched_p": "#c80000",
           "normal":     ("#ffffff", False, False),
           "keyword":    ("#558eff", False, False),
           "builtin":    ("#aa00aa", False, False),
           "definition": ("#ffffff", True,  False),
           "comment":    ("#7f7f7f", False, False),
           "string":     ("#11a642", False, True),
           "number":     ("#c80000", False, False),
           "instance":   ("#be5f00", False, True),
           },
          }
COLOR_SCHEME_NAMES = COLORS.keys()

class BaseSH(QSyntaxHighlighter):
    """Base Syntax Highlighter Class"""
    # Syntax highlighting rules:
    PROG = None
    # Syntax highlighting states (from one text block to another):
    NORMAL = 0
    def __init__(self, parent=None, font=None, color_scheme='IDLE'):
        QSyntaxHighlighter.__init__(self, parent)
        
        self.outlineexplorer_data = {}
        
        self.font = font
        self._check_color_scheme(color_scheme)
        if isinstance(color_scheme, basestring):
            self.color_scheme = COLORS[color_scheme]
        else:
            self.color_scheme = color_scheme
        
        self.background_color = None
        self.currentline_color = None
        self.occurence_color = None
        self.ctrlclick_color = None
        self.sideareas_color = None
        self.matched_p_color = None
        self.unmatched_p_color = None

        self.formats = None
        self.setup_formats(font)
        
    def get_background_color(self):
        return QColor(self.background_color)
        
    def get_foreground_color(self):
        """Return foreground ('normal' text) color"""
        return self.formats["normal"].foreground().color()
        
    def get_currentline_color(self):
        return QColor(self.currentline_color)
        
    def get_occurence_color(self):
        return QColor(self.occurence_color)
    
    def get_ctrlclick_color(self):
        return QColor(self.ctrlclick_color)
    
    def get_sideareas_color(self):
        return QColor(self.sideareas_color)
    
    def get_matched_p_color(self):
        return QColor(self.matched_p_color)
    
    def get_unmatched_p_color(self):
        return QColor(self.unmatched_p_color)
    
    def get_color_name(self, fmt):
        """Return color name assigned to a given format"""
        return self.formats[fmt].foreground().color().name()

    def setup_formats(self, font=None):
        base_format = QTextCharFormat()
        if font is not None:
            self.font = font
        if self.font is not None:
            base_format.setFont(self.font)
        self.formats = {}
        colors = self.color_scheme.copy()
        self.background_color = colors.pop("background")
        self.currentline_color = colors.pop("currentline")
        self.occurence_color = colors.pop("occurence")
        self.ctrlclick_color = colors.pop("ctrlclick")
        self.sideareas_color = colors.pop("sideareas")
        self.matched_p_color = colors.pop("matched_p")
        self.unmatched_p_color = colors.pop("unmatched_p")
        for name, (color, bold, italic) in colors.iteritems():
            format = QTextCharFormat(base_format)
            format.setForeground(QColor(color))
            format.setBackground(QColor(self.background_color))
            if bold:
                format.setFontWeight(QFont.Bold)
            format.setFontItalic(italic)
            self.formats[name] = format

    def _check_color_scheme(self, color_scheme):
        if isinstance(color_scheme, basestring):
            assert color_scheme in COLOR_SCHEME_NAMES
        else:
            assert all([key in color_scheme for key in COLOR_SCHEME_KEYS])

    def set_color_scheme(self, color_scheme):
        self._check_color_scheme(color_scheme)
        if isinstance(color_scheme, basestring):
            self.color_scheme = COLORS[color_scheme]
        else:
            self.color_scheme = color_scheme
        self.setup_formats()
        self.rehighlight()

    def highlightBlock(self, text):
        raise NotImplementedError
            
    def get_outlineexplorer_data(self):
        return self.outlineexplorer_data

    def rehighlight(self):
        self.outlineexplorer_data = {}
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        QSyntaxHighlighter.rehighlight(self)
        QApplication.restoreOverrideCursor()
        
#==============================================================================
# Python syntax highlighter
#==============================================================================
def any(name, alternates):
    "Return a named group pattern matching list of alternates."
    return "(?P<%s>" % name + "|".join(alternates) + ")"

def make_python_patterns(additional_keywords=[], additional_builtins=[]):
    "Strongly inspired from idlelib.ColorDelegator.make_pat"
    kw = r"\b" + any("keyword", keyword.kwlist+additional_keywords) + r"\b"
    builtinlist = [str(name) for name in dir(__builtin__)
                   if not name.startswith('_')]+additional_builtins
    builtin = r"([^.'\"\\#]\b|^)" + any("builtin", builtinlist) + r"\b"
    comment = any("comment", [r"#[^\n]*"])
    instance = any("instance", [r"\bself\b"])
    number = any("number",
                 [r"\b[+-]?[0-9]+[lLjJ]?\b",
                  r"\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b",
                  r"\b[+-]?0[oO][0-7]+[lL]?\b",
                  r"\b[+-]?0[bB][01]+[lL]?\b",
                  r"\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?[jJ]?\b"])
    sqstring =     r"(\b[rRuU])?'[^'\\\n]*(\\.[^'\\\n]*)*'?"
    dqstring =     r'(\b[rRuU])?"[^"\\\n]*(\\.[^"\\\n]*)*"?'
    uf_sqstring =  r"(\b[rRuU])?'[^'\\\n]*(\\.[^'\\\n]*)*(\\)$(?!')$"
    uf_dqstring =  r'(\b[rRuU])?"[^"\\\n]*(\\.[^"\\\n]*)*(\\)$(?!")$'
    sq3string =    r"(\b[rRuU])?'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
    dq3string =    r'(\b[rRuU])?"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
    uf_sq3string = r"(\b[rRuU])?'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(\\)?(?!''')$"
    uf_dq3string = r'(\b[rRuU])?"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(\\)?(?!""")$'
    string = any("string", [sq3string, dq3string, sqstring, dqstring])
    ufstring1 = any("uf_sqstring", [uf_sqstring])
    ufstring2 = any("uf_dqstring", [uf_dqstring])
    ufstring3 = any("uf_sq3string", [uf_sq3string])
    ufstring4 = any("uf_dq3string", [uf_dq3string])
    return "|".join([instance, kw, builtin, comment,
                     ufstring1, ufstring2, ufstring3, ufstring4, string,
                     number, any("SYNC", [r"\n"])])

class OutlineExplorerData(object):
    CLASS, FUNCTION, STATEMENT, COMMENT = range(4)
    def __init__(self):
        self.text = None
        self.fold_level = None
        self.def_type = None
        self.def_name = None
        
    def is_not_class_nor_function(self):
        return self.def_type not in (self.CLASS, self.FUNCTION)
    
    def is_comment(self):
        return self.def_type == self.COMMENT
        
    def get_class_name(self):
        if self.def_type == self.CLASS:
            return self.def_name
        
    def get_function_name(self):
        if self.def_type == self.FUNCTION:
            return self.def_name
    
class PythonSH(BaseSH):
    """Python Syntax Highlighter"""
    # Syntax highlighting rules:
    PROG = re.compile(make_python_patterns(), re.S)
    IDPROG = re.compile(r"\s+(\w+)", re.S)
    ASPROG = re.compile(r".*?\b(as)\b")
    # Syntax highlighting states (from one text block to another):
    (NORMAL, INSIDE_SQ3STRING, INSIDE_DQ3STRING,
     INSIDE_SQSTRING, INSIDE_DQSTRING) = range(5)
    DEF_TYPES = {"def": OutlineExplorerData.FUNCTION,
                 "class": OutlineExplorerData.CLASS}
    # Comments suitable for Outline Explorer
    OECOMMENT = re.compile('^(# ?--[-]+|##[#]+ )[ -]*[^- ]+')
    
    def __init__(self, parent=None, font=None, color_scheme='Spyder'):
        BaseSH.__init__(self, parent, font, color_scheme)
        self.import_statements = {}

    def highlightBlock(self, text):
        
        # My code #################################
        data = MyTextBlockData()
        data.setData(text)

        
        self.setCurrentBlockUserData(data);

        
        ###########################################
        # Borrowed code
        text = unicode(text)
        prev_state = self.previousBlockState()
        if prev_state == self.INSIDE_DQ3STRING:
            offset = -4
            text = r'""" '+text
        elif prev_state == self.INSIDE_SQ3STRING:
            offset = -4
            text = r"''' "+text
        elif prev_state == self.INSIDE_DQSTRING:
            offset = -2
            text = r'" '+text
        elif prev_state == self.INSIDE_SQSTRING:
            offset = -2
            text = r"' "+text
        else:
            offset = 0
            prev_state = self.NORMAL
        
        oedata = None
        import_stmt = None

        self.setFormat(0, len(text), self.formats["normal"])
        
        state = self.NORMAL
        match = self.PROG.search(text)
        while match:
            for key, value in match.groupdict().items():
                if value:
                    start, end = match.span(key)
                    start = max([0, start+offset])
                    end = max([0, end+offset])
                    if key == "uf_sq3string":
                        self.setFormat(start, end-start,
                                       self.formats["string"])
                        state = self.INSIDE_SQ3STRING
                    elif key == "uf_dq3string":
                        self.setFormat(start, end-start,
                                       self.formats["string"])
                        state = self.INSIDE_DQ3STRING
                    elif key == "uf_sqstring":
                        self.setFormat(start, end-start,
                                       self.formats["string"])
                        state = self.INSIDE_SQSTRING
                    elif key == "uf_dqstring":
                        self.setFormat(start, end-start,
                                       self.formats["string"])
                        state = self.INSIDE_DQSTRING
                    else:
                        self.setFormat(start, end-start, self.formats[key])
                        if key == "comment":
                            if self.OECOMMENT.match(text.lstrip()):
                                oedata = OutlineExplorerData()
                                oedata.text = unicode(text).strip()
                                oedata.fold_level = start
                                oedata.def_type = OutlineExplorerData.COMMENT
                                oedata.def_name = text.strip()
                        elif key == "keyword":
                            if value in ("def", "class"):
                                match1 = self.IDPROG.match(text, end)
                                if match1:
                                    start1, end1 = match1.span(1)
                                    self.setFormat(start1, end1-start1,
                                                   self.formats["definition"])
                                    oedata = OutlineExplorerData()
                                    oedata.text = unicode(text)
                                    oedata.fold_level = start
                                    oedata.def_type = self.DEF_TYPES[
                                                                unicode(value)]
                                    oedata.def_name = text[start1:end1]
                            elif value in ("elif", "else", "except", "finally",
                                           "for", "if", "try", "while",
                                           "with"):
                                if text.lstrip().startswith(value):
                                    oedata = OutlineExplorerData()
                                    oedata.text = unicode(text).strip()
                                    oedata.fold_level = start
                                    oedata.def_type = \
                                        OutlineExplorerData.STATEMENT
                                    oedata.def_name = text.strip()
                            elif value == "import":
                                import_stmt = text.strip()
                                # color all the "as" words on same line, except
                                # if in a comment; cheap approximation to the
                                # truth
                                if '#' in text:
                                    endpos = text.index('#')
                                else:
                                    endpos = len(text)
                                while True:
                                    match1 = self.ASPROG.match(text, end,
                                                               endpos)
                                    if not match1:
                                        break
                                    start, end = match1.span(1)
                                    self.setFormat(start, end-start,
                                                   self.formats["keyword"])
                    
            match = self.PROG.search(text, match.end())

        self.setCurrentBlockState(state)
        
        if oedata is not None:
            block_nb = self.currentBlock().blockNumber()
            self.outlineexplorer_data[block_nb] = oedata
        if import_stmt is not None:
            block_nb = self.currentBlock().blockNumber()
            self.import_statements[block_nb] = import_stmt
            
    def get_import_statements(self):
        return self.import_statements.values()
            
    def rehighlight(self):
        self.import_statements = {}
        BaseSH.rehighlight(self)
