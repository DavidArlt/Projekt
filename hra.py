

import pygame
import random
import sqlite3

# Inicializace Pygame
pygame.init()

# Nastavení okna
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hvězdný posel")

# Barvy
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# Font
font = pygame.font.Font(None, 36)

# Připojení k databázi
conn = sqlite3.connect("scores.db")
cursor = conn.cursor()

# Vytvoření tabulky, pokud neexistuje
cursor.execute("""
CREATE TABLE IF NOT EXISTS highscores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    score INTEGER NOT NULL
)
""")
conn.commit()

def draw_text(text, x, y, color=WHITE):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def save_score(name, score):
    """Uloží skóre hráče do databáze."""
    cursor.execute("INSERT INTO highscores (name, score) VALUES (?, ?)", (name, score))
    conn.commit()

def show_highscores():
    """Zobrazí nejlepší skóre z databáze."""
    screen.fill((0, 0, 0))
    draw_text("Nejlepší skóre:", WIDTH // 2 - 100, 100)
    
    cursor.execute("SELECT name, score FROM highscores ORDER BY score DESC LIMIT 3")
    scores = cursor.fetchall()
    
    if scores:
        for i, (name, score) in enumerate(scores):
            draw_text(f"{name}: {score}", WIDTH // 2 - 100, 150 + i * 40)
    else:
        draw_text("Žádná skóre zatím nejsou.", WIDTH // 2 - 100, 150)

    pygame.display.update()
    pygame.time.delay(3000)

def main_menu():
    """Hlavní menu hry, kde hráč zadává přezdívku."""
    global player_name
    input_active = False
    player_name = ""

    while True:
        screen.fill((0, 0, 0))
        draw_text("Hvězdný posel", WIDTH // 2 - 100, 100)
        draw_text("Zadej přezdívku: " + player_name, WIDTH // 2 - 150, 200, YELLOW if input_active else WHITE)
        draw_text("ENTER - Hrát", WIDTH // 2 - 100, 300)
        draw_text("T - Tabulka skóre", WIDTH // 2 - 100, 350)
        draw_text("ESC - Odejít", WIDTH // 2 - 100, 400)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                conn.close()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    conn.close()
                    exit()
                if event.key == pygame.K_t:
                    show_highscores()
                if event.key == pygame.K_RETURN and player_name.strip():
                    return  
                if event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif input_active and len(player_name) < 10 and event.unicode.isalnum():
                    player_name += event.unicode
                elif not input_active:
                    input_active = True

def game_loop():
    """Hlavní smyčka hry."""
    global player_name

    # Hráč (loď)
    player_size = 50
    player_x = WIDTH // 2
    player_y = HEIGHT - 100
    player_speed = 5
    score = 0

    # Asteroidy (menší kruhy)
    asteroid_radius = 15
    asteroids = [[random.randint(0, WIDTH-asteroid_radius), random.randint(-700, -50), random.randint(2, 5)] for _ in range(7)]

    # Planety
    num_planets = 5
    planets = [[random.randint(100, WIDTH-100), random.randint(100, HEIGHT//2), 40] for _ in range(num_planets)]

    # Cílová planeta
    target_planet = random.choice(planets)

    def reset_target():
        """Přepne cíl na novou planetu a zvýší skóre."""
        nonlocal target_planet, score
        score += 1
        target_planet = random.choice(planets)

    def show_game_over():
        """Zobrazí obrazovku Game Over a uloží skóre."""
        screen.fill((0, 0, 0))
        draw_text(f"Konec hry! Skóre: {score}", WIDTH // 2 - 100, HEIGHT // 2)
        pygame.display.update()
        pygame.time.delay(3000)
        save_score(player_name, score)

    # Hlavní smyčka hry
    running = True
    paused = False

    while running:
        screen.fill((0, 0, 0))

        # Zpracování událostí
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                conn.close()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = True

        # Pauza
        while paused:
            screen.fill((0, 0, 0))
            draw_text("Hra pozastavena", WIDTH // 2 - 100, HEIGHT // 2 - 50)
            draw_text("ENTER - Pokračovat", WIDTH // 2 - 100, HEIGHT // 2)
            draw_text("Q - Odejít do menu", WIDTH // 2 - 100, HEIGHT // 2 + 50)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        paused = False
                    if event.key == pygame.K_q:
                        return

        # Ovládání lodi
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_size:
            player_x += player_speed
        if keys[pygame.K_UP] and player_y > 0:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < HEIGHT - player_size:
            player_y += player_speed

        # Pohyb asteroidů
        for asteroid in asteroids:
            asteroid[1] += asteroid[2]
            if asteroid[1] > HEIGHT:
                asteroid[0] = random.randint(0, WIDTH - asteroid_radius)
                asteroid[1] = random.randint(-700, -50)

            # Kolize s asteroidem
            if (player_x < asteroid[0] + asteroid_radius and player_x + player_size > asteroid[0] - asteroid_radius and
                player_y < asteroid[1] + asteroid_radius and player_y + player_size > asteroid[1] - asteroid_radius):
                show_game_over()
                return

        # Kontrola doručení zprávy
        if player_x < target_planet[0] + target_planet[2] and player_x + player_size > target_planet[0] and player_y < target_planet[1] + target_planet[2] and player_y + player_size > target_planet[1]:
            reset_target()

        # Vykreslení hráče
        pygame.draw.rect(screen, BLUE, (player_x, player_y, player_size, player_size))

        # Vykreslení asteroidů jako kruhů
        for asteroid in asteroids:
            pygame.draw.circle(screen, RED, (asteroid[0], asteroid[1]), asteroid_radius)

        # Vykreslení cílové planety
        pygame.draw.circle(screen, GREEN, (target_planet[0], target_planet[1]), target_planet[2])

        # Zobrazení skóre
        draw_text(f"Skóre: {score}", 10, 10, WHITE)

        pygame.display.update()
        pygame.time.delay(30)

while True:
    main_menu()
    game_loop()