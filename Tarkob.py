import pygame as pg
import math
import random
import time
import sys
import os
import main
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow


class Boss:
    def __init__(self, size, hp):
        self.size_x = 200
        self.size_y = 200
        self.pos_x = size[0] // 2 - self.size_x // 2
        self.pos_y = size[1] // 2 - self.size_y // 2
        self.hp = hp

    def render(self, screen):
        pg.draw.rect(screen, pg.Color(79,0,20), (self.pos_x, self.pos_y, self.size_x, self.size_y))

    def health(self, attack, screen):
        self.hp -= attack
        pg.draw.rect(screen, pg.Color(100, 21, 43), (self.pos_x, self.pos_y, self.size_x, self.size_y))

    def getPosForAttack(self):
        return self.pos_x, self.pos_y, self.size_x, self.size_y

    def getHealth(self):
        return self.hp


class Enemy:
    def __init__(self, x, y, to_x, to_y, time_attack, all_sprites):
        self.x = x
        self.y = y
        self.height = 30
        self.weight = 30
        self.speed = 3
        self.hp = 100
        self.time_attack = time_attack
        self.time_to_attack = 0

        self.to_x = to_x
        self.to_y = to_y

        self.enemy_sprite = pg.sprite.Sprite()
        self.enemy_sprite.image = load_image("Enemy.png")
        self.enemy_sprite.rect = self.enemy_sprite.image.get_rect()
        self.enemy_sprite.rect.x, self.enemy_sprite.rect.y = self.x, self.y
        all_sprites.add(self.enemy_sprite)

    def spawn(self, size):
        if self.y < 0:
            self.y += self.speed

        if self.y > size[1]:
            self.y -= self.speed

    def render(self, screen):
        #pg.draw.rect(screen, pg.Color(79,0,20), (self.x, self.y, self.weight, self.height))
        pass

    def getPosForAttack(self):
        return self.x, self.y, self.weight, self.height

    def getHealth(self):
        return self.hp

    def health(self, attack, screen):
        self.hp -= attack

    def move(self, size):
        dx, dy = self.to_x - self.x, self.to_y - self.y
        lenth = math.hypot(dx, dy)
        vector_x = dx / lenth
        vector_y = dy / lenth
        self.x += self.speed * vector_x
        self.y += self.speed * vector_y
        self.time_to_attack += 1
        if self.time_to_attack >= self.time_attack:
            self.time_to_attack = 0

        if self.x - 2 <= self.to_x <= self.x + 2 and self.y - 2 <= self.to_y <= self.y + 2:
            self.to_x = random.randint(0, size[0])
            self.to_y = random.randint(0, size[1])

    def get_attack(self):
        return self.time_to_attack

    def get_sprite(self):
        return self.enemy_sprite


class Bullet:
    def __init__(self, player_pos, screen):
        self.x = player_pos[0]
        self.y = player_pos[1]
        self.vector_x = 0
        self.vector_y = 0
        self.speed = 7
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

    def attack(self, unit):
        unit_pos = unit.getPosForAttack()
        unit_x1 = unit_pos[0]
        unit_x2 = unit_pos[2]
        unit_y1 = unit_pos[1]
        unit_y2 = unit_pos[3]
        if unit_x1 <= self.x <= unit_x1 + unit_x2 and unit_y1 <= self.y <= unit_y1 + unit_y2:
            unit.health(50, self.screen)
            return 1

    def getPos(self):
        return (self.x, self.y)


