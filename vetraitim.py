import random
import time
from math import sin, cos, pi, log
from tkinter import Tk, Canvas

CANVAS_WIDTH = 640
CANVAS_HEIGHT = 640
CANVAS_CENTER_X = CANVAS_WIDTH // 2
CANVAS_CENTER_Y = CANVAS_HEIGHT // 2
IMAGE_ENLARGE = 11

HEART_COLORS = ["#ff99aa", "#ff4d6d", "#ff1744"]


def heart_function(t, shrink_ratio: float = IMAGE_ENLARGE):
    x = 16 * (sin(t) ** 3)
    y = -(13 * cos(t) - 5 * cos(2 * t) - 2 * cos(3 * t) - cos(4 * t))

    x *= shrink_ratio
    y *= shrink_ratio
    x += CANVAS_CENTER_X
    y += CANVAS_CENTER_Y
    return int(x), int(y)


def scatter_inside(x, y, beta=0.15):
    ratio_x = -beta * log(random.random())
    ratio_y = -beta * log(random.random())

    dx = ratio_x * (x - CANVAS_CENTER_X)
    dy = ratio_y * (y - CANVAS_CENTER_Y)
    return x - dx, y - dy


def curve(p):
    return sin(p)


class Heart:
    def __init__(self, generate_frame=40):
        self._points = set()
        self._edge_diffusion_points = set()
        self._center_diffusion_points = set()
        self.all_points = {}
 
        self.build(1200)   

        self.generate_frame = generate_frame
        for frame in range(generate_frame):
            self.calc(frame)

    def build(self, number):
       
        for _ in range(number):
            t = random.uniform(0, 2 * pi)
            x, y = heart_function(t)
            self._points.add((x, y))
 
        for x, y in list(self._points):
            for _ in range(3): 
                x1, y1 = scatter_inside(x, y, 0.25)
                self._edge_diffusion_points.add((x1, y1))
 
        point_list = list(self._points)
        for _ in range(2500):   
            x, y = random.choice(point_list)
            x, y = scatter_inside(x, y, 0.15)
            self._center_diffusion_points.add((x, y))

    @staticmethod
    def calc_position(x, y, ratio):
        force = 1 / (((x - CANVAS_CENTER_X) ** 2 +
                      (y - CANVAS_CENTER_Y) ** 2) ** 0.52)

        dx = ratio * force * (x - CANVAS_CENTER_X)
        dy = ratio * force * (y - CANVAS_CENTER_Y)
        return x - dx, y - dy

    def calc(self, generate_frame):
        ratio = 8 * curve(generate_frame / 10 * pi)
        all_points = []
        for x, y in self._points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(2, 2)
            all_points.append((x, y, size, HEART_COLORS[2]))

        for x, y in self._edge_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = random.randint(1, 2)
            all_points.append((x, y, size, HEART_COLORS[1]))

        for x, y in self._center_diffusion_points:
            x, y = self.calc_position(x, y, ratio)
            size = 1
            all_points.append((x, y, size, HEART_COLORS[0]))

        self.all_points[generate_frame] = all_points

    def render(self, frame):
        return self.all_points[frame % self.generate_frame]



class Animator:
    def __init__(self, heart, root):
        self.heart = heart
        self.root = root
        self.mode = "draw"
        self.edge_points = list(heart._points)
        self.draw_progress = 0
        self.beat_frame = 0
        self.start_time = None
        self.fragments = []
        self.black_screen_start = None

    def render(self, canvas):
        canvas.delete("all")

        if self.mode == "draw":
            total = len(self.edge_points)
            self.draw_progress += total * 0.025
            visible = int(self.draw_progress)

            for i in range(min(visible, total)):
                x, y = self.edge_points[i]

                canvas.create_rectangle(x, y, x + 2, y + 2,
                                        width=0, fill=HEART_COLORS[2])

                if random.random() < 0.4:
                    canvas.create_rectangle(x + random.randint(-2, 2),
                                            y + random.randint(-2, 2),
                                            x + 2, y + 2,
                                            width=0, fill=HEART_COLORS[1])

                if random.random() < 0.15:
                    canvas.create_rectangle(x + random.randint(-3, 3),
                                            y + random.randint(-3, 3),
                                            x + 2, y + 2,
                                            width=0, fill=HEART_COLORS[0])

            if visible >= total:
                self.mode = "beat"
                self.start_time = time.time()

        elif self.mode == "beat":
            points = self.heart.render(self.beat_frame)

            for x, y, size, color in points:
                canvas.create_rectangle(x, y, x + size, y + size,
                                        width=0, fill=color)

            self.beat_frame += 1

            if time.time() - self.start_time > 8:
                self.prepare_fragments(points)
                self.mode = "scatter"

        elif self.mode == "scatter":
            new_fragments = []

            for frag in self.fragments:
                frag["x"] += frag["vx"]
                frag["y"] += frag["vy"]

                frag["vx"] *= 1.015
                frag["vy"] *= 1.015

                if (-20 < frag["x"] < CANVAS_WIDTH + 20 and
                        -20 < frag["y"] < CANVAS_HEIGHT + 20):

                    canvas.create_rectangle(
                        frag["x"], frag["y"],
                        frag["x"] + frag["size"],
                        frag["y"] + frag["size"],
                        width=0, fill=frag["color"]
                    )
                    new_fragments.append(frag)

            self.fragments = new_fragments

            if not self.fragments:
                if self.black_screen_start is None:
                    self.black_screen_start = time.time()
                elif time.time() - self.black_screen_start > 3:
                    self.root.destroy()

    def prepare_fragments(self, points):
        self.fragments.clear()

        for x, y, size, color in points:
            angle = random.uniform(0, 2 * pi)
            speed = random.uniform(5.0, 8.0)   

            self.fragments.append({
                "x": x,
                "y": y,
                "size": size,
                "color": color,
                "vx": cos(angle) * speed,
                "vy": sin(angle) * speed
            })


def draw(root, canvas, animator):
    animator.render(canvas)
    root.after(30, draw, root, canvas, animator)


if __name__ == "__main__":
    root = Tk()
    root.title("Heart Explosion")

    canvas = Canvas(root, bg="black",
                    width=CANVAS_WIDTH,
                    height=CANVAS_HEIGHT)
    canvas.pack()

    heart = Heart()
    animator = Animator(heart, root)

    draw(root, canvas, animator)
    root.mainloop()
