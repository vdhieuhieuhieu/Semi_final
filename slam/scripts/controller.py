#!/usr/bin/env python3
import rospy
from std_msgs.msg import Float64
from geometry_msgs.msg import Twist
import pygame

# Khởi tạo pygame
pygame.init()
win = pygame.display.set_mode((300, 300))
pygame.display.set_caption("Keyboard Control")

# Khởi tạo font
font = pygame.font.SysFont("Arial", 18)

# Khởi tạo node ROS
rospy.init_node("two_dof_arm_controller")

# Tạo Publisher cho các bộ điều khiển
first_motor_pub = rospy.Publisher("/link1_joint_controller/command", Float64, queue_size=10)
second_motor_pub = rospy.Publisher("/link2_joint_controller/command", Float64, queue_size=10)
gripper_control_pub = rospy.Publisher("/gripper_control_controller/command", Float64, queue_size=10)
gripper_left_pub = rospy.Publisher("/gripper_left_controller/command", Float64, queue_size=10)

# Tạo Publisher cho điều khiển bánh xe
cmd_vel_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)

# Tần số gửi lệnh
rate = rospy.Rate(10)

# Giá trị vận tốc
linear_speed = 0.5  # Tốc độ tiến/lùi
angular_speed = 1.0  # Tốc độ quay

# Danh sách Publisher cho gripper với trạng thái đảo chiều
gripper_pubs = [(gripper_control_pub, False), (gripper_left_pub, True)]

# Khởi tạo vị trí hiện tại
current1, current2, current_gripper = 0.0, 0.0, 0.0

def smooth_move(pub_list, current, target, steps=100, rate=50):
    delta = (target - current) / steps
    for _ in range(steps):
        current += delta
        msg = Float64()
        for pub, inv in pub_list:
            msg.data = -current if inv else current
            pub.publish(msg)
        rospy.sleep(1.0 / rate)
    return current

def get_key_input():
    twist = Twist()
    keys = pygame.key.get_pressed()

    # Điều khiểdn bánh xe
    if keys[pygame.K_w]:
        twist.linear.x = linear_speed
    elif keys[pygame.K_s]:
        twist.linear.x = -linear_speed
    if keys[pygame.K_a]:
        twist.angular.z = angular_speed
    elif keys[pygame.K_d]:
        twist.angular.z = -angular_speed

    return twist

def display_info():
    # Hiển thị thông tin lên cửa sổ Pygame
    win.fill((255, 255, 255))  # Lấp đầy màn hình với màu trắng

    # Hiển thị thông tin động cơ
    motor1_text = font.render(f"Motor 1: {current1:.2f}", True, (0, 0, 0))
    motor2_text = font.render(f"Motor 2: {current2:.2f}", True, (0, 0, 0))
    gripper_text = font.render(f"Gripper: {current_gripper:.2f}", True, (0, 0, 0))

    # Hiển thị thông tin điều khiển
    control_text = font.render("W: Forward | S: Backward", True, (0, 0, 0))
    control_text2 = font.render("A: Left | D: Right", True, (0, 0, 0))
    control_text3 = font.render("E: Motor 1 Up | Q: Motor 1 Down", True, (0, 0, 0))
    control_text4 = font.render("X: Motor 2 Up | C: Motor 2 Down", True, (0, 0, 0))
    control_text5 = font.render("R: Gripper Open | F: Gripper Close", True, (0, 0, 0))

    # Vẽ các thông tin vào cửa sổ
    win.blit(motor1_text, (10, 10))
    win.blit(motor2_text, (10, 30))
    win.blit(gripper_text, (10, 50))
    win.blit(control_text, (10, 70))
    win.blit(control_text2, (10, 90))
    win.blit(control_text3, (10, 110))
    win.blit(control_text4, (10, 130))
    win.blit(control_text5, (10, 150))

    pygame.display.update()  # Cập nhật màn hình

def main():
    global current1, current2, current_gripper
    running = True
    while running and not rospy.is_shutdown():
        pygame.event.pump()  # Đảm bảo pygame hoạt động chính xác
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Điều khiển bánh xe
        twist = get_key_input()
        cmd_vel_pub.publish(twist)

        # Điều khiển tay máy
        keys = pygame.key.get_pressed()

        if keys[pygame.K_e]:
            current1 = smooth_move([(first_motor_pub, False)], current1, current1 + 0.1)
        elif keys[pygame.K_q]:
            current1 = smooth_move([(first_motor_pub, False)], current1, current1 - 0.1)

        if keys[pygame.K_x]:
            current2 = smooth_move([(second_motor_pub, False)], current2, current2 + 0.1)
        elif keys[pygame.K_c]:
            current2 = smooth_move([(second_motor_pub, False)], current2, current2 - 0.1)

        if keys[pygame.K_r]:
            current_gripper = smooth_move(gripper_pubs, current_gripper, current_gripper + 0.1)
        elif keys[pygame.K_f]:
            current_gripper = smooth_move(gripper_pubs, current_gripper, current_gripper - 0.1)

        # Cập nhật giao diện
        display_info()

        rate.sleep()

    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
