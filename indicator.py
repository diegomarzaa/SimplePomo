# indicator.py
import gi
gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3, Gtk
import subprocess
import signal
import os

# Nombre de la aplicación y ruta del ícono
APP_NAME = "MiAppIndicator"
ICON_PATH = "/home/diego/Documents/Proyectos/SimplePomo/pomoicon.png"  # Cambia esta ruta a tu icono

# Función para ejecutar la aplicación
def run_app(_):
    subprocess.Popen(["/home/diego/miniforge3/bin/python3", "/home/diego/Documents/Proyectos/SimplePomo/__main__.py"])



# Función para salir del indicador
def quit_app(_):
    Gtk.main_quit()

# Configuración del indicador
indicator = AppIndicator3.Indicator.new(
    APP_NAME,
    ICON_PATH,
    AppIndicator3.IndicatorCategory.APPLICATION_STATUS
)
indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

# Menú del indicador
menu = Gtk.Menu()

# Añadir la opción "Open App"
open_item = Gtk.MenuItem(label="Open App")
open_item.connect("activate", run_app)
menu.append(open_item)

# Añadir la opción "Quit"
quit_item = Gtk.MenuItem(label="Quit")
quit_item.connect("activate", quit_app)
menu.append(quit_item)

# Mostrar el menú
menu.show_all()
indicator.set_menu(menu)

# Manejador de señales para salir
signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()

