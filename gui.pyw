"""Launcher for Port Scanner GUI — double-click to run without console window."""
import sys
sys.path.insert(0, r"E:\class\ComputerNetworkDesign")

try:
    from gui import PortScannerGUI
    PortScannerGUI().run()
except Exception:
    import tkinter.messagebox as mb
    import traceback
    mb.showerror("Port Scanner Error", traceback.format_exc())
