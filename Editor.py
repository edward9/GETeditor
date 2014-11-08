# Name: Edward Takahashi
#
# file description:
#    Provides MyEditor class which inherited QPlainTextEdit class. It supports:
#        -display line number
#        -syntax highlight for python
#        -parentheses matching highlighting
#        -highlighting current line

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    
except ImportError:
    raise ImportError("Error: Pyside not installed")

import sys
import string

# used for parentheses matching
PAIR = {'(':')', ')':'(', '[':']', ']':'[', '{':'}', '}':'{'}


class LineNumber(QWidget):
    """ Class used to draw line number """
    def __init__(self, editor):
        super(LineNumber, self).__init__(editor)
        self.editor = editor
        
    def getWidth(self):
        return QSize(self.editor.lineNumberWidth(), 0)
    
    def paintEvent(self, event):
        """ override QWidget paintEvent """
        self.editor.lineNumberPaint(event)        

        
class MyEditor(QPlainTextEdit):
    """ inherit QPlainTextEdit class. MyEditor supports:
         display line number, syntax highlight for python, parentheses matching highlighting,
          and highlighting current line"""
          
    def __init__(self, parent=None):
        super(MyEditor, self).__init__(parent)
        self.parent = parent
        self.linenumber = LineNumber(self)
        self.countCache = [-1,-1]
        self.setContextMenuPolicy(Qt.NoContextMenu)
        
        # signal connection
        self.blockCountChanged.connect(self.updateLineNumberWidth)
        self.updateRequest.connect(self.updateLineNumber)
        self.cursorPositionChanged.connect(self.updateHighlight)
        
        self.updateLineNumberWidth(0)
        self.highlightCurrentLine()
        
    ########################################################
    # Method for displaying line number 
    
    def keyPressEvent(self,e):
        if self.parent.sharedWithParent and not self.isReadOnly():
            if e in [QKeySequence.SelectNextChar,QKeySequence.SelectNextLine,
                       QKeySequence.SelectPreviousChar,QKeySequence.SelectPreviousLine]:
                pass
            
            elif Qt.Key_Home <= e.key() and e.key() <= Qt.Key_PageDown:
                pass
            elif e == QKeySequence.Paste:
                text = QApplication.clipboard().text()
                if text != "":
                    start = self.textCursor().position()
                    self.parent.sharingParent.sendInsert(self.parent.getId(),start, text)
                return

            elif e == QKeySequence.Cut:
                start = self.textCursor().selectionStart()
                end   = self.textCursor().selectionEnd()
                if start != end:
                    QApplication.clipboard().setText(self.textCursor().selectedText())
                    self.parent.sharingParent.sendUpdate(self.parent,start,end-start,0)
                return
            elif e.key() == Qt.Key_Delete:
                start = self.textCursor().selectionStart()
                end   = self.textCursor().selectionEnd()
                if start == end:
                    if self.textCursor().atEnd() != True:
                        self.parent.sharingParent.sendUpdate(self.parent,start,1,0)
                else:
                    self.parent.sharingParent.sendUpdate(self.parent,start,end-start,0)
                return

            elif e.key() == Qt.Key_Backspace:
                start = self.textCursor().selectionStart()
                end   = self.textCursor().selectionEnd()
                if start == end:
                    if start != 0:
                        self.parent.sharingParent.sendUpdate(self.parent,start-1,1,0)
                else:
                    self.parent.sharingParent.sendUpdate(self.parent,start,end-start,0)
                return
            elif e.text() in string.printable:
                start = self.textCursor().position()
                self.parent.sharingParent.sendInsert(self.parent.getId(),start,e.text())
                return

        super(MyEditor,self).keyPressEvent(e)
        
    def lineNumberWidth(self):
        digits = 1
        maximum = max(1,self.blockCount())
        
        while maximum >= 10:
            maximum /= 10
            digits += 1
            
        space = 3 + self.fontMetrics().width('9') * digits
        
        return space
    
    def updateLineNumberWidth(self, width):
        self.setViewportMargins(self.lineNumberWidth(),0,0,0)
        
    def updateLineNumber(self, rect, dy):
        if dy:
            self.linenumber.scroll(0,dy)
        elif self.countCache[0] != self.blockCount() or self.countCache[1] != self.textCursor().block().lineCount():
            self.linenumber.update(0, rect.y(), self.linenumber.width(), rect.height())
            self.countCache[0] = self.blockCount()
            self.countCache[1] = self.textCursor().block().lineCount()
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberWidth(0)
            
    def resizeEvent(self, e):
        super(MyEditor, self).resizeEvent(e)
        cr = self.contentsRect()
        self.linenumber.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberWidth(), cr.height()))
        
    def lineNumberPaint(self, e):
        painter = QPainter(self.linenumber)
        painter.fillRect(e.rect(), Qt.lightGray)
        
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        
        while block.isValid() and top <= e.rect().bottom():
            if block.isVisible() and bottom >= e.rect().top():
                number = str(blockNumber+1)
                painter.setPen(Qt.black)
                painter.setFont(self.font())
                painter.drawText(0, top, self.linenumber.width(), self.fontMetrics().height(), Qt.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1
        
    ########################################################
    # Method for highlight current line
    def highlightCurrentLine(self):
        selections =  []
        if not self.isReadOnly():
            lineColor = QColor(Qt.cyan).lighter(190)
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            selections.append(selection)
    
        self.setExtraSelections(selections)
        
    ########################################################
    # Method for parenthesis matching

    def matchParentheses(self):
        cur_block = self.textCursor().block()
        data = cur_block.userData()
        
        if data:
            parentheses = data.getParentheses()
            position    = data.getSortedPosition()
            pos         = self.textCursor().block().position()
            cur_pos     = self.textCursor().position() - pos - 1
            if cur_pos in parentheses:
                if parentheses[cur_pos][0] in '{([':
                    if self.matchLeftParenthesis(cur_block, parentheses[cur_pos][0],parentheses[cur_pos][1]+1, 0):
                        self.HighlightParenthesis(pos + cur_pos)
                else:
                    if self.matchRightParenthesis(cur_block, parentheses[cur_pos][0],parentheses[cur_pos][1]-1, 0):
                        self.HighlightParenthesis(pos + cur_pos)

    def matchLeftParenthesis(self, cur_block, char, pos, numLeftParentheses):
        data = cur_block.userData()
        parentheses = data.getParentheses()
        position    = data.getSortedPosition()
        
        block_pos = cur_block.position()
        for i in range(pos, len(position)):
            if parentheses[position[i]][0] == char:
                numLeftParentheses += 1

            elif parentheses[position[i]][0] == PAIR[char] and numLeftParentheses == 0:
                self.HighlightParenthesis(block_pos + position[i])
                return True
            else:
                numLeftParentheses -= 1
                
        cur_block = cur_block.next()
        if cur_block.isValid():
            return self.matchLeftParenthesis(cur_block, char, 0, numLeftParentheses)
        
        return False
    
    def matchRightParenthesis(self, cur_block, char, pos, numRightParentheses):
        data = cur_block.userData()
        parentheses = data.getParentheses()
        position    = data.getSortedPosition()
        
        block_pos = cur_block.position()
        if len(position) > 0:
            for i in range(pos, -1, -1):
                if parentheses[position[i]][0] == char:
                    numRightParentheses += 1

                elif parentheses[position[i]][0] == PAIR[char] and numRightParentheses == 0:
                    self.HighlightParenthesis(block_pos + position[i])
                    return True
                else:
                    numRightParentheses -= 1
                
        cur_block = cur_block.previous()
        if cur_block.isValid():
            return self.matchRightParenthesis(cur_block, char, 0, numRightParentheses)
        
        return False
    
    def HighlightParenthesis(self, pos):
        
        selections = self.extraSelections()
        
        #lineColor = QColor(Qt.yellow).lighter(10)
        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(Qt.yellow)
        
        cursor = self.textCursor()
        cursor.setPosition(pos)
        cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
        selection.cursor = cursor
        
        selections.append(selection)
        
        self.setExtraSelections(selections)
    
    def updateHighlight(self):
        
        self.highlightCurrentLine()
        self.matchParentheses()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            
