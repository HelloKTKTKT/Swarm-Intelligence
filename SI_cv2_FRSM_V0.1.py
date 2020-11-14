import random
import numpy as np
import cv2
import matplotlib.pyplot as plt

dim_x = 2000
dim_y = 1000

WAIT = 0
FORAGE = 1
TRANSFER = 2
INIT = 3

init_stack = 100
power_n = 2
theta = 1
robot_num = 100
walk_step = 10

node_1 = (400, 500)
node_2 = (1000, 500)
node_3 = (1220, 500)
radi = 50


class Robot:
    def __init__(self, index):
        self.index = index
        self.p_forage = 0
        self.position = [random.randint(0, dim_x), random.randint(0, dim_y)]
        self.arrival = [1, 0]
        self.state = INIT
        self.destination = (0, 0)

    def cal_probability(self, in_x):
        stimuli = init_stack - in_x
        if stimuli <= 0:
            self.p_forage = 0
        else:
            self.p_forage = stimuli ** power_n / (stimuli ** power_n + theta ** power_n)

    def make_decision_frsm(self, c_stack):
        roll = random.randint(0, 100) / 100
        if roll <= self.p_forage:
            self.arrival = [0, 0]
            self.state = FORAGE
        else:
            if c_stack > 0:
                self.arrival = [0, 0]
                self.state = TRANSFER
                c_stack -= 1
            else:
                self.state = WAIT
        return c_stack

    def make_decision_random(self, c_stack):
        roll = random.randint(0, 1)
        if roll:
            self.arrival = [0, 0]
            self.state = FORAGE
        else:
            if c_stack > 0:
                self.arrival = [0, 0]
                self.state = TRANSFER
                c_stack -= 1
            else:
                self.state = WAIT
        return c_stack

    def match_and_update_destination(self, c_stack):
        if self.arrival[0] == 0:
            if self.state == FORAGE:
                self.destination = node_1
            else:
                self.destination = node_3
        else:
            self.destination = node_2

        if self.arrival[0] and self.arrival[1]:
            if self.state == FORAGE:
                c_stack += 1
            self.cal_probability(c_stack)
            c_stack = self.make_decision_frsm(c_stack)
        return c_stack

    def move(self):
        d_x = self.position[0] - self.destination[0]
        d_y = self.position[1] - self.destination[1]
        string_sq = d_x ** 2 + d_y ** 2
        if string_sq <= radi ** 2:
            if self.state == INIT:
                self.state = WAIT
            elif self.destination == node_1 or self.destination == node_3:
                self.arrival[0] = 1
            else:
                self.arrival[1] = 1
        else:
            ratio = walk_step / (string_sq ** 0.5)
            walk_x = round(d_x * ratio)
            walk_y = round(d_y * ratio)
            self.position[0] -= walk_x
            self.position[1] -= walk_y
            self.position = position_fix(self.position[0], self.position[1])


def spawn_swarm():
    r_list = []
    for i in range(robot_num):
        tem_robot = Robot(i)
        r_list.append(tem_robot)
    return r_list


def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        current_r_num = len(param)
        tem_robot = Robot(current_r_num)
        tem_robot.position = [x, y]
        tem_robot.state = INIT
        param.append(tem_robot)


def draw_map():
    map1 = np.zeros((dim_y, dim_x, 3), np.uint8)
    cv2.rectangle(map1, (0, 0), (dim_x + 1, dim_y + 1), (255, 255, 255), -1)
    cv2.circle(map1, node_1, radi, (80, 80, 80), -1)
    cv2.circle(map1, node_2, radi, (180, 180, 80), -1)
    cv2.circle(map1, node_3, radi, (50, 220, 120), -1)
    return map1


def position_fix(x, y):
    if x > dim_x:
        x = 2 * dim_x - x
    elif x < 0:
        x = -x
    if y > dim_y:
        y = 2 * dim_y - y
    elif y < 0:
        y = -y
    return [x, y]


def plot_stack(stack_l):
    x_axis = []
    for i in range(len(stack_l)):
        x_axis.append(i)
    plt.plot(x_axis, stack_l, label="stack")
    plt.legend(loc="upper right")
    plt.grid(None)
    plt.xlabel("Time")
    plt.ylabel("Stack")
    plt.title("Stack_change")
    plt.show()


def main():
    cv2.namedWindow('test', cv2.WINDOW_NORMAL)
    map1 = draw_map()
    map1_blank = draw_map()
    robot_list = spawn_swarm()
    stack = 130
    time = 1000
    stack_list = []
    font = cv2.FONT_HERSHEY_SIMPLEX
    while time > 0:
        stack_text = 'stack: ' + str(stack)
        rob_text = 'robot number: ' + str(len(robot_list))
        cv2.putText(map1, stack_text, (100, 100), font, 1, (50, 10, 80), 2)
        cv2.putText(map1, rob_text, (100, 200), font, 1, (50, 10, 80), 2)
        cv2.setMouseCallback('test', mouse_click, robot_list)
        stack_list.append(stack)
        time -= 1
        for robot in robot_list:
            cv2.circle(map1, (robot.position[0], robot.position[1]), 3, (0, 0, 0), -1)
            robot.move()
            stack = robot.match_and_update_destination(stack)
        cv2.imshow('test', map1)
        cv2.waitKey(1)
        map1[:] = map1_blank[:]
    plot_stack(stack_list)


main()
