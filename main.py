from controller import Controller
from model import Model
from view import View

# Cria as classes de Model e View e as passa para o controller para serem inicialiadas
def main():
    model = Model()
    view = View()
    controller = Controller(model, view)
    controller.start()

if __name__ == "__main__":
    main()