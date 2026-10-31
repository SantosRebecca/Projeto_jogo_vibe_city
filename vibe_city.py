import pygame
import random
import math
import sys

pygame.init()

# TELA CHEIA
info = pygame.display.Info()
LARGURA, ALTURA = info.current_w, info.current_h
tela = pygame.display.set_mode((LARGURA, ALTURA), pygame.FULLSCREEN)
pygame.display.set_caption("VIBE CITY: NEON RUSH")

relogio = pygame.time.Clock()

# CORES
PRETO = (8, 8, 22)
BRANCO = (240, 245, 255)
CIANO = (0, 230, 255)
ROXO = (165, 70, 255)
ROSA = (255, 50, 150)
VERMELHO = (255, 65, 75)
VERDE = (70, 255, 160)
AMARELO = (255, 220, 70)

fonte = pygame.font.SysFont("arial", 25, bold=True)
fonte_media = pygame.font.SysFont("arial", 42, bold=True)
fonte_grande = pygame.font.SysFont("arial", 76, bold=True)

# ESTADOS
MENU = "menu"
JOGANDO = "jogando"
PAUSADO = "pausado"
FIM = "fim"

estado = MENU

# FUNÇÕES VISUAIS
def texto(superficie, mensagem, fonte_usada, cor, x, y, centralizar=True):
    imagem = fonte_usada.render(mensagem, True, cor)
    retangulo = imagem.get_rect()
    if centralizar:
        retangulo.center = (x, y)
    else:
        retangulo.topleft = (x, y)
    superficie.blit(imagem, retangulo)


def distancia(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)


def barra(x, y, largura, altura, valor, maximo, cor):
    pygame.draw.rect(tela, (35, 35, 55), (x, y, largura, altura), border_radius=8)
    preenchimento = max(0, min(largura, largura * valor / maximo))
    pygame.draw.rect(tela, cor, (x, y, preenchimento, altura), border_radius=8)


# FUNDO ESTRELADO
estrelas = [
    [random.randint(0, LARGURA), random.randint(0, ALTURA),
     random.randint(1, 3), random.randint(15, 55)]
    for _ in range(100)
]


def desenhar_fundo():
    tela.fill(PRETO)

    for estrela in estrelas:
        x, y, tamanho, brilho = estrela
        pygame.draw.circle(tela, (brilho, brilho, brilho + 25),
                           (x, y), tamanho)

    # Grade futurista
    for x in range(0, LARGURA, 65):
        pygame.draw.line(tela, (18, 20, 48), (x, 0), (x, ALTURA), 1)

    for y in range(0, ALTURA, 65):
        pygame.draw.line(tela, (18, 20, 48), (0, y), (LARGURA, y), 1)


# PARTÍCULAS
particulas = []


def criar_particulas(x, y, cor, quantidade=12):
    for _ in range(quantidade):
        angulo = random.uniform(0, math.pi * 2)
        velocidade = random.uniform(1, 6)
        particulas.append([
            x, y,
            math.cos(angulo) * velocidade,
            math.sin(angulo) * velocidade,
            random.randint(3, 7),
            cor
        ])


