from ibgenomes.services import LocalidadesService, NomesService
from ibgenomes.ui.app import App

if __name__ == "__main__":
    App(LocalidadesService(), NomesService()).mainloop()
