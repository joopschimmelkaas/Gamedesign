import pygame
import sys
import random
 
pygame.init()
 
# ---------- Basis instellingen ----------
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker")
 
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("arial", 24)
BIG_FONT = pygame.font.SysFont("arial", 48)
SMALL_FONT = pygame.font.SysFont("arial", 18)
 
# ---------- Kleuren ----------
BG = (10, 10, 30)
WHITE = (255, 255, 255)
HINT = (180, 180, 180)
 
PADDLE_COLOR = (220, 220, 220)
BALL_COLOR = (250, 250, 250)
 
BRICK_COLORS = [
    (50, 150, 250),
    (250, 200, 50),
    (0, 200, 150),
    (200, 80, 200),
]
 
SOLID_COLOR = (120, 120, 120)
QUIT_COLOR = (220, 40, 40)
 
POWERUP_COLORS = {
    "life": (0, 200, 0),
    "expand": (0, 150, 255),
    "slow": (255, 215, 0),
}
 
# Powerup instellingen
POWERUP_SIZE = 20
POWERUP_SPEED = 4
POWERUP_CHANCE = 0.25  # 25%
 
# ---------- Singleplayer Levels (1 t/m 4) ----------
# 0 = leeg, 1 = breekbaar, 2 = onbreekbaar (grijs)
LEVELS = [
    # Level 1: simpel
    [
        [1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1],
        [1,1,1,1,1,1,1,1,1,1],
    ],
    # Level 2: checkerboard
    [
        [1,0,1,0,1,0,1,0,1,0],
        [0,1,0,1,0,1,0,1,0,1],
        [1,0,1,0,1,0,1,0,1,0],
        [0,1,0,1,0,1,0,1,0,1],
    ],
    # Level 3: piramide
    [
        [0,0,0,1,1,1,1,0,0,0],
        [0,0,1,1,1,1,1,1,0,0],
        [0,1,1,1,1,1,1,1,1,0],
        [1,1,1,1,1,1,1,1,1,1],
    ],
    # Level 4: met onbreekbare rand
    [
        [2,2,2,2,2,2,2,2,2,2,2,2,2,2],
        [2,1,1,1,1,1,1,1,1,1,1,1,1,2],
        [2,1,1,1,1,1,1,1,1,1,1,1,1,2],
        [2,0,0,0,0,0,0,0,0,0,0,0,0,2],
        [2,1,1,1,1,1,1,1,1,1,1,1,1,2],
        [2,1,1,1,1,1,1,1,1,1,1,1,1,2],
        [2,0,0,0,0,0,0,0,0,0,0,0,0,2],
        [2,1,1,1,1,1,1,1,1,1,1,1,1,2],
        [2,1,1,1,1,1,1,1,1,1,1,1,1,2],
        [2,2,2,2,2,0,0,0,2,2,2,2,2,2],
    ],
]
 
# ---------- Paddle & Bal ----------
PADDLE_W, PADDLE_H = 100, 15
BALL_SIZE = 12
 
paddle = pygame.Rect(WIDTH//2 - PADDLE_W//2, HEIGHT-40, PADDLE_W, PADDLE_H)
ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2, BALL_SIZE, BALL_SIZE)
 
paddle_speed = 8
ball_speed_x, ball_speed_y = 4, -4
 