def atualizar_particulas():
    for p in particulas[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[4] -= 0.12

        if p[4] <= 0:
            particulas.remove(p)
        else:
            pygame.draw.circle(
                tela, p[5],
                (int(p[0]), int(p[1])),
                max(1, int(p[4]))
            )


# JOGADOR
class Jogador:
    def __init__(self):
        self.x = LARGURA // 2
        self.y = ALTURA // 2
        self.raio = 19
        self.vida = 100
        self.energia = 100
        self.velocidade = 5
        self.ultimo_tiro = 0
        self.dash = 0
        self.dash_recarga = 0
        self.pulso_recarga = 0
        self.especial_recarga = 0
        self.invencivel = 0

    def atualizar(self, teclas):
        dx = 0
        dy = 0

        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            dy -= 1
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            dy += 1
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            dx -= 1
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            dx += 1

        if dx != 0 or dy != 0:
            tamanho = math.hypot(dx, dy)
            dx /= tamanho
            dy /= tamanho

        velocidade = self.velocidade

        if self.dash > 0:
            velocidade = 17
            self.dash -= 1

        self.x += dx * velocidade
        self.y += dy * velocidade

        self.x = max(self.raio, min(LARGURA - self.raio, self.x))
        self.y = max(self.raio, min(ALTURA - self.raio, self.y))

        if self.dash_recarga > 0:
            self.dash_recarga -= 1
        if self.pulso_recarga > 0:
            self.pulso_recarga -= 1
        if self.especial_recarga > 0:
            self.especial_recarga -= 1
        if self.invencivel > 0:
            self.invencivel -= 1

        self.energia = min(100, self.energia + 0.08)

    def desenhar(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angulo = math.atan2(mouse_y - self.y, mouse_x - self.x)

        pontos = []
        for ang, tamanho in [
            (0, 27), (2.5, 19), (-2.5, 19)
        ]:
            a = angulo + ang
            pontos.append((
                self.x + math.cos(a) * tamanho,
                self.y + math.sin(a) * tamanho
            ))

        cor = CIANO if self.invencivel <= 0 else BRANCO

        pygame.draw.circle(tela, (0, 100, 130),
                           (int(self.x), int(self.y)), 29)
        pygame.draw.polygon(tela, cor, pontos)
        pygame.draw.polygon(tela, BRANCO, pontos, 2)


# PROJÉTEIS
tiros = []


def atirar(jogador):
    agora = pygame.time.get_ticks()

    if agora - jogador.ultimo_tiro < 170:
        return

    mx, my = pygame.mouse.get_pos()
    angulo = math.atan2(my - jogador.y, mx - jogador.x)

    tiros.append([
        jogador.x, jogador.y,
        math.cos(angulo) * 12,
        math.sin(angulo) * 12,
        7
    ])

    jogador.ultimo_tiro = agora


def atualizar_tiros():
    for tiro in tiros[:]:
        tiro[0] += tiro[2]
        tiro[1] += tiro[3]

        pygame.draw.circle(
            tela, CIANO,
            (int(tiro[0]), int(tiro[1])), tiro[4]
        )

        pygame.draw.circle(
            tela, BRANCO,
            (int(tiro[0]), int(tiro[1])), 3
        )

        if (tiro[0] < 0 or tiro[0] > LARGURA or
                tiro[1] < 0 or tiro[1] > ALTURA):
            tiros.remove(tiro)


# INIMIGOS
inimigos = []


class Inimigo:
    def __init__(self, tipo, chefe=False):
        self.tipo = tipo
        self.chefe = chefe

        lado = random.randint(0, 3)

        if lado == 0:
            self.x, self.y = random.randint(0, LARGURA), -40
        elif lado == 1:
            self.x, self.y = LARGURA + 40, random.randint(0, ALTURA)
        elif lado == 2:
            self.x, self.y = random.randint(0, LARGURA), ALTURA + 40
        else:
            self.x, self.y = -40, random.randint(0, ALTURA)

        if chefe:
            self.vida = 35
            self.velocidade = 1.3
            self.raio = 43
            self.dano = 30
        elif tipo == "rapido":
            self.vida = 2
            self.velocidade = 3.1
            self.raio = 13
            self.dano = 12
        elif tipo == "tanque":
            self.vida = 8
            self.velocidade = 0.9
            self.raio = 27
            self.dano = 22
        else:
            self.vida = 4
            self.velocidade = 1.7
            self.raio = 19
            self.dano = 15

        self.ultimo_ataque = 0

    def atualizar(self, jogador):
        dx = jogador.x - self.x
        dy = jogador.y - self.y
        d = max(1, math.hypot(dx, dy))

        self.x += dx / d * self.velocidade
        self.y += dy / d * self.velocidade

        if self.chefe:
            cor = ROSA
        elif self.tipo == "rapido":
            cor = AMARELO
        elif self.tipo == "tanque":
            cor = ROXO
        else:
            cor = VERMELHO

        pygame.draw.circle(
            tela, cor,
            (int(self.x), int(self.y)), self.raio
        )

        pygame.draw.circle(
            tela, BRANCO,
            (int(self.x), int(self.y)), self.raio, 2
        )

        # Olhos
        pygame.draw.circle(
            tela, PRETO,
            (int(self.x - 6), int(self.y - 4)), 3
        )
        pygame.draw.circle(
            tela, PRETO,
            (int(self.x + 6), int(self.y - 4)), 3
        )


# REINICIAR PARTIDA
def nova_partida():
    global jogador, inimigos, tiros, pontos, onda
    global inimigos_criados, tempo_spawn, chefe_ativo

    jogador = Jogador()
    inimigos = []
    tiros = []
    particulas.clear()

    pontos = 0
    onda = 1
    inimigos_criados = 0
    tempo_spawn = 0
    chefe_ativo = False


nova_partida()


# HUD
def desenhar_hud():
    texto(tela, "VIBE CITY", fonte_media, CIANO, 115, 40)
    texto(tela, f"PONTOS: {pontos}", fonte, BRANCO, 35, 85, False)
    texto(tela, f"ONDA: {onda}", fonte, AMARELO, 35, 120, False)

    texto(tela, "VIDA", fonte, BRANCO, 35, ALTURA - 95, False)
    barra(110, ALTURA - 92, 220, 20, jogador.vida, 100, VERDE)

    texto(tela, "ENERGIA", fonte, BRANCO, 35, ALTURA - 58, False)
    barra(145, ALTURA - 55, 185, 16,
          jogador.energia, 100, CIANO)

    texto(tela, "ESPAÇO: DASH", fonte, CIANO,
          LARGURA - 270, ALTURA - 90)
    texto(tela, "Q: PULSO  |  E: ESPECIAL", fonte,
          ROXO, LARGURA - 270, ALTURA - 55)


# MENU
def desenhar_menu():
    desenhar_fundo()

    texto(tela, "VIBE CITY", fonte_grande, CIANO,
          LARGURA // 2, ALTURA // 2 - 155)

    texto(tela, "N E O N   R U S H", fonte_media, ROSA,
          LARGURA // 2, ALTURA // 2 - 85)

    texto(tela, "A cidade precisa de você.", fonte,
          BRANCO, LARGURA // 2, ALTURA // 2 - 15)

    texto(tela, "DESTRUA OS DRONES. SOBREVIVA ÀS ONDAS.",
          fonte, AMARELO, LARGURA // 2, ALTURA // 2 + 35)

    pygame.draw.rect(
        tela, CIANO,
        (LARGURA // 2 - 160, ALTURA // 2 + 100, 320, 65),
        border_radius=15
    )

    texto(tela, "PRESSIONE ENTER", fonte, PRETO,
          LARGURA // 2, ALTURA // 2 + 132)

    texto(tela, "WASD: mover | Mouse: mirar e atirar",
          fonte, BRANCO, LARGURA // 2, ALTURA - 110)

    texto(tela, "ESPAÇO: dash | Q: pulso | E: especial",
          fonte, BRANCO, LARGURA // 2, ALTURA - 75)


# CONTROLES ESPECIAIS
def usar_pulso():
    global inimigos, pontos

    if jogador.pulso_recarga > 0 or jogador.energia < 30:
        return

    jogador.energia -= 30
    jogador.pulso_recarga = 240

    for inimigo in inimigos[:]:
        if distancia(jogador.x, jogador.y,
                     inimigo.x, inimigo.y) < 190:
            inimigo.vida -= 4
            criar_particulas(inimigo.x, inimigo.y, CIANO, 15)

            if inimigo.vida <= 0:
                inimigos.remove(inimigo)
                pontos += 20


def usar_especial():
    global inimigos, pontos

    if jogador.especial_recarga > 0 or jogador.energia < 65:
        return

    jogador.energia -= 65
    jogador.especial_recarga = 600

    # Explosão que atinge todos os inimigos
    for inimigo in inimigos[:]:
        inimigo.vida -= 12
        criar_particulas(inimigo.x, inimigo.y, ROSA, 22)

        if inimigo.vida <= 0:
            inimigos.remove(inimigo)
            pontos += 30

    criar_particulas(jogador.x, jogador.y, ROSA, 65)


# LOOP PRINCIPAL
rodando = True

while rodando:
    dt = relogio.tick(60)
    desenhar_fundo()

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.KEYDOWN:

            if evento.key == pygame.K_ESCAPE:
                rodando = False

            if estado == MENU:
                if evento.key == pygame.K_RETURN:
                    nova_partida()
                    estado = JOGANDO

            elif estado == JOGANDO:

                if evento.key == pygame.K_p:
                    estado = PAUSADO

                if evento.key == pygame.K_SPACE:
                    if jogador.dash_recarga <= 0:
                        jogador.dash = 12
                        jogador.dash_recarga = 100
                        jogador.invencivel = 18
                        criar_particulas(
                            jogador.x, jogador.y, CIANO, 18
                        )

                if evento.key == pygame.K_q:
                    usar_pulso()

                if evento.key == pygame.K_e:
                    usar_especial()

            elif estado == PAUSADO:
                if evento.key == pygame.K_p:
                    estado = JOGANDO

                if evento.key == pygame.K_RETURN:
                    estado = MENU

            elif estado == FIM:
                if evento.key == pygame.K_RETURN:
                    nova_partida()
                    estado = JOGANDO

                if evento.key == pygame.K_m:
                    estado = MENU

    # MENU
    if estado == MENU:
        desenhar_menu()

    # JOGO
    elif estado == JOGANDO:

        teclas = pygame.key.get_pressed()
        jogador.atualizar(teclas)

        if pygame.mouse.get_pressed()[0]:
            atirar(jogador)

        # CRIAÇÃO DAS ONDAS
        tempo_spawn += dt

        limite_inimigos = min(5 + onda * 2, 18)

        if len(inimigos) < limite_inimigos:
            if tempo_spawn > max(350, 1250 - onda * 65):
                tempo_spawn = 0

                tipo = random.choice(["normal", "rapido", "tanque"])
                inimigos.append(Inimigo(tipo))
                inimigos_criados += 1

        # CHEFÃO A CADA 5 ONDAS
        if onda % 5 == 0 and not chefe_ativo:
            if not any(i.chefe for i in inimigos):
                inimigos.append(Inimigo("chefe", True))
                chefe_ativo = True

        # ATUALIZA TIROS
        atualizar_tiros()

        # ATUALIZA INIMIGOS
        for inimigo in inimigos[:]:
            inimigo.atualizar(jogador)

            # Colisão com tiro
            for tiro in tiros[:]:
                if distancia(tiro[0], tiro[1],
                             inimigo.x, inimigo.y) < inimigo.raio + 7:

                    inimigo.vida -= 1

                    if tiro in tiros:
                        tiros.remove(tiro)

                    criar_particulas(
                        inimigo.x, inimigo.y, CIANO, 5
                    )

                    if inimigo.vida <= 0:
                        criar_particulas(
                            inimigo.x, inimigo.y, ROSA, 20
                        )

                        if inimigo in inimigos:
                            inimigos.remove(inimigo)

                        pontos += 100 if inimigo.chefe else 20

                        if inimigo.chefe:
                            chefe_ativo = False

                    break

            # Colisão com jogador
            if inimigo in inimigos:
                if distancia(jogador.x, jogador.y,
                             inimigo.x, inimigo.y) < (
                                 jogador.raio + inimigo.raio
                             ):

                    if jogador.invencivel <= 0:
                        jogador.vida -= inimigo.dano
                        jogador.invencivel = 55

                        criar_particulas(
                            jogador.x, jogador.y, VERMELHO, 25
                        )

        # EVOLUÇÃO DAS ONDAS
        if pontos >= onda * 250:
            onda += 1
            jogador.vida = min(100, jogador.vida + 15)
            jogador.energia = min(100, jogador.energia + 25)

            criar_particulas(
                LARGURA // 2, ALTURA // 2, AMARELO, 50
            )

        jogador.desenhar()
        atualizar_particulas()
        desenhar_hud()

        if jogador.vida <= 0:
            estado = FIM

        # INDICADOR DE CHEFÃO
        if any(i.chefe for i in inimigos):
            texto(tela, "CHEFÃO!", fonte_media, ROSA,
                  LARGURA // 2, 45)

            chefe = next(i for i in inimigos if i.chefe)
            barra(LARGURA // 2 - 170, 80, 340, 18,
                  chefe.vida, 35, ROSA)

    # PAUSA
    elif estado == PAUSADO:
        texto(tela, "JOGO PAUSADO", fonte_grande, CIANO,
              LARGURA // 2, ALTURA // 2 - 50)

        texto(tela, "P para continuar", fonte_media,
              BRANCO, LARGURA // 2, ALTURA // 2 + 35)

        texto(tela, "ENTER para voltar ao menu",
              fonte, ROSA, LARGURA // 2, ALTURA // 2 + 90)

    # FIM DE JOGO
    elif estado == FIM:
        texto(tela, "FIM DE JOGO", fonte_grande, ROSA,
              LARGURA // 2, ALTURA // 2 - 100)

        texto(tela, f"PONTUAÇÃO FINAL: {pontos}",
              fonte_media, BRANCO,
              LARGURA // 2, ALTURA // 2 - 15)

        texto(tela, f"ONDAS SOBREVIVIDAS: {onda}",
              fonte, AMARELO,
              LARGURA // 2, ALTURA // 2 + 35)

        texto(tela, "ENTER para jogar novamente",
              fonte, CIANO, LARGURA // 2, ALTURA // 2 + 105)

        texto(tela, "M para voltar ao menu",
              fonte, BRANCO, LARGURA // 2, ALTURA // 2 + 145)

    pygame.display.flip()

pygame.quit()
sys.exit()
