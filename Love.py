import pygame
import random
import time
import math

# --- Konstanta Proposi Potret (9:16) ---
WIDTH = 450
HEIGHT = 800
FPS = 60

# --- Warna ---
DEEP_RED = (180, 20, 40)
SOFT_PINK = (255, 182, 193)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
BLACK = (5, 5, 10)
AURORA = (30, 10, 40) # Warna kabut agak ungu untuk nuansa romantis

# --- Inisialisasi ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("9:16 Love Portrait")
clock = pygame.time.Clock()

# --- Font (Disesuaikan untuk layar sempit) ---
def get_font(size, bold=False):
    try: return pygame.font.SysFont('georgia', size, bold=bold)
    except: return pygame.font.Font(None, size)

font_poem = get_font(18)          # Ukuran lebih kecil untuk potret
font_heart = get_font(32, bold=True)

# --- Puisi ---
POEM_TEXT = """
Aku ingin mencintaimu
dengan sederhana:
dengan kata yang tak
sempat diucapkan
kayu kepada api yang
menjadikannya abu.
Aku ingin mencintaimu
dengan sederhana:
dengan isyarat yang tak
sempat disampaikan
awan kepada hujan yang
menjadikannya tiada
"""

# --- Kelas Kata (Efek Muncul & Hilang) ---
class WordEffect:
    def __init__(self, text, x, y, delay):
        self.text = text
        self.x = x
        self.y = y
        self.alpha = 0
        self.phase = "FADE_IN"
        self.start_time = time.time() + delay
        self.display_time = 0
        self.fade_speed = 5

    def update(self):
        now = time.time()
        if now < self.start_time: return
        if self.phase == "FADE_IN":
            self.alpha += self.fade_speed
            if self.alpha >= 255:
                self.alpha = 255
                self.phase = "WAIT"
                self.display_time = now
        elif self.phase == "WAIT":
            if now - self.display_time > 2.0:
                self.phase = "FADE_OUT"
        elif self.phase == "FADE_OUT":
            self.alpha -= self.fade_speed
            if self.alpha <= 0: self.alpha = 0
        return self.alpha <= 0 and self.phase == "FADE_OUT"

    def draw(self, surface):
        if time.time() < self.start_time or self.alpha <= 0: return
        text_surf = font_poem.render(self.text, True, WHITE)
        alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.fill((255, 255, 255, int(self.alpha)))
        text_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        rect = text_surf.get_rect(center=(self.x, self.y))
        surface.blit(text_surf, rect)

# --- Kelas Partikel ---
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color, size_range=(1, 3), velocity=None):
        super().__init__()
        size = random.randint(size_range[0], size_range[1])
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_x, self.speed_y = velocity if velocity else (random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4))
        self.life = 255
        self.decay = random.uniform(2.0, 4.0)

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        self.life -= self.decay
        if self.life <= 0: self.kill()
        else: self.image.set_alpha(int(self.life))

# --- Logika Tata Letak ---
def create_poem_objects():
    objects = []
    lines = POEM_TEXT.strip().split('\n')
    cumulative_delay = 0
    # Puisi diletakkan di area bawah (1/3 layar bawah)
    start_y = HEIGHT * 0.65 
    
    for i, line in enumerate(lines):
        words = line.split()
        line_y = start_y + (i * 25)
        total_width = sum(font_poem.size(w + " ")[0] for w in words)
        current_x = (WIDTH - total_width) // 2
        for word in words:
            word_w = font_poem.size(word + " ")[0]
            objects.append(WordEffect(word, current_x + word_w//2, line_y, cumulative_delay))
            current_x += word_w
            cumulative_delay += 0.25
        cumulative_delay += 0.5
    return objects

def get_heart_point(t, scale=8): # Skala diperkecil agar pas di lebar potret
    x = 16 * math.sin(t)**3
    y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
    # Posisi hati di 1/3 layar atas
    return (int(WIDTH/2 + x * scale), int(HEIGHT/3 - y * scale))

# --- Inisialisasi Objek ---
all_particles = pygame.sprite.Group()
poem_objects = create_poem_objects()
heart_t = 0
running = True

while running:
    screen.fill(BLACK)
    now_time = time.time()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    # 1. Background Glow
    mist_surf = pygame.Surface((300, 300), pygame.SRCALPHA)
    pygame.draw.circle(mist_surf, (AURORA[0], AURORA[1], AURORA[2], 5), (150, 150), 150)
    screen.blit(mist_surf, (WIDTH//2 - 150, HEIGHT//3 - 150))

    # 2. Partikel Hati
    for _ in range(4):
        heart_t += 0.05
        pos = get_heart_point(heart_t, scale=int(WIDTH/55))
        color = random.choice([DEEP_RED, SOFT_PINK, GOLD])
        all_particles.add(Particle(pos[0], pos[1], color, (2, 4)))

    # 3. Teks I LOVE U Berkedip (Tengah Hati)
    pulse = (math.sin(now_time * 3) + 1) / 2
    alpha = int(120 + (pulse * 135))
    
    txt_love = font_heart.render("I LOVE U", True, SOFT_PINK)
    txt_love.set_alpha(alpha)
    love_rect = txt_love.get_rect(center=(WIDTH//2, HEIGHT/3))
    
    # Shadow/Glow effect
    glow = font_heart.render("I LOVE U", True, DEEP_RED)
    glow.set_alpha(int(alpha * 0.4))
    screen.blit(glow, (love_rect.x+2, love_rect.y+2))
    screen.blit(txt_love, love_rect)

    # 4. Puisi (Per kata muncul/hilang)
    active = False
    for obj in poem_objects:
        obj.update()
        obj.draw(screen)
        if obj.phase != "FADE_OUT" or obj.alpha > 0:
            active = True
    
    if not active:
        poem_objects = create_poem_objects()

    # 5. Partikel Update
    all_particles.update()
    all_particles.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
