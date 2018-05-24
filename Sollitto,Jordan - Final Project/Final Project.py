import pygame, sys, random, time, os, math

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SAND = (238, 214, 175)
BLUE = (0, 0, 255)
LIGHTBLUE = (173, 216, 230)
GREEN = (25,239,25)

TIMER = 0

WIN_H = 700


class Camera:
    def __init__(self, container):
        self.y_offset = 0
        self.container = container

    def update(self, hook):
        self.y_offset = -hook.rect.y + WIN_H / 2

        if self.y_offset > 0:
            self.y_offset = 0

        if self.y_offset < -(self.container.height - WIN_H):
            self.y_offset = -(self.container.height - WIN_H)

    def apply(self, obj):
        return pygame.Rect(obj.rect.x, obj.rect.y + self.y_offset, obj.rect.width, obj.rect.height)


class Background(pygame.sprite.Sprite):
    def __init__(self, x, y, col):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((32,32))
        self.image.convert()
        self.set_image(col)
        self.rect = pygame.Rect(x, y, 32, 32)

    def set_image(self, col):
        if col == "P":
            return self.image.fill(LIGHTBLUE)
        if col == "C":
            return self.image.fill(WHITE)
        if col == "S":
            return self.image.fill(SAND)
        if col == " ":
            return self.image.fill(BLUE)
        if col == "G":
            return self.image.fill(GREEN)