class Player:
    def __init__(self, weight, height, size):
        self.start_time = 0
        self.ost_time = 1

        self.height = height
        self.weight = weight
        self.pos_x = 5
        self.pos_y = size[1] // 2
        self.speed = 3
        self.ammo = 20
        self.hp = 1000

    def render(self, screen):
        #pg.draw.rect(screen, pg.Color(0, 0, 0), (self.pos_x, self.pos_y, self.weight, self.height))
        pass

    def move(self, key, size, endgame):
        if 1073742049 in key:
            self.speed = 5
        if 1073742049 not in key:
            self.speed = 3

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
        if self.pos_x + self.weight + 2 > size[0] and endgame:
            self.pos_x = size[0] - self.weight + 2
        if self.pos_x + self.weight + 2 > size[0] and not(endgame):
            self.pos_x = size[0] - self.weight
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

    def getHealth(self):
        return self.hp

    def health(self, attack, screen):
        self.hp -= attack

    def getPos(self):
        return (self.pos_x, self.pos_y)

    def getPosForAttack(self):
        return self.pos_x, self.pos_y, self.weight, self.height

    def getAmmo(self):
        return (self.ammo)

    def setAmmo(self, ammo):
        self.ammo += ammo

    def goOut(self, size, screen, level):
        if not(size[0] - size[0] // 65 <= self.pos_x <= size[0] - size[0] // 65 + size[0] // 65 and size[1] // 4 <= self.pos_y <= size[1] // 4 + size[1] // 2):
            self.start_time = time.time()

        if size[0] - size[0] // 65 <= self.pos_x <= size[0] - size[0] // 65 + size[0] // 65 and size[1] // 4 <= self.pos_y <= size[1] // 4 + size[1] // 2:
            f = pg.font.Font(None, 100)
            self.ost_time = round(10 - (time.time() - self.start_time), 1)
            if self.ost_time < 0.1:
                self.ost_time = 0
            text = f.render(f'{self.ost_time} Выход с локации', True, (0, 200, 0))
            screen.blit(text, (size[0] // 3, size[1] // 2))
            if self.ost_time <= 0:
                text = f.render(f'{self.ost_time} Выход с локации', True, (0, 200, 0))
                main(level + 1)


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
        self.x = size[0] - size[0] // 65
        self.y = size[1] // 4
        self.size_x = size[0] - self.x
        self.size_y = size[1] // 2

    def render(self, screen):
        pg.draw.rect(screen, pg.Color(38, 171, 29), (self.x, self.y, self.size_x, self.size_y))


class UI:
    def __init__(self, player, boss):
        self.player_hp = player.getHealth()
        self.boss_hp = boss.getHealth()

    def render(self, player, boss, screen, size):
        self.player_hp = player.getHealth()
        self.player_ammo = player.getAmmo()
        if boss == 0:
            self.boss_hp = 0
        else:
            self.boss_hp = boss.getHealth()

        f = pg.font.Font(None, 30)
        text = f.render(f'Осталось здоровья: {self.player_hp}', True, (0, 200, 0))
        screen.blit(text, (size[0] // 100, size[1] // 10))
        text = f.render(f'Осталось патрон: {self.player_ammo}', True, (0, 200, 0))
        screen.blit(text, (size[0] // 100, size[1] // 10 + size[1] // 15))

        text = f.render(f'Осталось здоровья босса: {self.boss_hp}', True, (0, 200, 0))
        screen.blit(text, (size[0] - size[0] // 5, size[1] // 10))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    return image


def main(level):
    pg.init()
    size = (1920, 1080)
    screen = pg.display.set_mode(size)
    pg.display.set_caption("Эщкерп пром Карков")
    field = Field(size)
    level = level

    all_sprites = pg.sprite.Group()
    player_sprite = pg.sprite.Sprite()
    player_sprite.image = load_image("Player.png")
    player_sprite.rect = player_sprite.image.get_rect()
    all_sprites.add(player_sprite)

    boss_sprite = pg.sprite.Sprite()
    boss_sprite.image = load_image("Boss.png")
    boss_sprite.rect = boss_sprite.image.get_rect()
    all_sprites.add(boss_sprite)

    player = Player(30, 30, size)
    players = [player]
    boss = Boss(size, 1000 + 100 * (level - 1))
    bosses = [boss]
    enemies = []

    down = False
    key = []
    bullets = []
    enemy_bullets = []
    running = True
    ui = UI(player, boss)

    while running:
        if player.getHealth() <= 0:
            players = []
        if len(players) > 0:
            player_sprite.rect.x, player_sprite.rect.y = player.getPos()[0], player.getPos()[1]

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False

                if event.type == pg.KEYDOWN:
                    key.append(event.key)
                    if event.key == 112:
                        sys.exit()

                if event.type == pg.KEYUP:
                    key.remove(event.key)

                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1 and player.getAmmo() > 0:
                        bullet = Bullet(player.getPos(), screen)
                        bullet.spawn(event.pos[0], event.pos[1])
                        bullets.append(bullet)
                        player.setAmmo(-1)

            field.render(screen)
            player.render(screen)

            if len(enemies) < level and len(bosses) != 0:
                enemy = Enemy(random.randint(0, size[0]), random.choice([-2, size[1] + 2]), random.randint(0, size[0]),
                              random.randint(0, size[1]), random.randint(20, 50), all_sprites)
                enemies.append(enemy)

            for enemy in enemies:
                enemy_sprite = enemy.get_sprite()
                enemy_sprite.rect.x, enemy_sprite.rect.y = enemy.getPosForAttack()[0], enemy.getPosForAttack()[1]
                if enemy.getPosForAttack()[1] <= 0:
                    enemy.spawn(size)
                else:
                    enemy.move(size)
                    if enemy.get_attack() == 0:
                        enemy_bullet = Bullet((enemy.getPosForAttack()[0], enemy.getPosForAttack()[1]), screen)
                        enemy_bullet.spawn(player.getPosForAttack()[0], player.getPosForAttack()[1])
                        enemy_bullets.append(enemy_bullet)
                enemy.render(screen)

                all_sprites.update()
                if enemy.getHealth() <= 0:
                    enemy_sprite.rect.x, enemy_sprite.rect.y = -1000, -1000
                    enemies.remove(enemy)

            for boss in bosses:
                    boss_sprite.rect.x, boss_sprite.rect.y = boss.getPosForAttack()[0], boss.getPosForAttack()[1]
                    boss.render(screen)
                    if boss.getHealth() <= 0:
                        bosses.remove(boss)
                        boss_sprite.rect.x, boss_sprite.rect.y = -1000, -1000
                    else:
                        enemy_bullet = Bullet((boss.getPosForAttack()[0] + boss.getPosForAttack()[2] // 2,
                                               boss.getPosForAttack()[1] + boss.getPosForAttack()[3] // 2), screen)
                        enemy_bullet.spawn(player.getPosForAttack()[0], player.getPosForAttack()[1])
                        enemy_bullets.append(enemy_bullet)
            if len(bosses) == 0:
                endgame = EndGame(size)
                endgame.render(screen)
                player.goOut(size, screen, level)
                MyWidget()

            if key:
                if len(bosses) == 0:
                    endgame = True
                else:
                    endgame = False
                player.move(key, size, endgame)
                if key[0] == 101:
                    player.openCase(field.sendCases())

            for enemy_bullet in enemy_bullets:
                enemy_bullet.render(screen)
                if enemy_bullet.attack(player):
                    enemy_bullets.remove(enemy_bullet)

            for bullet in bullets:
                bullet.render(screen)
                if bullet.attack(boss) if len(bosses) > 0 else 0:
                    bullets.remove(bullet)

                for enemy in enemies:
                    if bullet.attack(enemy) if len(enemies) > 0 else 0:
                        try:
                            bullets.remove(bullet)
                        except ValueError:
                            pass

                xy = bullet.getPos()
                x = xy[0]
                y = xy[1]
                if x < 0 or x > size[0] or y < 0 or y > size[1]:
                    if bullet in bullets:
                        bullets.remove(bullet)
            if len(bosses) != 0:
                ui.render(player, boss, screen, size)
            else:
                ui.render(player, 0, screen, size)

            if level == 1:
                f = pg.font.Font(None, 15)
                text = f.render('WASD - управление, SHIFT - бег, E - подбор патронов, P - Выход из игры',
                                True, (0, 200, 0))
                screen.blit(text, (text.get_rect(center=(size[0] // 2, size[1] - size[1] // 10))))

            all_sprites.draw(screen)

        if len(players) == 0:
            f = pg.font.Font(None, 100)
            text = f.render(f'ТЫ ПРОИГРАЛ уровень: {level}', True, (200, 0, 0))
            screen.blit(text, (text.get_rect(center=(size[0] // 2, size[1] // 2))))
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        main(1)

        pg.display.flip()


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Main.ui', self)
        self.setWindowTitle('Эщкерп пром Карков')
        self.pixmap = QPixmap('EFT.jpg')
        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)

        self.pushButton.clicked.connect(self.run)
        self.label.setGeometry(30, 30, 770, 461)
        self.label.resize(730, 430)

    def run(self):
        main(int(self.lineEdit.text()))
        sys.exit()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())