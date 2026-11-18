from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image

from core.estado import MovimentoIlegal, PartidaEncerrada
from interface.coordenadas import modelo_para_tela, tela_para_modelo
from interface.formatacao import linhas_historico

COR_CASA_CLARA = "#EEEED2"
COR_CASA_ESCURA = "#769656"
COR_SELECIONADA = "#F6F669"
COR_MOVIMENTO_VALIDO = "#DA7D7A"
COR_REI_EM_XEQUE = "#E5484D"
COR_PAINEL = "#242B35"
COR_TEXTO = "#F1F4F9"
COR_TEXTO_SECUNDARIO = "#B5BECF"

IMAGENS = Path(__file__).resolve().parent / "imgs"
PECAS = ("Peao", "Torre", "Cavalo", "Bispo", "Rainha", "Rei")


class JanelaXadrez(ctk.CTk):

    def __init__(self, servico):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("Chess Open Source Nerfado")
        self.geometry("1010x735")
        self.minsize(965, 700)
        self.configure(fg_color="#1A2029")

        self.servico = servico
        self.casa_selecionada: tuple[int, int] | None = None
        self.movimentos_selecionados = []
        self.movimentos_destacados: set[tuple[int, int]] = set()
        self.invertido = False
        self.rei_destacado: tuple[int, int] | None = None
        self._temporizador_xeque = None
        self._temporizador_aviso = None
        self.botoes = {}
        self.imagens = self._carregar_imagens()
        self.protocol("WM_DELETE_WINDOW", self.fechar)

        self._montar_interface()
        self.atualizar_tudo()
        self._avisar_xeque_ao_abrir()

    @property
    def jogo(self):
        return self.servico.jogo

    def _carregar_imagens(self):
        imagens = {}
        for cor in ("branco", "preto"):
            for nome in PECAS:
                caminho = IMAGENS / f"Chess_{nome}_{cor}_Sprite.png"
                pil = Image.open(caminho).convert("RGBA")
                imagens[(cor, nome)] = ctk.CTkImage(
                    light_image=pil, dark_image=pil, size=(68, 68)
                )
        vazio = Image.open(IMAGENS / "pngg.png").convert("RGBA")
        imagens[None] = ctk.CTkImage(light_image=vazio, dark_image=vazio, size=(68, 68))
        return imagens

    def _montar_interface(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        area_tabuleiro = ctk.CTkFrame(self, fg_color="transparent")
        area_tabuleiro.grid(row=0, column=0, padx=(18, 8), pady=16, sticky="n")
        ctk.CTkLabel(
            area_tabuleiro, text="CHESS", font=ctk.CTkFont(size=29, weight="bold"),
            text_color=COR_TEXTO,
        ).pack(pady=(0, 1))
        self.label_turnos = ctk.CTkLabel(
            area_tabuleiro, text="", font=ctk.CTkFont(size=17, weight="bold"),
            text_color=COR_TEXTO_SECUNDARIO,
        )
        self.label_turnos.pack(pady=(0, 8))

        frame_tabuleiro = ctk.CTkFrame(area_tabuleiro, corner_radius=0, fg_color="transparent")
        frame_tabuleiro.pack()
        for linha in range(8):
            for coluna in range(8):
                cor = COR_CASA_CLARA if (linha + coluna) % 2 == 0 else COR_CASA_ESCURA
                botao = ctk.CTkButton(
                    frame_tabuleiro, text="", width=70, height=70,
                    corner_radius=0, border_width=0,
                    fg_color=cor, hover_color=cor,
                    command=lambda l=linha, c=coluna: self.clicar_casa(l, c),
                )
                botao.grid(row=linha, column=coluna)
                self.botoes[(linha, coluna)] = botao

        ctk.CTkLabel(
            area_tabuleiro,
            text="",
            font=ctk.CTkFont(size=13), text_color=COR_TEXTO_SECUNDARIO,
        ).pack(pady=(10, 0))

        painel = ctk.CTkFrame(self, width=355, corner_radius=14, fg_color=COR_PAINEL)
        painel.grid(row=0, column=1, padx=(8, 20), pady=17, sticky="nsew")
        painel.grid_propagate(False)
        painel.grid_columnconfigure(0, weight=1)
        painel.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            painel, text="Partida", font=ctk.CTkFont(size=23, weight="bold"),
            text_color=COR_TEXTO, anchor="w",
        ).grid(row=0, column=0, padx=18, pady=(18, 2), sticky="ew")
        self.label_partida = ctk.CTkLabel(
            painel, text="", font=ctk.CTkFont(size=13),
            text_color=COR_TEXTO_SECUNDARIO, justify="left", anchor="w",
        )
        self.label_partida.grid(row=1, column=0, padx=18, pady=(0, 13), sticky="ew")

        cabecalho = ctk.CTkFrame(painel, fg_color="#303A48", corner_radius=8)
        cabecalho.grid(row=2, column=0, padx=14, pady=(0, 4), sticky="ew")
        cabecalho.grid_columnconfigure(0, minsize=48)
        cabecalho.grid_columnconfigure(1, weight=1)
        cabecalho.grid_columnconfigure(2, weight=1)
        for coluna, texto in enumerate(("Nº", "Brancas", "Pretas")):
            ctk.CTkLabel(
                cabecalho, text=texto, text_color=COR_TEXTO,
                font=ctk.CTkFont(size=13, weight="bold"),
            ).grid(row=0, column=coluna, padx=5, pady=7, sticky="ew")

        self.rolagem_lances = ctk.CTkScrollableFrame(
            painel, corner_radius=8, fg_color="#1B232E",
            scrollbar_button_color="#67778B",
        )
        self.rolagem_lances.grid(row=3, column=0, padx=14, pady=0, sticky="nsew")
        self.rolagem_lances.grid_columnconfigure(0, minsize=43)
        self.rolagem_lances.grid_columnconfigure(1, weight=1)
        self.rolagem_lances.grid_columnconfigure(2, weight=1)

        controles = ctk.CTkFrame(painel, fg_color="transparent")
        controles.grid(row=4, column=0, padx=14, pady=(14, 0), sticky="ew")
        controles.grid_columnconfigure(0, weight=1)
        controles.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(
            controles, text="Nova partida", height=38,
            fg_color="#487C61", hover_color="#3A6951",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.nova_partida,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkButton(
            controles, text="Voltar lance", height=38,
            fg_color="#47566B", hover_color="#3B485B",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.voltar_lance,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))
        ctk.CTkButton(
            controles, text="Inverter tabuleiro (linhas)", height=34,
            fg_color="#343F4D", hover_color="#47566B",
            command=self.inverter_tabuleiro,
        ).grid(row=1, column=0, columnspan=2, pady=(9, 0), sticky="ew")

        self.label_aviso = ctk.CTkLabel(
            painel, text="", height=43, wraplength=313,
            font=ctk.CTkFont(size=12), text_color="#F5B7B8",
        )
        self.label_aviso.grid(row=5, column=0, padx=14, pady=(8, 4), sticky="ew")
        ctk.CTkLabel(
            painel, text="Made for Camila",
            font=ctk.CTkFont(size=11), text_color=COR_TEXTO_SECUNDARIO,
        ).grid(row=6, column=0, padx=14, pady=(0, 12))

    def clicar_casa(self, linha_tela: int, coluna_tela: int):
        if self.jogo.estado().terminado:
            self._mostrar_aviso("Esta partida terminou. Use 'Nova partida' para jogar novamente.")
            return

        linha, coluna = tela_para_modelo(linha_tela, coluna_tela, self.invertido)
        destino = (linha, coluna)
        peca = self.jogo.tabuleiro.get_peca(linha, coluna)

        if self.casa_selecionada is None:
            if peca and peca.cor == self.jogo.turno:
                self.selecionar_casa(destino)
            elif peca:
                self._mostrar_aviso("Aguarde sua vez: esta peça é do adversário.")
            else:
                self._mostrar_aviso("Selecione primeiro uma peça da cor da vez.")
            return

        if destino == self.casa_selecionada:
            self.limpar_selecao()
            self.atualizar_tabuleiro()
            return

        if destino in self.movimentos_destacados:
            promocao_possivel = any(
                mov.destino == destino and mov.promocao
                for mov in self.movimentos_selecionados
            )
            if promocao_possivel:
                self._escolher_promocao(self.casa_selecionada, destino)
            else:
                self._jogar(self.casa_selecionada, destino)
            return

        if peca and peca.cor == self.jogo.turno:
            # Trocar de peça selecionada não é uma tentativa ilegal.
            self.selecionar_casa(destino)
        else:
            self._mostrar_aviso("Movimento inválido: a peça não pode ir para essa casa.")
            self._piscar_rei(self.jogo.turno)

    def selecionar_casa(self, origem: tuple[int, int]):
        self.casa_selecionada = origem
        self.movimentos_selecionados = self.jogo.movimentos_legais(origem)
        self.movimentos_destacados = {mov.destino for mov in self.movimentos_selecionados}
        self.atualizar_tabuleiro()

    def limpar_selecao(self):
        self.casa_selecionada = None
        self.movimentos_selecionados = []
        self.movimentos_destacados = set()

    def _jogar(self, origem, destino, promocao=None):
        estava_terminada = self.jogo.estado().terminado
        try:
            self.servico.jogar(origem, destino, promocao)
        except (MovimentoIlegal, PartidaEncerrada, ValueError) as erro:
            self._mostrar_aviso(f"Não foi possível jogar: {erro}")
            self._piscar_rei(self.jogo.turno)
            return
        except Exception as erro:
            messagebox.showerror("Falha ao salvar o lance", str(erro), parent=self)
            self.atualizar_tudo()
            return

        self.limpar_selecao()
        self.atualizar_tudo()
        estado = self.jogo.estado()
        if estado.em_xeque:
            self._piscar_rei(self.jogo.turno)
        if estado.terminado and not estava_terminada:
            if estado.vencedor:
                texto = f"As {'brancas' if estado.vencedor == 'branco' else 'pretas'} venceram!"
                if estado.tipo == "xeque_mate":
                    texto += "\nXeque-mate!"
            else:
                texto = f"Empate!\nMotivo: {estado.motivo or estado.tipo}"
            messagebox.showinfo("Fim da partida", texto, parent=self)

    def _escolher_promocao(self, origem, destino):
        """Escolha de peça sem bloquear o programa ou mexer nas regras do core."""
        janela = ctk.CTkToplevel(self)
        janela.title("Promoção do peão")
        janela.geometry("290x215")
        janela.resizable(False, False)
        janela.transient(self)
        ctk.CTkLabel(
            janela, text="Promover peão para:", font=ctk.CTkFont(size=17, weight="bold")
        ).pack(pady=(16, 8))
        grade = ctk.CTkFrame(janela, fg_color="transparent")
        grade.pack(padx=14, fill="both", expand=True)
        for indice, nome in enumerate(("Rainha", "Torre", "Bispo", "Cavalo")):
            ctk.CTkButton(
                grade, text=nome, width=113, height=40,
                command=lambda escolha=nome: confirmar(escolha),
            ).grid(row=indice // 2, column=indice % 2, padx=5, pady=5)

        def confirmar(escolha):
            janela.grab_release()
            janela.destroy()
            self._jogar(origem, destino, escolha)

        janela.grab_set()
        janela.focus()

    def atualizar_casa(self, linha_tela: int, coluna_tela: int):
        linha, coluna = tela_para_modelo(linha_tela, coluna_tela, self.invertido)
        peca = self.jogo.tabuleiro.get_peca(linha, coluna)
        imagem = self.imagens[(peca.cor, type(peca).__name__)] if peca else self.imagens[None]
        cor = COR_CASA_CLARA if (linha_tela + coluna_tela) % 2 == 0 else COR_CASA_ESCURA
        if (linha, coluna) == self.casa_selecionada:
            cor = COR_SELECIONADA
        elif (linha, coluna) in self.movimentos_destacados:
            cor = COR_MOVIMENTO_VALIDO
        if (linha, coluna) == self.rei_destacado:
            cor = COR_REI_EM_XEQUE
        self.botoes[(linha_tela, coluna_tela)].configure(
            image=imagem, fg_color=cor, hover_color=cor,
        )

    def atualizar_tabuleiro(self):
        for linha in range(8):
            for coluna in range(8):
                self.atualizar_casa(linha, coluna)
        self.label_turnos.configure(
            text=f"Vez das {'brancas' if self.jogo.turno == 'branco' else 'pretas'}"
            if not self.jogo.estado().terminado else "Partida encerrada"
        )

    def atualizar_historico(self):
        for filho in self.rolagem_lances.winfo_children():
            filho.destroy()
        linhas = linhas_historico(self.jogo.notacoes)
        if not linhas:
            ctk.CTkLabel(
                self.rolagem_lances, text="Nenhum lance ainda.",
                font=ctk.CTkFont(size=13), text_color=COR_TEXTO_SECUNDARIO,
            ).grid(row=0, column=0, columnspan=3, pady=12, sticky="ew")
        for indice, (numero, brancas, pretas) in enumerate(linhas):
            textos = (str(numero), brancas, pretas)
            for coluna, conteudo in enumerate(textos):
                fundo = "#273240" if indice % 2 == 0 else "#1B232E"
                ctk.CTkLabel(
                    self.rolagem_lances, text=conteudo,
                    height=32, corner_radius=3, fg_color=fundo,
                    text_color=COR_TEXTO_SECUNDARIO if coluna == 0 else COR_TEXTO,
                    font=ctk.CTkFont(size=13),
                ).grid(row=indice, column=coluna, padx=(2, 0), pady=1, sticky="ew")
        if linhas:
            self.after_idle(
                lambda: self.rolagem_lances._parent_canvas.yview_moveto(1.0)
                if self.rolagem_lances.winfo_exists() else None
            )

    def atualizar_tudo(self):
        self.atualizar_tabuleiro()
        self.atualizar_historico()
        estado = self.jogo.estado()
        if estado.terminado:
            status = f"Encerrada • {estado.motivo or estado.tipo}"
        else:
            status = f"Em andamento • {len(self.jogo.notacoes)} lance(s)"
        self.label_partida.configure(
            text=f"Partida #{self.servico.partida_id}  |  {status}"
        )

    def _mostrar_aviso(self, texto: str):
        if self._temporizador_aviso is not None:
            self.after_cancel(self._temporizador_aviso)
        self.label_aviso.configure(text=texto)
        self._temporizador_aviso = self.after(3200, self._limpar_aviso)

    def _limpar_aviso(self):
        self._temporizador_aviso = None
        self.label_aviso.configure(text="")

    def _piscar_rei(self, cor: str):
        """Marca o rei em vermelho por exatos 2000 ms, sem bloquear a tela."""
        if self._temporizador_xeque is not None:
            self.after_cancel(self._temporizador_xeque)
        self.rei_destacado = self.jogo.tabuleiro.reis[cor].posicao_atual()
        self.atualizar_tabuleiro()
        self._temporizador_xeque = self.after(2000, self._terminar_destaque_rei)

    def _terminar_destaque_rei(self):
        self._temporizador_xeque = None
        self.rei_destacado = None
        self.atualizar_tabuleiro()

    def _avisar_xeque_ao_abrir(self):
        if self.jogo.estado().em_xeque:
            self._piscar_rei(self.jogo.turno)

    def _reiniciar_destaques(self):
        if self._temporizador_xeque is not None:
            self.after_cancel(self._temporizador_xeque)
            self._temporizador_xeque = None
        self.rei_destacado = None
        self.limpar_selecao()

    def nova_partida(self):
        if not messagebox.askyesno(
            "Nova partida", "Criar uma nova partida? A atual continuará salva no banco.",
            parent=self,
        ):
            return
        try:
            self.servico.criar_com_nomes()
        except Exception as erro:
            messagebox.showerror("Não foi possível iniciar a partida", str(erro), parent=self)
            return
        self._reiniciar_destaques()
        self.atualizar_tudo()
        self._mostrar_aviso("Nova partida criada. As brancas começam.")

    def voltar_lance(self):
        try:
            desfez = self.servico.desfazer()
        except (ValueError, PartidaEncerrada) as erro:
            self._mostrar_aviso(str(erro))
            return
        except Exception as erro:
            messagebox.showerror("Não foi possível desfazer o lance", str(erro), parent=self)
            return
        if not desfez:
            self._mostrar_aviso("Ainda não existem lances para voltar.")
            return
        self._reiniciar_destaques()
        self.atualizar_tudo()
        self._mostrar_aviso("Último lance removido do tabuleiro e do banco.")
        self._avisar_xeque_ao_abrir()

    def inverter_tabuleiro(self):
        self.invertido = not self.invertido
        self.limpar_selecao()
        self.atualizar_tabuleiro()

    def fechar(self):
        if self._temporizador_xeque is not None:
            self.after_cancel(self._temporizador_xeque)
        if self._temporizador_aviso is not None:
            self.after_cancel(self._temporizador_aviso)
        # Não há estado pendente em memória: toda jogada foi commitada.
        self.destroy()
