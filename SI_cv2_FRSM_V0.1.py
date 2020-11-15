import random
import numpy as np
import cv2
import matplotlib.pyplot as plt

FORAGE = 1
TRANSFER = 2
INIT = 0

dim_x = 2000
dim_y = 1000

robot_num = 30
stack_control = 101
node_1 = (400, 500)
node_2 = (1000, 500)
node_3 = (1220, 500)
radi = 50
walk_step = 10

power_n = 2
theta = 1


class Robot:
    def __init__(self, index):
        self.index = index
        self.arrival = [1, 0]
        self.position = [random.randint(0, dim_x), (random.randint(0, dim_y))]
        self.state = INIT
        self.forage_probability = 0

    def move(self):
        if self.state == INIT:
            flag = check_arrival(self.position, node_2)
            if flag == 1:
                self.arrival = [1, 1]
            else:
                walk_x, walk_y = forward(self.position, node_2)
                self.position[0] += walk_x
                self.position[1] += walk_y
                self.position = position_fix(self.position[0], self.position[1])
        elif self.state == FORAGE:
            if self.arrival[0] == 0:
                flag = check_arrival(self.position, node_1)
                if flag == 1:
                    self.arrival = [1, 0]
                else:
                    walk_x, walk_y = forward(self.position, node_1)
                    self.position[0] += walk_x
                    self.position[1] += walk_y
                    self.position = position_fix(self.position[0], self.position[1])
            elif self.arrival[1] == 0:
                flag = check_arrival(self.position, node_2)
                if flag == 1:
                    self.arrival = [1, 1]
                else:
                    walk_x, walk_y = forward(self.position, node_2)
                    self.position[0] += walk_x
                    self.position[1] += walk_y
                    self.position = position_fix(self.position[0], self.position[1])
            else:
                pass
        elif self.state == TRANSFER:
            if self.arrival[0] == 0:
                flag = check_arrival(self.position, node_3)
                if flag == 1:
                    self.arrival = [1, 0]
                else:
                    walk_x, walk_y = forward(self.position, node_3)
                    self.position[0] += walk_x
                    self.position[1] += walk_y
                    self.position = position_fix(self.position[0], self.position[1])
            elif self.arrival[1] == 0:
                flag = check_arrival(self.position, node_2)
                if flag == 1:
                    self.arrival = [1, 1]
                else:
                    walk_x, walk_y = forward(self.position, node_2)
                    self.position[0] += walk_x
                    self.position[1] += walk_y
                    self.position = position_fix(self.position[0], self.position[1])
            else:
                pass
        else:
            pass

    def rematch_frsm(self, c_stack):
        stimuli = stack_control - c_stack
        if stimuli <= 0:
            self.forage_probability = 0
        else:
            self.forage_probability = stimuli ** power_n / (stimuli ** power_n + theta ** power_n)
        roll = random.randint(0, 1000) / 1000
        if roll <= self.forage_probability:
            self.state = FORAGE
        else:
            self.state = TRANSFER

    def rematch_random(self, c_stack):
        stimuli = stack_control - c_stack
        if stimuli <= 0:
            self.forage_probability = 0
        else:
            self.forage_probability = stimuli ** power_n / (stimuli ** power_n + theta ** power_n)
        roll = random.randint(0, 1)
        if roll:
            self.state = FORAGE
        else:
            self.state = TRANSFER


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


def forward(start_n, end_n):
    d_x = end_n[0] - start_n[0]
    d_y = end_n[1] - start_n[1]
    string_sq = d_x ** 2 + d_y ** 2
    ratio = walk_step / (string_sq ** 0.5)
    walk_x = round(d_x * ratio)
    walk_y = round(d_y * ratio)
    return walk_x, walk_y


def check_arrival(a, b):
    d_x = a[0] - b[0]
    d_y = a[1] - b[1]
    distance_sq = d_x ** 2 + d_y ** 2
    if distance_sq <= radi ** 2:
        return 1
    else:
        return 0


def spawn_swarm():
    robot_l = []
    for i in range(robot_num):
        tem_robot = Robot(i)
        robot_l.append(tem_robot)
    return robot_l


def draw_map():
    map1 = np.zeros((dim_y, dim_x, 3), np.uint8)
    cv2.rectangle(map1, (0, 0), (dim_x + 1, dim_y + 1), (255, 255, 255), -1)
    cv2.circle(map1, node_1, radi, (80, 80, 80), -1)
    cv2.circle(map1, node_2, radi, (180, 180, 80), -1)
    cv2.circle(map1, node_3, radi, (50, 220, 120), -1)
    return map1


def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        current_r_num = len(param)
        tem_robot = Robot(current_r_num)
        tem_robot.position = [x, y]
        tem_robot.state = INIT
        param.append(tem_robot)


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
    stack = 50
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
            if robot.arrival[0] and robot.arrival[1]:
                if robot.state == FORAGE:
                    stack += 1

                robot.rematch_frsm(stack)
                if robot.state == TRANSFER:
                    if stack > 0:
                        stack -= 1
                        robot.arrival = [0, 0]
                    else:
                        robot.arrival = [1, 1]
                else:
                    robot.arrival = [0, 0]
            else:
                robot.move()
        cv2.imshow('test', map1)
        cv2.waitKey(1)
        map1[:] = map1_blank[:]
    plot_stack(stack_list)


main()

