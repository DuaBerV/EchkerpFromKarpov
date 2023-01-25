import pygame as pg
import math
import random
import time
import sys


class Boss:
    def __init__(self, size):
        self.size_x = 200
        self.size_y = 200
        self.pos_x = size[0] // 2 - self.size_x // 2
        self.pos_y = size[1] // 2 - self.size_y // 2
        self.hp = 1000

    def render(self, screen):
        pg.draw.rect(screen, pg.Color(79,0,20), (self.pos_x, self.pos_y, self.size_x, self.size_y))

    def health(self, attack, screen):
        self.hp -= attack
        pg.draw.rect(screen, pg.Color(100, 21, 43), (self.pos_x, self.pos_y, self.size_x, self.size_y))

    def getPos(self):
        return self.pos_x, self.pos_y, self.size_x, self.size_y

    def getHealth(self):
        return self.hp


class Bullet:
    def __init__(self, player_pos, screen):
        self.x = player_pos[0]
        self.y = player_pos[1]
        self.vector_x = 0
        self.vector_y = 0
        self.speed = 5
        self.screen = screen

    def spawn(self, x, y):
        dx, dy = x - self.x, y - self.y
        lenth = math.hypot(dx, dy)
        self.vector_x = dx / lenth
        self.vector_y = dy / lenth

    def render(self, screen):
        self.x += self.speed * self.vector_x
        self.y += self.speed * self.vector_y
        pg.draw.circle(screen, pg.Color(255, 0, 0), (self.x, self.y), 3)

    def attack(self, boss):
        boss_pos = boss.getPos()
        boss_x1 = boss_pos[0]
        boss_x2 = boss_pos[2]
        boss_y1 = boss_pos[1]
        boss_y2 = boss_pos[3]
        if boss_x1 <= self.x <= boss_x1 + boss_x2 and boss_y1 <= self.y <= boss_y1 + boss_y2:
            boss.health(50, self.screen)
            return 1

    def getPos(self):
        return (self.x, self.y)


class Player:
    def __init__(self, weight, height):
        self.start_time = 0
        self.ost_time = 1

        self.height = height
        self.weight = weight
        self.pos_x = 250
        self.pos_y = 250
        self.speed = 3
        self.ammo = 20

    def render(self, screen):
        pg.draw.rect(screen, pg.Color(0, 0, 0), (self.pos_x, self.pos_y, self.weight, self.height))

    def move(self, key, size):
        for movement in key:
            'S'
            if movement == 119:
                self.pos_y -= self.speed
            'W'
            if movement == 115:
                self.pos_y += self.speed
            'A'
            if movement == 97:
                self.pos_x -= self.speed
            'D'
            if movement == 100:
                self.pos_x += self.speed
        if self.pos_x < 0:
            self.pos_x = 0
        if self.pos_y < 0:
            self.pos_y = 0
        if self.pos_x + self.weight + 2 > size[0]:
            self.pos_x = size[0] - self.weight + 2
        if self.pos_y + self.height > size[1]:
            self.pos_y = size[1] - self.height

    def openCase(self, case):
        if len(case) > 0:
            for xy in case:
                x = xy[0]
                y = xy[1]
                if (self.pos_x - 30 <= x and self.pos_x + 60 >= x) and (self.pos_y - 30 <= y and self.pos_y + 30 >= y):
                    self.setAmmo(20)
                    case.remove(xy)

    def getPos(self):
        return (self.pos_x, self.pos_y)

    def getAmmo(self):
        return (self.ammo)

    def setAmmo(self, ammo):
        self.ammo += ammo

    def goOut(self, size, screen):
        if size[0] - size[0] // 100 - 10 <= self.pos_x <= size[0] - size[0] // 100 and size[1] // 4 - 10 <= self.pos_y <= size[1] // 4 + size[1] // 2 + 10:
            self.start_time = time.time()

        if size[0] - size[0] // 100 <= self.pos_x <= size[0] - size[0] // 100 + size[0] // 100 and size[1] // 4 <= self.pos_y <= size[1] // 4 + size[1] // 2:
            f = pg.font.Font(None, 100)
            self.ost_time = round(20 - (time.time() - self.start_time), 1)
            if self.ost_time < 0.1:
                self.ost_time = 0
            text = f.render(f'{self.ost_time} Выход с локации', True, (0, 200, 0))
            screen.blit(text, (size[0] // 3, size[1] // 2))
            if self.ost_time <= 0:
                text = f.render(f'{self.ost_time} Выход с локации', True, (0, 200, 0))
                time.sleep()
                sys.exit()


class Field:
    def __init__(self, size):
        self.height = size[1]
        self.weight = size[0]
        self.size = size
        self.plates = [(random.randint(0, size[0]), random.randint(0, size[1]), random.randint(1, 100), random.randint(1, 100)) for _ in range(100)]
        self.cases = [
            (random.randint(0, size[0]), random.randint(0, size[1]), 30, 30) for _ in range(random.randint(5, 15))]

    def render(self, screen):
        pg.draw.rect(screen, pg.Color(90, 90, 90), (0, 0, self.weight, self.height))
        for plate in self.plates:
            pg.draw.rect(screen, pg.Color(100, 100, 100), plate)
        for case in self.cases:
            pg.draw.rect(screen, pg.Color(121,85,61), case)

        if len(self.cases) == 0:
            self.cases.append((random.randint(0, self.size[0]), random.randint(0, self.size[1]), 30, 30))

    def sendCases(self):
        return self.cases


class EndGame:
    def __init__(self, size):
        self.x = size[0] - size[0] // 100
        self.y = size[1] // 4
        self.size_x = size[0] - self.x
        self.size_y = size[1] // 2

    def render(self, screen):
        pg.draw.rect(screen, pg.Color(38, 171, 29), (self.x, self.y, self.size_x, self.size_y))

def main():
    pg.init()
    size = (1920, 1080)
    screen = pg.display.set_mode(size)
    pg.display.set_caption("Эщкерп пром Карков")
    field = Field(size)

    player = Player(20, 50)
    boss = Boss(size)
    bosses = [boss]

    down = False
    key = []
    bullets = []
    running = True
    while running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.KEYDOWN:
                key.append(event.key)

            if event.type == pg.KEYUP:
                key.append(event.key)
                key = []

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1 and player.getAmmo() > 0:
                    bullet = Bullet(player.getPos(), screen)
                    bullet.spawn(event.pos[0], event.pos[1])
                    bullets.append(bullet)
                    player.setAmmo(-1)

        field.render(screen)
        player.render(screen)

        for boss in bosses:
                boss.render(screen)
                if boss.getHealth() <= 0:
                    bosses.remove(boss)
        if len(bosses) == 0:
            endgame = EndGame(size)
            endgame.render(screen)
            player.goOut(size, screen)

        if key:
            player.move(key, size)
            if key[0] == 101:
                player.openCase(field.sendCases())

        for bullet in bullets:
            bullet.render(screen)
            if bullet.attack(boss) if len(bosses) > 0 else 0:
                bullets.remove(bullet)

            xy = bullet.getPos()
            x = xy[0]
            y = xy[1]
            if x < 0 or x > size[0] or y < 0 or y > size[1]:
                bullets.remove(bullet)

        pg.display.flip()


if __name__ == '__main__':
    main()
