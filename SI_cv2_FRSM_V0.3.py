import random
import numpy as np
import cv2
import matplotlib.pyplot as plt

FORAGE_0 = 1
FORAGE_1 = 3
TRANSFER = 2
INIT = 0

dim_x = 2000
dim_y = 1000

robot_num = 30
stack_control = [20, 20]
node_1 = (400, 350)
node_2 = (1100, 450)
node_3 = (1000, 500)
node_4 = (1000, 750)
radi = 50
walk_step = 5
delay = 10

power_n = 2
theta = 1


class Robot:
    def __init__(self, index):
        self.index = index
        self.arrival = [1, 0]
        self.position = [random.randint(0, dim_x), (random.randint(0, dim_y))]
        self.state = INIT
        self.probability = [0, 0, 0]
        self.lineup = 0
        self.comm_range = 45
        self.walk_step = random.randint(2, 5)

    def move(self):
        if self.state == INIT:
            flag = check_arrival(self.position, node_3)
            if flag == 1:
                self.arrival = [1, 1]
            else:
                walk_x, walk_y = forward(self.position, node_3, self.walk_step)
                self.position[0] += walk_x
                self.position[1] += walk_y
                self.position = position_fix(self.position[0], self.position[1])
        elif self.state == FORAGE_0:
            if self.arrival[0] == 0:
                flag = check_arrival(self.position, node_1)
                if flag == 1:
                    self.arrival = [1, 0]
                else:
                    walk_x, walk_y = forward(self.position, node_1, self.walk_step)
                    self.position[0] += walk_x
                    self.position[1] += walk_y
                    self.position = position_fix(self.position[0], self.position[1])
            elif self.arrival[1] == 0:
                flag = check_arrival(self.position, node_3)
                if flag == 1:
                    self.arrival = [1, 1]
                else:
                    walk_x, walk_y = forward(self.position, node_3, self.walk_step)
                    self.position[0] += walk_x
                    self.position[1] += walk_y
                    self.position = position_fix(self.position[0], self.position[1])
            else:
                pass
        elif self.state == FORAGE_1:
            if self.arrival[0] == 0:
                flag = check_arrival(self.position, node_2)
                if flag == 1:
                    self.arrival = [1, 0]
                else:
                    walk_x, walk_y = forward(self.position, node_2, self.walk_step)
                    self.position[0] += walk_x
                    self.position[1] += walk_y
                    self.position = position_fix(self.position[0], self.position[1])
            elif self.arrival[1] == 0:
                flag = check_arrival(self.position, node_3)
                if flag == 1:
                    self.arrival = [1, 1]
                else:
                    walk_x, walk_y = forward(self.position, node_3, self.walk_step)
                    self.position[0] += walk_x
                    self.position[1] += walk_y
                    self.position = position_fix(self.position[0], self.position[1])
            else:
                pass

        elif self.state == TRANSFER:
            if self.arrival[0] == 0:
                flag = check_arrival(self.position, node_4)
                if flag == 1:
                    self.arrival = [1, 0]
                else:
                    walk_x, walk_y = forward(self.position, node_4, self.walk_step)
                    self.position[0] += walk_x
                    self.position[1] += walk_y
                    self.position = position_fix(self.position[0], self.position[1])
            elif self.arrival[1] == 0:
                flag = check_arrival(self.position, node_3)
                if flag == 1:
                    self.arrival = [1, 1]
                else:
                    walk_x, walk_y = forward(self.position, node_3, self.walk_step)
                    self.position[0] += walk_x
                    self.position[1] += walk_y
                    self.position = position_fix(self.position[0], self.position[1])
            else:
                pass
        else:
            pass

    def rematch_frsm(self, c_stack):
        stimuli_0 = stack_control[0] - c_stack[0]
        stimuli_1 = stack_control[1] - c_stack[1]
        stimuli_2 = min(-stimuli_0, -stimuli_1)
        if stimuli_0 <= 0:
            self.probability[0] = 0
        else:
            self.probability[0] = stimuli_0 ** power_n / (stimuli_0 ** power_n + theta ** power_n)

        if stimuli_1 <= 0:
            self.probability[1] = 0
        else:
            self.probability[1] = stimuli_1 ** power_n / (stimuli_1 ** power_n + theta ** power_n)

        if stimuli_2 <= 0:
            self.probability[2] = 0
        else:
            self.probability[2] = stimuli_2 ** power_n / (stimuli_2 ** power_n + theta ** power_n)

        sum_value = 0
        for i in range(len(self.probability)):
            sum_value += self.probability[i]
        if sum_value == 0:
            # self.rematch_random(c_stack)
            self.state = TRANSFER
        else:
            p_list = []
            for i in range(len(self.probability)):
                p_list.append(self.probability[i] / sum_value)

            p_sum = [0, 0, 0]
            for i in range(len(p_sum)):
                for j in range(0, i + 1):
                    p_sum[i] += p_list[j]

            roll = random.randint(0, 1000) / 1000
            if roll <= p_sum[0]:
                self.state = FORAGE_0
            elif roll <= p_sum[1]:
                self.state = FORAGE_1
            else:
                self.state = TRANSFER


    def rematch_random(self, c_stack):
        roll = random.randint(0, 2)
        if roll == 0:
            self.state = FORAGE_0
        elif roll == 1:
            self.state = FORAGE_1
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