class Boat(pygame.sprite.Sprite):
    def __init__(self, container):
        pygame.sprite.Sprite.__init__(self)
        self.container = container
        self.speed = 4.25
        self.image = pygame.image.load("Images/boat.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (250, 250))
        self.rect = self.image.get_rect()
        self.rect.centerx = container.width/2
        self.rect.centery = container.width/2
        self.hook = Hook(self.rect, container)

    def update(self, container, fish_group, netting):

        key = pygame.key.get_pressed()

        if key[pygame.K_a]:
            self.rect.x -= self.speed
        elif key[pygame.K_d]:
            self.rect.x += self.speed
        if key[pygame.K_s]:
            self.hook.update(self.rect, True, fish_group, netting)
        else:
            self.hook.update(self.rect, False, fish_group, netting)

        if self.rect.left <= self.rect.width/10:
            self.rect.left = self.rect.width/10

        elif self.rect.left + self.rect.width/10 >= container.width:
            self.rect.left = container.width - self.rect.width/10


class Hook(pygame.sprite.Sprite):
    def __init__(self, ship_rect, container):
        pygame.sprite.Sprite.__init__(self)
        self.container = container
        self.speed = 4.5
        self.image = pygame.image.load("Images/hook.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.centerx = ship_rect.left
        self.rect.centery = ship_rect.bottom
        self.falling = False
        self.reeling = False
        self.top = self.rect.y

    def update(self, ship_rect, down, fish_group, netting):
        self.rect.centerx = ship_rect.left
        print self.rect.y
        if down and self.falling == False:
            self.falling = True
        elif not down and self.falling == True:
            self.falling = False
        if self.falling:
            self.rect.y += self.speed
        elif not self.falling and self.rect.y >= self.top:
            self.rect.y -= self.speed

        collide = pygame.sprite.spritecollide(self, fish_group, False)
        # Use collide algorithm
        for fish in collide:
            if not fish.hooked:
                fish.image = pygame.transform.rotate(fish.image, -90)
                fish.hooked = True

            if fish.hooked:
                fish.rect.y = self.rect.y
                fish.rect.centerx = self.rect.centerx

            if fish.rect.y <= 387:
                netting.play(1)
                fish.kill()

        self.rect.clamp_ip(self.container)


class Fish(pygame.sprite.Sprite):
    def __init__(self, container, img, depth):
        pygame.sprite.Sprite.__init__(self)
        self.container = container
        self.speed = 2
        self.image = pygame.image.load(img).convert_alpha()
        self.image = pygame.transform.scale(self.image, (150, 150))
        self.rect = self.image.get_rect()
        self.rect.x = (random.randrange(0, (container.width - 150)))
        self.rect.y = depth
        self.hooked = False

    def update(self):
        self.rect.x += self.speed
        if self.rect.left <= 0:
            self.speed *= -1

        elif self.rect.right >= self.container.width:
            self.speed *= -1


class Text:
    def __init__(self, size, text, xpos, ypos):
        self.font = pygame.font.SysFont("Britannic Bold", size)
        self.image = self.font.render(text, 1, BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = xpos
        self.rect.centery = ypos


class Game:
    def __init__(self, width):
        self.screen = pygame.display.set_mode((width, WIN_H))
        self.fps = 60
        self.play = True
        self.intro = True
        self.clock = pygame.time.Clock()
        self.title = Text(115, str("8-Bit Fishing"), width / 2, WIN_H/4)
        self.subtitle = Text(75, str("--- Click Here ---"), width / 2, WIN_H/2)
        self.leftscore = Text(75, str(0), width/7, 30)
        self.rightscore = Text(75, str(0), width/1.5, 30)
        self.beg_time = pygame.time.get_ticks()
        self.outro = True
        self.restarttitle = Text(150, str("Great Match!"), width / 2, WIN_H / 4)
        self.restartsubtitle = Text(75, str("--- Click To Restart ---"), width / 2, WIN_H / 2)

    def blink(self):
        cur_time = pygame.time.get_ticks()

        if ((cur_time - self.beg_time) % 1000) < 500:
            self.screen.blit(self.subtitle.image, self.subtitle.rect)

    def endblink(self):
        cur_time = pygame.time.get_ticks()

        if ((cur_time - self.beg_time) % 1000) < 500:
            self.screen.blit(self.restartsubtitle.image, self.restartsubtitle.rect)

    def restart(self):
        self.play = True
        self.leftscore.image = self.leftscore.font.render(str(0), 1, BLACK)
        self.rightscore.image = self.rightscore.font.render(str(0), 1, BLACK)
        self.screen.blit(self.leftscore.image, self.leftscore.rect)
        self.screen.blit(self.rightscore.image, self.rightscore.rect)

    def winner(self):
            self.play = False
            self.outro = True


def main():
    global WIN_H, BLACK, TIMER

    pygame.init()
    pygame.display.set_caption(" 8-Bit Fishing")

    level = [
   "PPPPPPPPPPPPPPPPPP",
   "PPPCCCPPPPPPPPPPPP",
   "PPPPPPPPPPPPPCCCPP",
   "PPPPPPPPPPPPPPPPPP",
   "PPPPPPPPPPPPPPPPPP",
   "PPCCCCCPPPPPPPPPPP",
   "PPPPPPPPPPPPPPPPPP",
   "PPPPPPPPPPPPCCCCPP",
   "PPPPPPPPPPPPPPPPPP",
   "PPPPPPPPPPPPPPPPPP",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "                  ",
   "SSSSSSSSSSSSSSSSSS",
   "SSSSSSSSSSSSSSSSSS",]

    game = Game(len(level[0]) * 32)

    platform_group = pygame.sprite.Group()
    container = pygame.Rect(0, 0, len(level[0]) * 32, len(level) * 32)

    #5580 (length of fishable map)
    #512 (where fish start to spawn)

    boat = Boat(container)
    camera = Camera(container)
    fish_group = pygame.sprite.Group()

    for i in range(1, 21):
        sk = Fish(container, "Images/Skipjack(Transparent).png", random.randrange(512, 3750))
        fish_group.add(sk)

    for i in range(1, 16):
        bg = Fish(container, "Images/Bigeye(Transparent).png", random.randrange(512, 3750))
        fish_group.add(bg)

    for i in range(1, 11):
        yf = Fish(container, "Images/Yellowfin(Transparent).png", random.randrange(2512, 4580))
        fish_group.add(yf)

    for i in range(1, 6):
        bf = Fish(container, "Images/Bluefin(Transparent).png", random.randrange(3000, 5100))
        fish_group.add(bf)

    bluefin_variant = Fish(container, "Images/Bluefin-Variant(1).png", random.randrange(4900, 5251))

    yellowfin_variant = Fish(container, "Images/Yellowfin-Variant(2).png", random.randrange(4900, 5251))

    skipjack_variant = Fish(container, "Images/Skipjack-Variant(1).png", random.randrange(4900, 5251))

    bigeye_variant = Fish(container, "Images/Bigeye-Variant(2).png", random.randrange(4900, 5251))

    fish_group.add(bluefin_variant, yellowfin_variant, skipjack_variant, bigeye_variant )

    bubbles = pygame.mixer.Sound("Sounds/Bubbles.ogg")
    netting = pygame.mixer.Sound("Sounds/Netting.ogg")
    reeling = pygame.mixer.Sound("Sounds/Reeling.ogg")
    Music_Intro = pygame.mixer.Sound("Sounds/Music_Intro.ogg")
    Music_Intro.play()

    x = y = 0
    for row in level:
        for col in row:
            p = Background(x, y, col)
            platform_group.add(p)
            x += 32
        y += 32
        x = 0

    while True:
        while game.intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN or pygame.key.get_pressed()[pygame.K_RETURN] != 0:
                    game.intro = False
                    Music_Intro.stop()
            game.screen.fill(BLUE)
            game.screen.blit(game.title.image, game.title.rect)
            game.blink()
            game.clock.tick(game.fps)
            pygame.display.flip()

        while game.play:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            boat.update(container, fish_group, netting)
            camera.update(boat.hook)
            fish_group.update()

            for p in platform_group:
                game.screen.blit(p.image, camera.apply(p))

            game.screen.blit(boat.image, camera.apply(boat))
            game.screen.blit(boat.hook.image, camera.apply(boat.hook))
            for fish in fish_group:
                game.screen.blit(fish.image, camera.apply(fish))

            game.clock.tick(game.fps)
            pygame.display.flip()

        TIMER += 1


if __name__ == "__main__":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    main()