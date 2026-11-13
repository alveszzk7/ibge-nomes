"""Camada de Apresentação (Tkinter): dropdowns e listas. Só usa os Services."""
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from ibgenomes.models import Estado, Municipio, NomesLocalidade
from ibgenomes.services import ApiError, LocalidadesService, NomesService


class App(tk.Tk):
    def __init__(self, localidades: LocalidadesService, nomes: NomesService):
        super().__init__()
        self.title("IBGE Data Insights - Nomes mais comuns (Censo 2022)")
        self.geometry("820x600")
        self._loc = localidades
        self._nomes = nomes
        self._estados: list[Estado] = []
        self._municipios: list[Municipio] = []
        self._consulta_atual = 0  # evita que resposta antiga sobrescreva a nova

        self._fila: queue.Queue = queue.Queue()
        self._build()
        self._poll_fila()
        self._run(self._loc.listar_estados, self._on_estados)

    # ---------- construção da tela ----------
    def _build(self) -> None:
        top = ttk.LabelFrame(self, text="Localidade", padding=10)
        top.pack(fill="x", padx=10, pady=10)
        top.columnconfigure(1, weight=1)

        self.modo = tk.StringVar(value="estado")
        ttk.Radiobutton(top, text="Estado", variable=self.modo, value="estado",
                        command=self._on_modo).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(top, text="Município", variable=self.modo, value="municipio",
                        command=self._on_modo).grid(row=0, column=1, sticky="w")

        ttk.Label(top, text="Estado:").grid(row=1, column=0, sticky="w", pady=4)
        self.cb_estado = ttk.Combobox(top, state="readonly", width=40)
        self.cb_estado.grid(row=1, column=1, sticky="ew", pady=4)
        self.cb_estado.bind("<<ComboboxSelected>>", self._on_estado)

        ttk.Label(top, text="Município:").grid(row=2, column=0, sticky="w", pady=4)
        self.cb_mun = ttk.Combobox(top, state="disabled", width=40)
        self.cb_mun.grid(row=2, column=1, sticky="ew", pady=4)
        self.cb_mun.bind("<<ComboboxSelected>>", self._on_municipio)

        self.status = tk.StringVar(value="Carregando estados...")
        ttk.Label(self, textvariable=self.status, foreground="gray").pack(anchor="w", padx=12)

        cols = ttk.Frame(self)
        cols.pack(fill="both", expand=True, padx=10, pady=10)
        self.trees = {}
        for i, (chave, titulo) in enumerate(
            [("homens", "Homens"), ("mulheres", "Mulheres"), ("sobrenomes", "Sobrenomes")]
        ):
            cols.columnconfigure(i, weight=1, uniform="c")
            cols.rowconfigure(0, weight=1)
            box = ttk.LabelFrame(cols, text=titulo, padding=4)
            box.grid(row=0, column=i, sticky="nsew", padx=4)
            tree = ttk.Treeview(box, columns=("pos", "nome", "freq"), show="headings", height=12)
            tree.heading("pos", text="#")
            tree.heading("nome", text="Nome")
            tree.heading("freq", text="Frequência")
            tree.column("pos", width=28, anchor="center", stretch=False)
            tree.column("nome", width=110)
            tree.column("freq", width=80, anchor="e")
            tree.pack(fill="both", expand=True)
            self.trees[chave] = tree

    # ---------- execução assíncrona (não trava a janela) ----------
    def _run(self, func, on_ok, *args) -> None:
        def worker():
            try:
                result = func(*args)
            except ApiError as e:
                msg = str(e)
                self._fila.put(lambda: self._on_erro(msg))
                return
            self._fila.put(lambda: on_ok(result))

        threading.Thread(target=worker, daemon=True).start()

    def _poll_fila(self) -> None:
        """Executa na thread da UI os resultados vindos das threads de rede."""
        try:
            while True:
                self._fila.get_nowait()()
        except queue.Empty:
            pass
        self.after(50, self._poll_fila)

    def _on_erro(self, msg: str) -> None:
        self.status.set("Erro.")
        messagebox.showerror("Erro de comunicação", msg)

    # ---------- eventos ----------
    def _on_estados(self, estados: list[Estado]) -> None:
        self._estados = estados
        self.cb_estado["values"] = [str(e) for e in estados]
        self.status.set("Selecione um estado.")

    def _on_modo(self) -> None:
        if self.modo.get() == "estado":
            self.cb_mun.set("")
            self.cb_mun.configure(state="disabled")
            if self.cb_estado.current() >= 0:
                self._consultar(self._estados[self.cb_estado.current()].id, self.cb_estado.get())
        else:
            self.cb_mun.configure(state="readonly" if self._municipios else "disabled")
            self._limpar()
            self.status.set("Selecione um estado e depois um município.")

    def _on_estado(self, _evt=None) -> None:
        estado = self._estados[self.cb_estado.current()]
        if self.modo.get() == "estado":
            self._consultar(estado.id, str(estado))
            return
        self.cb_mun.set("")
        self.cb_mun.configure(state="disabled", values=[])
        self._municipios = []
        self._limpar()
        self.status.set(f"Carregando municípios de {estado.nome}...")
        self._run(self._loc.listar_municipios, self._on_municipios, estado.id)

    def _on_municipios(self, municipios: list[Municipio]) -> None:
        self._municipios = municipios
        self.cb_mun.configure(state="readonly", values=[m.nome for m in municipios])
        self.status.set(f"{len(municipios)} municípios. Selecione um.")

    def _on_municipio(self, _evt=None) -> None:
        m = self._municipios[self.cb_mun.current()]
        self._consultar(m.id, f"{m.nome} - {self.cb_estado.get()}")

    def _consultar(self, localidade_id: int, rotulo: str) -> None:
        self._consulta_atual += 1
        token = self._consulta_atual
        self.status.set(f"Consultando nomes de {rotulo}...")
        self._limpar()

        def ok(dados: NomesLocalidade):
            if token != self._consulta_atual:
                return
            self._mostrar(dados)
            self.status.set(f"Nomes mais comuns em {rotulo} (Censo 2022).")

        self._run(self._nomes.buscar_por_localidade, ok, localidade_id)

    # ---------- exibição ----------
    def _limpar(self) -> None:
        for t in self.trees.values():
            t.delete(*t.get_children())

    def _mostrar(self, dados: NomesLocalidade) -> None:
        for chave in ("homens", "mulheres", "sobrenomes"):
            tree = self.trees[chave]
            itens = getattr(dados, chave)
            if not itens:
                tree.insert("", "end", values=("", "Sem dados", ""))
            for i, f in enumerate(itens, 1):
                tree.insert("", "end", values=(i, f.nome, f"{f.frequencia:,}".replace(",", ".")))