# ---------- Menu knoppen ----------
BTN_W, BTN_H = 300, 50
start_button = pygame.Rect(WIDTH//2 - BTN_W//2, 230, BTN_W, BTN_H)
levels_button = pygame.Rect(WIDTH//2 - BTN_W//2, 300, BTN_W, BTN_H)
guide_button = pygame.Rect(WIDTH//2 - BTN_W//2, 370, BTN_W, BTN_H)
 
# Quit-knop in-game
QUIT_W, QUIT_H = 120, 40
quit_button = pygame.Rect(WIDTH - QUIT_W - 20, HEIGHT - QUIT_H - 20, QUIT_W, QUIT_H)
 
# ---------- Game state ----------
state = "menu"
current_level = 0
bricks = []
powerups = []
score = 0
lives = 3
level_buttons = []
 
 
# ---------- Bricks helpers ----------
 
def create_bricks(level_index):
    # Fix: maak kopie van iedere rij, zodat levels niet stuk gaan
    layout_src = LEVELS[level_index]
    layout = [row[:] for row in layout_src]
 
    rows = len(layout)
    cols = len(layout[0])
    brick_width = (WIDTH - 80) // cols
    brick_height = 25
 
    bricks_list = []
    for r in range(rows):
        for c in range(cols):
            val = layout[r][c]
            if val == 0:
                continue
 
            x = 40 + c * brick_width
            y = 60 + r * brick_height
            rect = pygame.Rect(x, y, brick_width - 4, brick_height - 4)
 
            if val == 2:
                color = SOLID_COLOR
                btype = "solid"
            else:
                color = BRICK_COLORS[level_index % len(BRICK_COLORS)]
                btype = "normal"
 
            bricks_list.append({"rect": rect, "color": color, "type": btype})
 
    return bricks_list
 
 
def load_level(i):
    global current_level, bricks, powerups
    current_level = i
    bricks = create_bricks(i)
    powerups = []
 
 
def reset_ball_and_paddle():
    global ball, ball_speed_x, ball_speed_y, paddle
    paddle.width = PADDLE_W
    paddle.x = WIDTH//2 - paddle.width//2
    paddle.y = HEIGHT - 40
    ball.x = WIDTH//2 - BALL_SIZE//2
    ball.y = HEIGHT//2
    ball_speed_x, ball_speed_y = 4, -4
 
 
def reset_full_game():
    global score, lives
    score = 0
    lives = 3
    load_level(0)
    reset_ball_and_paddle()
 
 
# ---------- Powerups ----------
 
def apply_powerup(ptype):
    global lives, paddle, ball_speed_x, ball_speed_y
 
    if ptype == "life":
        lives += 1
 
    elif ptype == "expand":
        new_w = min(paddle.width + 40, 220)
        center = paddle.centerx
        paddle.width = new_w
        paddle.x = max(0, min(center - paddle.width//2, WIDTH - paddle.width))
 
    elif ptype == "slow":
        if ball_speed_x != 0:
            sx = 1 if ball_speed_x > 0 else -1
            ball_speed_x = max(2, abs(ball_speed_x) - 1) * sx
        if ball_speed_y != 0:
            sy = 1 if ball_speed_y > 0 else -1
            ball_speed_y = max(2, abs(ball_speed_y) - 1) * sy
 
 
def spawn_powerup(x, y):
    if random.random() < POWERUP_CHANCE:
        ptype = random.choice(list(POWERUP_COLORS.keys()))
        rect = pygame.Rect(x - POWERUP_SIZE//2, y, POWERUP_SIZE, POWERUP_SIZE)
        powerups.append({"rect": rect, "type": ptype})
 
 
def update_powerups():
    for p in powerups[:]:
        p["rect"].y += POWERUP_SPEED
        if p["rect"].colliderect(paddle):
            apply_powerup(p["type"])
            powerups.remove(p)
        elif p["rect"].top > HEIGHT:
            powerups.remove(p)
 
 
def draw_powerups():
    for p in powerups:
        color = POWERUP_COLORS[p["type"]]
        pygame.draw.rect(screen, color, p["rect"], border_radius=4)
        letter = {"life": "+", "expand": "E", "slow": "S"}[p["type"]]
        t = FONT.render(letter, True, (0, 0, 0))
        screen.blit(
            t,
            (p["rect"].centerx - t.get_width()//2,
             p["rect"].centery - t.get_height()//2),
        )
 
 
# ---------- UI tekenfuncties ----------
 
def draw_menu():
    screen.fill(BG)
    title = BIG_FONT.render("BRICK BREAKER", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
 
    for rect, color, text in [
        (start_button, (70, 160, 70), "START GAME"),
        (levels_button, (70, 70, 160), "LEVELS"),
        (guide_button, (160, 100, 50), "HANDLEIDING"),
    ]:
        pygame.draw.rect(screen, color, rect, border_radius=10)
        t = FONT.render(text, True, WHITE)
        screen.blit(
            t,
            (rect.centerx - t.get_width()//2,
             rect.centery - t.get_height()//2),
        )
 
    hint = FONT.render("ESC = Afsluiten", True, HINT)
    screen.blit(hint, (WIDTH//2 - hint.get_width()//2, 470))
 
 
def draw_hud():
    s = FONT.render(f"Score: {score}", True, WHITE)
    l = FONT.render(f"Levens: {lives}", True, WHITE)
    v = FONT.render(f"Level: {current_level+1}/5", True, WHITE)
    screen.blit(s, (10, 10))
    screen.blit(v, (WIDTH//2 - v.get_width()//2, 10))
    screen.blit(l, (WIDTH - l.get_width() - 10, 10))
 
 
def draw_quit():
    pygame.draw.rect(screen, QUIT_COLOR, quit_button, border_radius=8)
    t = FONT.render("MENU", True, WHITE)
    screen.blit(
        t,
        (quit_button.centerx - t.get_width()//2,
         quit_button.centery - t.get_height()//2),
    )
 
 
def draw_levels_menu():
    global level_buttons
    screen.fill(BG)
    title = BIG_FONT.render("Kies een level", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
 
    level_buttons = []
    total = len(LEVELS) + 1  # +1 voor Level 5 (2-player)
    for i in range(total):
        r = pygame.Rect(WIDTH//2 - BTN_W//2, 220 + i*60, BTN_W, BTN_H)
        level_buttons.append((r, i))
        pygame.draw.rect(screen, (60, 60, 140), r, border_radius=10)
        t = FONT.render(f"Level {i+1}", True, WHITE)
        screen.blit(
            t,
            (r.centerx - t.get_width()//2,
             r.centery - t.get_height()//2),
        )
 
    back = FONT.render("M / ESC = terug naar menu", True, HINT)
    screen.blit(back, (WIDTH//2 - back.get_width()//2, 500))
 
 
def draw_guide():
    screen.fill(BG)
    title = BIG_FONT.render("HANDLEIDING", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
 
    lines = [
        "Besturing:",
        "  Links / Rechts pijltje - beweeg de paddle",
        "  Rode MENU-knop - terug naar hoofdmenu",
        "",
        "Doel:",
        "  Breek alle gekleurde blokken.",
        "  Grijze blokken zijn onbreekbaar.",
        "",
        "Power-ups:",
        "  + = extra leven",
        "  E = grotere paddle",
        "  S = langzamere bal",
        "",
        "Level 5 (2-speler):",
        "  Links: A / D  (rode paddle)",
        "  Rechts: pijltjes (blauwe paddle)",
        "  Wie als eerste zijn blokken sloopt wint.",
        "",
        "M / ESC = terug naar menu",
    ]
 
    y = 150
    for line in lines:
        color = HINT if line.startswith("  ") else WHITE
        t = SMALL_FONT.render(line, True, color)
        screen.blit(t, (70, y))
        y += 24
 
 
def draw_game_over():
    screen.fill(BG)
    t = BIG_FONT.render("GAME OVER", True, WHITE)
    s = FONT.render(f"Score: {score}", True, WHITE)
    r = FONT.render("ENTER / SPATIE = opnieuw", True, HINT)
    m = FONT.render("M = terug naar menu", True, HINT)
    screen.blit(t, (WIDTH//2 - t.get_width()//2, 170))
    screen.blit(s, (WIDTH//2 - s.get_width()//2, 230))
    screen.blit(r, (WIDTH//2 - r.get_width()//2, 290))
    screen.blit(m, (WIDTH//2 - m.get_width()//2, 330))
 
 
def draw_win():
    screen.fill(BG)
    t = BIG_FONT.render("YOU WIN!", True, WHITE)
    s = FONT.render(f"Eindscore: {score}", True, WHITE)
    r = FONT.render("ENTER / SPATIE = opnieuw", True, HINT)
    m = FONT.render("M = terug naar menu", True, HINT)
    screen.blit(t, (WIDTH//2 - t.get_width()//2, 170))
    screen.blit(s, (WIDTH//2 - s.get_width()//2, 230))
    screen.blit(r, (WIDTH//2 - r.get_width()//2, 290))
    screen.blit(m, (WIDTH//2 - m.get_width()//2, 330))
 
 
# ---------- Level 5: 2-player versus ----------
 
def play_level5():
    half_w = WIDTH // 2
    cols, rows = 7, 4
    bw = (half_w - 80) // cols
    bh = 25
 
    left_bricks = [pygame.Rect(40 + c*bw, 60 + r*bh, bw-4, bh-4)
                   for r in range(rows) for c in range(cols)]
    right_bricks = [pygame.Rect(half_w + 40 + c*bw, 60 + r*bh, bw-4, bh-4)
                    for r in range(rows) for c in range(cols)]
 
    p1 = pygame.Rect(half_w//2 - 50, HEIGHT-40, 100, 15)
    p2 = pygame.Rect(half_w + half_w//2 - 50, HEIGHT-40, 100, 15)
 
    b1 = pygame.Rect(p1.centerx - 6, HEIGHT//2, 12, 12)
    b2 = pygame.Rect(p2.centerx - 6, HEIGHT//2, 12, 12)
 
    v1 = [4, -4]
    v2 = [-4, -4]
 
    winner = 0
 
    while True:
        clock.tick(60)
 
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return
 
        keys = pygame.key.get_pressed()
        # Player 1
        if keys[pygame.K_a] and p1.left > 0:
            p1.x -= 8
        if keys[pygame.K_d] and p1.right < half_w - 4:
            p1.x += 8
        # Player 2
        if keys[pygame.K_LEFT] and p2.left > half_w + 4:
            p2.x -= 8
        if keys[pygame.K_RIGHT] and p2.right < WIDTH:
            p2.x += 8
 
        # Bal 1 (links)
        b1.x += v1[0]
        b1.y += v1[1]
        if b1.left <= 0 or b1.right >= half_w - 2:
            v1[0] *= -1
        if b1.top <= 0:
            v1[1] *= -1
        if b1.colliderect(p1) and v1[1] > 0:
            v1[1] *= -1
        for r in left_bricks[:]:
            if b1.colliderect(r):
                v1[1] *= -1
                left_bricks.remove(r)
                break
        if b1.bottom > HEIGHT:
            b1.x = p1.centerx - 6
            b1.y = HEIGHT//2
            v1[:] = [4, -4]
 
        # Bal 2 (rechts)
        b2.x += v2[0]
        b2.y += v2[1]
        if b2.left <= half_w + 2 or b2.right >= WIDTH:
            v2[0] *= -1
        if b2.top <= 0:
            v2[1] *= -1
        if b2.colliderect(p2) and v2[1] > 0:
            v2[1] *= -1
        for r in right_bricks[:]:
            if b2.colliderect(r):
                v2[1] *= -1
                right_bricks.remove(r)
                break
        if b2.bottom > HEIGHT:
            b2.x = p2.centerx - 6
            b2.y = HEIGHT//2
            v2[:] = [-4, -4]
 
        # Win check
        if not left_bricks and winner == 0:
            winner = 1
        if not right_bricks and winner == 0:
            winner = 2
 
        screen.fill(BG)
        # Middenlijn
        pygame.draw.line(screen, SOLID_COLOR, (half_w, 0), (half_w, HEIGHT), 2)
 
        for r in left_bricks:
            pygame.draw.rect(screen, (230, 60, 60), r)
        for r in right_bricks:
            pygame.draw.rect(screen, (60, 130, 255), r)
 
        pygame.draw.rect(screen, (230, 60, 60), p1)
        pygame.draw.rect(screen, (60, 130, 255), p2)
        pygame.draw.ellipse(screen, (230, 60, 60), b1)
        pygame.draw.ellipse(screen, (60, 130, 255), b2)
 
        if winner:
            msg = "PLAYER 1 WINS!" if winner == 1 else "PLAYER 2 WINS!"
            col = (230, 60, 60) if winner == 1 else (60, 130, 255)
            t = BIG_FONT.render(msg, True, col)
            screen.blit(t, (WIDTH//2 - t.get_width()//2, HEIGHT//2 - 40))
            s = FONT.render("ENTER / M / ESC = terug naar menu", True, WHITE)
            screen.blit(s, (WIDTH//2 - s.get_width()//2, HEIGHT//2 + 20))
            pygame.display.flip()
 
            waiting = True
            while waiting:
                clock.tick(30)
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if ev.type == pygame.KEYDOWN and ev.key in (
                        pygame.K_RETURN, pygame.K_m, pygame.K_ESCAPE
                    ):
                        return
 
        pygame.display.flip()
 
 
# ---------- Init ----------
load_level(0)
reset_ball_and_paddle()
 
 
# ---------- Main loop ----------
running = True
while running:
    clock.tick(60)
 
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
 
        if state == "menu":
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if start_button.collidepoint(e.pos):
                    reset_full_game()
                    state = "playing"
                elif levels_button.collidepoint(e.pos):
                    state = "levels"
                elif guide_button.collidepoint(e.pos):
                    state = "guide"
 
        elif state == "levels":
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_m):
                state = "menu"
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                for r, idx in level_buttons:
                    if r.collidepoint(e.pos):
                        if idx == len(LEVELS):  # Level 5 (versus)
                            play_level5()
                            state = "menu"
                        else:
                            load_level(idx)
                            reset_ball_and_paddle()
                            score = 0
                            lives = 3
                            state = "playing"
 
        elif state in ("game_over", "win"):
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_RETURN, pygame.K_SPACE):
                    reset_full_game()
                    state = "playing"
                elif e.key == pygame.K_m:
                    state = "menu"
 
        elif state == "playing":
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if quit_button.collidepoint(e.pos):
                    state = "menu"
 
        elif state == "guide":
            if e.type == pygame.KEYDOWN and e.key in (pygame.K_m, pygame.K_ESCAPE):
                state = "menu"
 
    # ---------- Update & Draw ----------
    if state == "menu":
        draw_menu()
 
    elif state == "levels":
        draw_levels_menu()
 
    elif state == "guide":
        draw_guide()
 
    elif state == "playing":
        # Paddle beweging
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and paddle.left > 0:
            paddle.x -= paddle_speed
        if keys[pygame.K_RIGHT] and paddle.right < WIDTH:
            paddle.x += paddle_speed
 
        # Bal bewegen
        ball.x += ball_speed_x
        ball.y += ball_speed_y
 
        # Muren
        if ball.left <= 0 or ball.right >= WIDTH:
            ball_speed_x *= -1
        if ball.top <= 0:
            ball_speed_y *= -1
 
        # Paddle
        if ball.colliderect(paddle) and ball_speed_y > 0:
            ball_speed_y *= -1
 
        # Botsing met bricks (incl. zij-detectie, solid blijft staan)
        hit_block = None
        for b in bricks:
            if ball.colliderect(b["rect"]):
                hit_block = b
                break
 
        if hit_block:
            rect = hit_block["rect"]
            # Overlaps berekenen
            overlap_left = ball.right - rect.left
            overlap_right = rect.right - ball.left
            overlap_top = ball.bottom - rect.top
            overlap_bottom = rect.bottom - ball.top
            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
 
            if min_overlap == overlap_left:
                ball.right = rect.left
                ball_speed_x *= -1
            elif min_overlap == overlap_right:
                ball.left = rect.right
                ball_speed_x *= -1
            elif min_overlap == overlap_top:
                ball.bottom = rect.top
                ball_speed_y *= -1
            else:
                ball.top = rect.bottom
                ball_speed_y *= -1
 
            if hit_block["type"] == "normal":
                bricks.remove(hit_block)
                score += 10
                spawn_powerup(rect.centerx, rect.bottom)
 
        update_powerups()
 
        # Bal gemist
        if ball.top > HEIGHT:
            lives -= 1
            if lives > 0:
                reset_ball_and_paddle()
            else:
                state = "game_over"
 
        # Level klaar? (alleen normale bricks tellen)
        if not any(b["type"] == "normal" for b in bricks):
            if current_level + 1 < len(LEVELS):
                load_level(current_level + 1)
                reset_ball_and_paddle()
            else:
                state = "win"
 
        # Teken singleplayer
        screen.fill(BG)
        for b in bricks:
            pygame.draw.rect(screen, b["color"], b["rect"])
        pygame.draw.rect(screen, PADDLE_COLOR, paddle)
        pygame.draw.ellipse(screen, BALL_COLOR, ball)
        draw_powerups()
        draw_hud()
        draw_quit()
 
    elif state == "game_over":
        draw_game_over()
 
    elif state == "win":
        draw_win()
 
    pygame.display.flip()