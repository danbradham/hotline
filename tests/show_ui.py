from hotline import ui
import sys


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    view = ui.View()
    view.show()

    dock = ui.Dock()
    dock.show()

    sys.exit(app.exec_())
