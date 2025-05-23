"""
ECG Report Generator Application
Entry point for the PyQt5 ECG application.
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.app.main_window import AppMainWindow


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    window = AppMainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()