def forward(start_n, end_n, step):
    d_x = end_n[0] - start_n[0]
    d_y = end_n[1] - start_n[1]
    string_sq = d_x ** 2 + d_y ** 2
    ratio = step / (string_sq ** 0.5)
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
    cv2.circle(map1, node_4, radi, (100, 100, 200), -1)
    return map1


def draw_local_network(r_list, map):
    for i in range(len(r_list)):
        for j in range(len(r_list)):
            if i != j:
                dx = r_list[i].position[0] - r_list[j].position[0]
                dy = r_list[i].position[1] - r_list[j].position[1]
                if dx ** 2 + dy ** 2 <= r_list[i].comm_range ** 2:
                    cv2.line(map, (r_list[i].position[0], r_list[i].position[1]),
                             (r_list[j].position[0], r_list[j].position[1]), (10, 200, 255), 2)


def mouse_click_1(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        current_r_num = len(param)
        tem_robot = Robot(current_r_num)
        tem_robot.position = [x, y]
        tem_robot.state = INIT
        param.append(tem_robot)
    elif event == cv2.EVENT_RBUTTONDOWN:
        while True:
            value = cv2.waitKey(1)
            if value == 32:
                break
    else:
        pass


def plot_stack(stack_l, stack_m):
    x_axis = []
    for i in range(len(stack_l)):
        x_axis.append(i)
    plt.plot(x_axis, stack_l, label="stack_0")
    plt.plot(x_axis, stack_m, label="stack_1")
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
    stack = [0, 0]
    time = 2000
    stack_list_0 = []
    stack_list_1 = []
    font = cv2.FONT_HERSHEY_SIMPLEX
    while time > 0:
        stack_text_0 = 'stack_0: ' + str(stack[0])
        stack_text_1 = 'stack_1: ' + str(stack[1])
        rob_text = 'robot number: ' + str(len(robot_list))
        cv2.putText(map1, stack_text_0, (100, 100), font, 1, (50, 10, 80), 2)
        cv2.putText(map1, stack_text_1, (100, 200), font, 1, (50, 10, 80), 2)
        cv2.putText(map1, rob_text, (100, 300), font, 1, (50, 10, 80), 2)
        cv2.setMouseCallback('test', mouse_click_1, robot_list)
        draw_local_network(robot_list, map1)
        stack_list_0.append(stack[0])
        stack_list_1.append(stack[1])
        time -= 1
        for robot in robot_list:
            cv2.circle(map1, (robot.position[0], robot.position[1]), 7 - robot.walk_step, (0, 0, 0), -1)
            cv2.circle(map1, (robot.position[0], robot.position[1]), robot.comm_range, (0, 0, 255), 1)
            if robot.lineup > 0:
                robot.lineup -= 1
                if robot.lineup == 0:
                    if stack[0] > 0 and stack[1] > 0:
                        stack[0] -= 1
                        stack[1] -= 1
                        robot.arrival = [0, 0]
                    else:
                        robot.arrival = [1, 1]
                else:
                    pass
            else:
                if robot.arrival[0] and robot.arrival[1]:
                    if robot.state == FORAGE_0:
                        stack[0] += 1
                    elif robot.state == FORAGE_1:
                        stack[1] += 1
                    else:
                        pass

                    robot.rematch_frsm(stack)
                    if robot.state == TRANSFER:
                        robot.lineup = delay
                    else:
                        robot.arrival = [0, 0]
                else:
                    robot.move()

        cv2.imshow('test', map1)
        cv2.waitKey(1)
        map1[:] = map1_blank[:]
    plot_stack(stack_list_0, stack_list_1)


main()
