#!/usr/bin/env python3


import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

import sys
import subprocess
import threading

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, \
                            QVBoxLayout, \
                            QListWidget, \
                            QTextEdit, \
                            QSplitter, \
                            QMainWindow, \
                            QApplication


class GstBrowser(QMainWindow):
    
    def __init__(self):
        
        super().__init__()
        
        self.setWindowTitle('gst-browser')
        self.resize(800, 600)
        
        self.move(QApplication.desktop().screen().rect().center()
                  - self.frameGeometry().center())
                
        self._widget = QWidget()
        self.setCentralWidget(self._widget)

        self._splitter = QSplitter(Qt.Horizontal)

        self._list = QListWidget()
        self._editor = QTextEdit()
        
        font = QFont('monospace')
        self._list.setFont(font)
        self._editor.setFont(font)
        
        self._splitter.addWidget(self._list)
        self._splitter.addWidget(self._editor)
        self._splitter.setSizes([200, 600])

        self._layout = QVBoxLayout()
        self._layout.addWidget(self._splitter)
        self._widget.setLayout(self._layout)

        self.show()
        self.raise_()
        self.activateWindow()

        Gst.init([])

        self._registry = Gst.Registry.get()
        self._plugin_list = self._registry.get_plugin_list()

        self._plugin_names = [plugin.get_name()
                              for plugin
                              in self._plugin_list]

        self._plugin_names = sorted(self._plugin_names)

        self._list.addItems(self._plugin_names)

        self._list.itemSelectionChanged.connect(self.selectionChanged)
        
        self._current_plugin_name = ''
        
    def selectionChanged(self):

        def safe_str(string):
            if string is None:
                return 'None'
            elif type(string) is str:
                return string
            else:
                try:
                    return str(string)
                except:
                    return 'Error'
            
        def safe_line(title, string):
            return title + safe_str(string) + '\n'
        
        selected_items = self._list.selectedItems()
        
        if len(selected_items) <= 0:
            self._current_plugin_name = ''
            self._editor.setText('')
        else:
            self._current_plugin_name = selected_items[0].text()
            
            found = [plugin for plugin in self._plugin_list
                     if plugin.get_name() == self._current_plugin_name]

            message = ''
            
            if len(found) <= 0:
                message = 'Not found'
                self._current_plugin_name = ''
            else:
                plugin = found[0]

                message += safe_line('Name: ', plugin.get_name())
                message += safe_line('Version: ', plugin.get_version())
                message += safe_line('Description: ', plugin.get_description())
                message += safe_line('Filename: ', plugin.get_filename())
                message += safe_line('License: ', plugin.get_license())
                message += safe_line('Origin: ', plugin.get_origin())
                message += safe_line('Package: ', plugin.get_package())
                message += safe_line('Source: ', plugin.get_source())
                    
                inspection_result = subprocess.run(['gst-inspect-1.0',
                                                    plugin.get_name()],
                                                   stdout=subprocess.PIPE)
                result_message = inspection_result.stdout.decode('utf-8')
        
                message += '------\n\n'
                message += result_message

#                thread = threading.Thread(target=self.get_more_info)
#                thread.start()

            self._editor.setText(message)

    def get_more_info(self):
        try:
            plugin_name = self._current_plugin_name
            
            inspection_result = subprocess.run(['gst-inspect-1.0',
                                                plugin_name],
                                               stdout=subprocess.PIPE)
            result_message = inspection_result.stdout.decode('utf-8')
    
            if plugin_name == self._current_plugin_name:
                self._editor.append('------\n%s' % result_message)

        except Exception as e:
            print(e)
            pass


def main():

    app = QApplication(sys.argv)
    browser = GstBrowser()
    print('# of plugins =', len(browser._plugin_list))
    sys.exit(app.exec_())

    
if __name__ == '__main__':
    
    main()
