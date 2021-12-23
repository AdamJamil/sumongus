import pygame
import math
import time
from pygame.locals import (
    K_w,
    K_a,
    K_s,
    K_d,
    # K_ESCAPE,
    KEYDOWN,
    KEYUP,
    # QUIT,
)

FPS = 60


def rot_center(image, angle):
    if hasattr(rot_center, "sumongus"):
        return rot_center.sumongus[int(angle / (2 * math.pi) * 1000)]
    else:
        rot_center.sumongus = []
        for i in range(1000):
            rot_sprite = pygame.transform.rotate(image, i * (2 * math.pi / 1000) * 180 / math.pi)
            rot_sprite.get_rect().center = image.get_rect().center
            rot_center.sumongus += [rot_sprite]
        return rot_center(image, angle)


def circ_line_seg_collision(C, r, E, L):
    d = L[0] - E[0], L[1] - E[1]
    f = E[0] - C[0], E[1] - C[1]
    a = d[0] * d[0] + d[1] * d[1]
    b = 2 * (f[0] * d[0] + f[1] * d[1])
    c = f[0] * f[0] + f[1] * f[1] - r * r
    disc = b * b - 4 * a * c
    if disc < 0:
        return False
    disc = math.sqrt(disc)
    t1 = (-b - disc) / (2 * a)
    t2 = (-b + disc) / (2 * a)
    return 0 <= t1 <= 1 or 0 <= t2 <= 1


def collide(C, r, E, L, pos, b):
    return circ_line_seg_collision(C, r, E, L) and pos + r - 10 < b


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode([1000, 500])

    running = True
    platforms = (
        pygame.Rect(30, 450, 940, 20),  # bottom
        pygame.Rect(30, 30, 940, 20),  # ceiling
        pygame.Rect(30, 30, 20, 440),  # left wall
        pygame.Rect(950, 30, 20, 440),  # right wall
        pygame.Rect(300, 420, 400, 30),  # middle raise
        pygame.Rect(180, 280, 180, 30),  # left float
        pygame.Rect(1000 - 360, 280, 180, 30),  # right float
        pygame.Rect(310, 130, 380, 30),  # middle float
    )

    sumongus = pygame.image.load('amogs.png')


    class Player:
        def __init__(self):
            self.r = math.dist(sumongus.get_rect().topleft, sumongus.get_rect().bottomright) / 2
            self.x, self.y = 80, 450 - self.r
            self.vx, self.vy = 0, 0
            self.left, self.right = -1, -1
            self.theta = 0
            self.w = 0
            self.jump = True
            self.on_platform = True
            self.on_wall = False


    players = Player(),
    tick = 0
    last_time = None
    last_mouse_ang = None
    while running:
        if last_time:
            time.sleep(max(0., 1 / FPS - (time.time() - last_time)))
        last_time = time.time()
        tick += 1
        for event in pygame.event.get():
            running = event.type != pygame.QUIT
            for p in players:
                if event.type == KEYDOWN:
                    if event.key == K_w:  # jump
                        if p.on_platform:
                            p.vy += -2.5
                        elif p.on_wall:
                            p.vy += -4.5
                            p.vx += 4
                    elif event.key == K_a:  # left
                        p.left = tick
                    elif event.key == K_d:  # right
                        p.right = tick
                    elif event.key == K_s and p.on_platform:
                        p.vx = 0
                        p.w = 0
                elif event.type == KEYUP:
                    if event.key == K_a:  # left release
                        p.left = -1
                    elif event.key == K_d:  # right release
                        p.right = -1
        for p in players:
            curr_mouse_ang = math.atan2(pygame.mouse.get_pos()[0] - p.x, pygame.mouse.get_pos()[1] - p.y)
            if last_mouse_ang:
                p.w += 0.01 * ((curr_mouse_ang - last_mouse_ang + math.pi) % (2 * math.pi) - math.pi)
            last_mouse_ang = curr_mouse_ang
            if p.left != -1 and p.right != -1:
                if p.right > p.left:
                    p.left = -1
                else:
                    p.right = -1
            if p.left != -1:
                if p.on_platform and p.vx >= -0.1:
                    p.vx = -2
                else:
                    p.vx = max(-4, -4 / 150 + p.vx) if p.vx > -4 else p.vx
            elif p.right != -1:
                if p.on_platform and p.vx <= 0.1:
                    p.vx = 2
                else:
                    p.vx = min(4, 4 / 150 + p.vx) if p.vx < 4 else p.vx
            else:
                p.vx = 0.99 * p.vx

        for p in players:
            TIME_GRANULARITY = 20
            for i in range(TIME_GRANULARITY):
                p.theta += p.w / TIME_GRANULARITY
                p.theta %= 2 * math.pi
                C = p.x, p.y
                top = any(collide(C, p.r, pl.topleft, pl.topright, C[1], pl.top) for pl in platforms)
                bot = any(collide(C, p.r, pl.bottomleft, pl.bottomright, -C[1], -pl.bottom) for pl in platforms)
                left = any(collide(C, p.r, pl.topleft, pl.bottomleft, C[0], pl.left) for pl in platforms)
                right = any(collide(C, p.r, pl.topright, pl.bottomright, -C[0], -pl.right) for pl in platforms)
                if top or bot:
                    p.vy = p.vy if (p.vy < 0) == top else -p.vy if abs(p.vy) > 2 and bot else 0
                    p.vx += 10 * (1 - math.pow(0.95, 1 / TIME_GRANULARITY)) * p.w * (1 if bot else -1)
                    p.w *= math.pow(0.95, 1 / TIME_GRANULARITY)
                if left or right:
                    p.vx = p.vx if (p.vx < 0) == left else -p.vx if abs(p.vx) > 2 and not top else 0
                    p.vy += 13 * (1 - math.pow(0.8, 1 / TIME_GRANULARITY)) * p.w * (1 if left else -1)
                    p.w *= math.pow(0.8, 1 / TIME_GRANULARITY)
                p.on_platform = top
                p.on_wall = left or right
                p.y += p.vy / TIME_GRANULARITY
                p.x += p.vx / TIME_GRANULARITY

                if not p.on_platform:
                    p.vy += 1 / 20 / TIME_GRANULARITY

        screen.fill((0, 0, 0))
        for p in platforms:
            pygame.draw.rect(screen, (255, 255, 255), p)
        for p in players:
            rot_img = rot_center(sumongus, p.theta)
            screen.blit(
                rot_img, (
                    p.x - rot_img.get_rect().width / 2,
                    p.y - rot_img.get_rect().height / 2
                )
            )

        pygame.display.flip()

    pygame.quit()
