from pygame import *
import socket
import json
from threading import Thread

# ---ПУГАМЕ НАЛАШТУВАННЯ ---
WIDTH, HEIGHT = 800, 600
init()
mixer.init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")
# ---СЕРВЕР ---

backimage = image.load("Hmm.png")
backimage = transform.scale(backimage,(WIDTH,HEIGHT))
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080)) # ---- Підключення до сервера
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass


def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break

# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)
fontscore = font.Font(None,56)
fontsmall = font.Font(None,20)

# --- ANIM ---
balltrail = []
# --- ЗОБРАЖЕННЯ ----

# --- ЗВУКИ ---
wallsound = mixer.Sound("musicholder-hitting-stalactites-with-axe-212652.mp3")
platsound = mixer.Sound("dragon-studio-tennis-ball-hit-386155.mp3")


# --- ГРА ---
game_over = False
winner = None
you_winner = None

padeffect = 0

my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()
while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

    if "countdown" in game_state and game_state["countdown"] > 0:
        screen.fill((0, 0, 0))
        countdown_text = font.Font(None, 72).render(str(game_state["countdown"]), True, (255, 255, 255))
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
        display.update()
        continue  # Не малюємо гру до завершення відліку

    if "winner" in game_state and game_state["winner"] is not None:
        screen.fill((20, 20, 20))

        if you_winner is None:  # Встановлюємо тільки один раз
            if game_state["winner"] == my_id:
                you_winner = True
            else:
                you_winner = False

        if you_winner:
            text = "Ти переміг!"
        else:
            text = "Пощастить наступним разом!"

        win_text = font_win.render(text, True, (255, 215, 0))
        text_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(win_text, text_rect)

        text = font_win.render('К - рестарт', True, (255, 215, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
        screen.blit(text, text_rect)

        display.update()
        continue  # Блокує гру після перемоги

    if game_state:
        ballx = game_state["ball"]["x"]
        bally = game_state["ball"]["y"]
        if game_state["sound_event"] == "platform_hit":
            padeffect = 10
        balltrail.append((ballx,bally))
        if len(balltrail) > 15:
            balltrail.pop(0)

        #screen.fill((30, 30, 30))
        screen.blit(backimage,(0,0))
        #draw.rect(screen, (0, 255, 0), (20, game_state['paddles']['0'], 20, 100))
        #draw.rect(screen, (255, 0, 255), (WIDTH - 40, game_state['paddles']['1'], 20, 100))
        if padeffect >0:
            padcolor0 = (112,30,240)
            padcolor1 = (20,30,200),
            padeffect -=1
        else:
            padcolor0 = (0,255,0)
            padcolor1 = (255,0,255)
        draw.rect(screen, padcolor0, (20, game_state['paddles']['0'], 20, 100))
        draw.rect(screen, padcolor1, (WIDTH - 40, game_state['paddles']['1'], 20, 100))
        for i, pos in enumerate(balltrail):
            alpha = int((i / len(balltrail)) * 255)
            radius = int(3 + (i / len(balltrail)) * 7)
            trailsurface = Surface((30,30), SRCALPHA)
            draw.circle(trailsurface, (0,150,255, alpha), (15,15), radius)
            screen.blit(trailsurface, (pos[0] - 15, pos[1] - 15))
        draw.circle(screen, (255, 255, 255), (ballx,bally), 10)
        score_text = fontscore.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center = (WIDTH // 2, 35))
        screen.blit(score_text, score_rect)

        if game_state['sound_event']:
            if game_state['sound_event'] == 'wall_hit':
                # звук відбиття м'ячика від стін
                wallsound.play()
                pass
            if game_state['sound_event'] == 'platform_hit':
                # звук відбиття м'ячика від платформи
                platsound.play()
                pass

    else:
        wating_text = font_main.render(f"Очікування гравців...", True, (255, 255, 255))
        screen.blit(wating_text, (WIDTH // 2 - 25, 20))

    display.update()
    clock.tick(60)

    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")
