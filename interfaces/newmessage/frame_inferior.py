import tkinter as tk
from interfaces.colors import *
from interfaces.fonts import *
from interfaces.commands.newmessage import Commands

class FrameInferior:
    def main(self):
        frame_inferior = tk.Frame(
            master = self.camada_1,
            bg = azul_frame,
            bd = 10
        )
        save = tk.Button(
            master = frame_inferior,
            text = 'Salvar',
            command = lambda : Commands.save_all_json(self),
            bg = azul_entrada,
            relief = tk.FLAT,
            borderwidth = 1
        )
        save_and_quit = tk.Button(
            master = frame_inferior,
            text = 'Salvar e sair',
            command = lambda : Commands.save_and_quit(self),
            bg = azul_entrada,
            relief = tk.FLAT,
            borderwidth = 1, 
        )
        save.grid(
            row = 1,
            column = 1,
            padx = 10,
            pady = 10
        )
        save_and_quit.grid(
            row = 2,
            column = 1,
        )
        frame_inferior.pack(
            side = tk.BOTTOM,
            fill = tk.Y,
            expand = True
        )