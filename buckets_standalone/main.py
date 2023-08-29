from time import sleep, monotonic
from gc import enable
from random import randint
from hardware import (
    DISPLAY,
    ENCODER,
    ENC,
    RED,
    BLUE,
    RED_LED,
    BLUE_LED,
    ENCB,
    REDB,
    BLUEB,
)
from audio_commands import play_track, set_vol
from led_commands import rgb_control

# Setting initial variables for use
position = ENCODER.position
last_position = position
MENU = [
    "KotH",
    "Attrition",
    "Death Clicks",
    "Domination 2",
    "Domination 3",
    "Basic Timer",
]
menu_index = 0
RESTART_OPTIONS = ["Yes", "No"]
restart_index = 0
EXTRAS = [
    "You're a nerd",
    "Weiners",
    "Ooh, a piece of candy",
    "Oatmeal",
    "You're my little pogchamp",
    "Anything is a \nhammer once",
    "Watch out for \nthem pointy bits",
    "This bucket \nkills fascists",
    "Taco Tuesday",
]


def display_message(message):
    """Displays a string to the 1602 LCD"""
    DISPLAY.clear()
    DISPLAY.print(message)


def update_team(teamp: str, speed=0.005):
    """Updates button LED state based on team"""
    global team
    team = teamp
    RED_LED.value = "Red" in teamp
    BLUE_LED.value = "Blue" in teamp
    rgb_control(team, delay=speed)


###


def main_menu():
    """Main menu for scrolling and displaying game options"""
    global position, last_position, menu_index, team, timer_state
    display_message(EXTRAS[randint(0, len(EXTRAS) - 1)])
    rgb_control("Off", "solid")
    for color in ["Red", "Blue", "Green"]:
        rgb_control(color)
    timer_state = True
    update_team("Green")
    display_message(f"Select a game:\n{MENU[menu_index]}")
    sleep(0.5)
    while ENC.value:
        position = ENCODER.position
        if position != last_position:
            if position > last_position:
                menu_index = (menu_index + 1) % len(MENU)
            elif position < last_position:
                menu_index = (menu_index - 1) % len(MENU)
            last_position = position
            display_message(f"Select a game:\n{MENU[menu_index]}")
    run_program(MENU[menu_index])


def run_program(menu_choice):
    """Used to run a function when the respective menu item is selected"""
    display_message(f"Running:\n{menu_choice}")
    sleep(1)
    if menu_choice == "Attrition":
        counter_screen(menu_choice)
    elif menu_choice == "Death Clicks":
        team_screen(menu_choice)
    else:
        timer_screen(menu_choice)


def timer_screen(game_mode):
    """Screen used to set time for KotH and Domination"""
    sleep(0.5)
    global position, last_position, game_length
    game_length = 0
    display_message(
        f"{game_mode}\nTime: {game_length // 60:02d}:{game_length % 60:02d}"
    )
    while ENC.value:
        position = ENCODER.position
        if position != last_position:
            if position > last_position:  # clockwise rotation
                game_length += 15
            elif position < last_position:  # counterclockwise rotation
                if game_length > 0:
                    game_length -= 15
            display_message(
                f"{game_mode}\nTime: {game_length // 60:02d}:{game_length % 60:02d}"
            )
            last_position = position
    sleep(0.1)
    standby_screen(game_mode)


def counter_screen(game_mode):
    """Screen used to set lives for Attrition"""
    sleep(0.5)
    global position, last_position, lives_count
    lives_count = 0
    display_message(f"{game_mode} \nLives: {lives_count}")
    while ENC.value:
        position = ENCODER.position
        if position != last_position:
            if position > last_position:
                lives_count += 1
            elif position < last_position:
                if lives_count > 0:
                    lives_count -= 1
            display_message(f"{game_mode}\nLives: {lives_count}")
            last_position = position
    sleep(0.1)
    team_screen(game_mode)


def team_screen(game_mode):
    """Screen for selecting team counter for Attrition and Death Clicks"""
    sleep(0.5)
    global team
    display_message(f"{game_mode}\nTeam:")
    while ENC.value:
        if not RED.value or not BLUE.value:
            if not RED.value:
                update_team("Red")
            if not BLUE.value:
                update_team("Blue")
            display_message(f"{game_mode}\nTeam {team}")
            sleep(0.1)
    sleep(0.1)
    standby_screen(game_mode)


def standby_screen(game_mode):
    """Pre-game confirmation screen"""
    sleep(0.5)
    if game_mode == "KotH":
        display_message(
            f"{game_mode} Ready\n{game_length // 60:02d}:{game_length % 60:02d}"
        )
    elif game_mode == "Attrition":
        display_message(f"{game_mode} Ready\nTeam {team} {lives_count} Life")
    elif game_mode == "Death Clicks":
        display_message(f"{game_mode}\nReady Team {team}")
    elif game_mode == "Domination 2":
        display_message(
            f"{game_mode}\nReady {game_length // 60:02d}:{game_length % 60:02d}"
        )
    elif game_mode == "Domination 3":
        display_message(
            f"{game_mode}\nReady {game_length // 60:02d}:{game_length % 60:02d}"
        )
    elif game_mode == "Basic Timer":
        display_message(
            f"{game_mode}\nReady {game_length // 60:02d}:{game_length % 60:02d}"
        )
    rgb_control("Off")
    sleep(0.5)
    while ENC.value:
        sleep(0.1)
    sleep(0.1)
    if game_mode == "KotH":
        display_message(f"{game_mode}\nStarting...")
        start_koth_timer(game_mode)
    elif game_mode == "Attrition":
        display_message(f"{game_mode}\nStarting...")
        start_attrition_counter(game_mode)
    elif game_mode == "Death Clicks":
        display_message(f"{game_mode}\nStarting...")
        start_clicks_counter(game_mode)
    elif game_mode == "Domination 2":
        display_message(f"{game_mode}\nStarting...")
        start_domination_2_timer(game_mode)
    elif game_mode == "Domination 3":
        display_message(f"{game_mode}\nStarting...")
        start_domination_3_timer(game_mode)
    elif game_mode == "Basic Timer":
        display_message(f"{game_mode}\nStarting...")
        start_basic_timer(game_mode)


def start_koth_timer(game_mode):
    """Function for KotH timers"""
    sleep(0.5)
    global position, last_position, restart_index, team, timer_state
    red_time = game_length
    blue_time = game_length
    red_time_str = f"{red_time // 60:02d}:{red_time % 60:02d}"
    blue_time_str = f"{blue_time // 60:02d}:{blue_time % 60:02d}"
    timer_state = True
    display_message(f"RED: {red_time_str}\nBLUE: {blue_time_str}")
    update_team("Green")
    sleep(0.5)
    while RED.value and BLUE.value:
        REDB.update()
        BLUEB.update()
        sleep(0.01)
    clock = monotonic()
    while red_time > 0 and blue_time > 0:
        ENCB.update()
        REDB.update()
        BLUEB.update()
        if not RED.value and team != "Red" and timer_state:
            update_team("Red", 0.0025)
            print(f"{team} timer started")
        elif not BLUE.value and team != "Blue" and timer_state:
            update_team("Blue", 0.0025)
            print(f"{team} timer started")
        if monotonic() - clock >= 1:
            if timer_state:
                if team == "Red":
                    red_time -= 1
                    red_time_str = f"{red_time // 60:02d}:{red_time % 60:02d}"
                elif team == "Blue":
                    blue_time -= 1
                    blue_time_str = f"{blue_time // 60:02d}:{blue_time % 60:02d}"
            display_message(f"RED:  {red_time_str}\nBLUE: {blue_time_str}")
            clock = monotonic()
        if ENCB.short_count > 1:
            timer_state = not timer_state
        if ENCB.long_press:
            break
    display_message(f"RED:  {red_time_str}\nBLUE: {blue_time_str}")
    while ENCB.value:
        ENCB.update()
        rgb_control(team)
        ENCB.update()
        rgb_control("Off")
    sleep(0.1)
    rgb_control("Off")
    display_message(f"Restart?:\n{RESTART_OPTIONS[restart_index]}")
    sleep(0.5)
    while ENC.value:
        position = ENCODER.position
        if position != last_position:
            if position > last_position:
                restart_index = (restart_index + 1) % len(RESTART_OPTIONS)
            elif position < last_position:
                restart_index = (restart_index - 1) % len(RESTART_OPTIONS)
            last_position = position
            display_message(f"Restart?:\n{RESTART_OPTIONS[restart_index]}")
    if restart_index == 0:
        update_team("Green")
        standby_screen(game_mode)
    elif restart_index == 1:
        main_menu()


def start_attrition_counter(game_mode):
    """Function for Attrition countdown"""
    sleep(0.5)
    global position, last_position, restart_index, team
    lives_attr = lives_count
    display_message(f"{team} Lives Left\n{lives_attr}")
    rgb_control(team)
    while lives_attr > 0:
        ENCB.update()
        if not RED.value or not BLUE.value:
            lives_attr -= 1
            rgb_control("Off", "chase", 0.001)
            rgb_control(team, "chase", 0.001)
            display_message(f"{team} Lives Left\n{lives_attr}")
        if ENCB.long_press:
            break
    display_message(f"{team} Lives Left\n{lives_attr}")
    while ENCB.value:
        ENCB.update()
        rgb_control(team)
        ENCB.update()
        rgb_control("Off")
    sleep(0.1)
    display_message(f"Restart?:\n{RESTART_OPTIONS[restart_index]}")
    rgb_control("Off")
    sleep(0.5)
    while ENC.value:
        position = ENCODER.position
        if position != last_position:
            if position > last_position:
                restart_index = (restart_index + 1) % len(RESTART_OPTIONS)
            elif position < last_position:
                restart_index = (restart_index - 1) % len(RESTART_OPTIONS)
            last_position = position
            display_message(f"Restart?:\n{RESTART_OPTIONS[restart_index]}")
    if restart_index == 0:
        update_team(("Red", "Blue")[team == "Blue"])
        standby_screen(game_mode)
    elif restart_index == 1:
        main_menu()


def start_clicks_counter(game_mode):
    """Function for Death Clicks countdown"""
    sleep(0.5)
    global position, last_position, restart_index, team
    death_count = 0
    display_message(f"{team} team\nDeaths {death_count}")
    rgb_control(team)
    while not ENCB.long_press:
        ENCB.update()
        if not RED.value or not BLUE.value:
            death_count += 1
            rgb_control("Off", "chase", 0.001)
            rgb_control(team, "chase", 0.001)
            display_message(f"{team} team\nDeaths {death_count}")
    display_message(f"Restart?:\n{RESTART_OPTIONS[restart_index]}")
    rgb_control("Off")
    sleep(0.5)
    while ENC.value:
        position = ENCODER.position
        if position != last_position:
            if position > last_position:
                restart_index = (restart_index + 1) % len(RESTART_OPTIONS)
            elif position < last_position:
                restart_index = (restart_index - 1) % len(RESTART_OPTIONS)
            last_position = position
            display_message(f"Restart?:\n{RESTART_OPTIONS[restart_index]}")
    if restart_index == 0:
        update_team(("Red", "Blue")[team == "Blue"])
        standby_screen(game_mode)
    elif restart_index == 1:
        main_menu()


def start_domination_2_timer(game_mode):
    """Function for Domination v2 timer"""
    sleep(0.5)
    global position, last_position, restart_index, team, timer_state
    dom_time = game_length
    dom_time_str = f"{dom_time // 60:02d}:{dom_time % 60:02d}"
    timer_state = True
    display_message(f"{team} Team\n{dom_time // 60:02d}:{dom_time % 60:02d}")
    update_team("Green")
    clock = monotonic()
    while dom_time > 0:
        ENCB.update()
        REDB.update()
        BLUEB.update()
        if REDB.long_press and timer_state:
            update_team("Red", 0.0025)
            display_message(f"{team} Team \n{dom_time // 60:02d}:{dom_time % 60:02d}")
            print(f"{team} point control")
        elif BLUEB.long_press and timer_state:
            update_team("Blue", 0.0025)
            display_message(f"{team} Team \n{dom_time // 60:02d}:{dom_time % 60:02d}")
            print(f"{team} point control")
        if monotonic() - clock >= 1:
            if timer_state:
                dom_time -= 1
                dom_time_str = f"{dom_time // 60:02d}:{dom_time % 60:02d}"
            display_message(f"{team} Team\n{dom_time_str}")
            clock = monotonic()
        if ENCB.short_count > 1:
            timer_state = not timer_state
            sleep(0.1)
        if ENCB.long_press:
            break
    display_message(f"{team} Team\nPoint Locked")
    while ENCB.value:
        ENCB.update()
        rgb_control(team)
        ENCB.update()
        rgb_control("Off")
    sleep(0.1)
    display_message(f"Restart?:\n{RESTART_OPTIONS[restart_index]}")
    rgb_control("Off")
    while ENC.value:
        position = ENCODER.position
        if position != last_position:
            if position > last_position:
                restart_index = (restart_index + 1) % len(RESTART_OPTIONS)
            elif position < last_position:
                restart_index = (restart_index - 1) % len(RESTART_OPTIONS)
            last_position = position
            display_message(f"Restart?:\n{RESTART_OPTIONS[restart_index]}")
    if restart_index == 0:
        update_team("Green")
        standby_screen(game_mode)
    elif restart_index == 1:
        main_menu()


def start_domination_3_timer(game_mode):
    """Function for Domination v3 timer"""
    sleep(0.5)
    global position, last_position, restart_index, team, timer_state
    red_time, blue_time = game_length, game_length
    red_time_str = f"{red_time // 60:02d}:{red_time % 60:02d}"
    blue_time_str = f"{blue_time // 60:02d}:{blue_time % 60:02d}"
    timer_state = True
    display_message(f"RED: {red_time_str}\nBLUE: {blue_time_str}")
    update_team("Green")
    sleep(0.5)
    while RED.value and BLUE.value:
        REDB.update()
        BLUEB.update()
        sleep(0.01)
    clock = monotonic()
    while red_time > 0 and blue_time > 0:
        ENCB.update()
        REDB.update()
        BLUEB.update()
        if REDB.long_press and team != "Red" and timer_state:
            update_team("Red", 0.0025)
            print("red timer started")
        elif BLUEB.long_press and team != "Blue" and timer_state:
            update_team("Blue", 0.0025)
            print("blue timer started")
        if monotonic() - clock >= 1:
            if timer_state:
                if team == "Red":
                    red_time -= 1
                    red_time_str = f"{red_time // 60:02d}:{red_time % 60:02d}"
                elif team == "Blue":
                    blue_time -= 1
                    blue_time_str = f"{blue_time // 60:02d}:{blue_time % 60:02d}"
            display_message(f"RED:  {red_time_str}\nBLUE: {blue_time_str}")
            clock = monotonic()
        if ENCB.short_count > 1:
            timer_state = not timer_state
        if ENCB.long_press:
            break
    display_message(f"{team} Team\nPoint Locked")
    while True:
        ENCB.update()
        rgb_control(team)
        rgb_control("Off")
        if ENCB.short_count != 0:
            break
    sleep(0.5)
    rgb_control("Off")
    display_message(f"Restart?:\n{RESTART_OPTIONS[restart_index]}")
    while ENC.value:
        position = ENCODER.position
        if position != last_position:
            if position > last_position:
                restart_index = (restart_index + 1) % len(RESTART_OPTIONS)
            elif position < last_position:
                restart_index = (restart_index - 1) % len(RESTART_OPTIONS)
            last_position = position
            display_message(f"Restart?:\n{RESTART_OPTIONS[restart_index]}")
    if restart_index == 0:
        rgb_control("Green")
        RED_LED.value = False
        BLUE_LED.value = False
        standby_screen(game_mode)
    elif restart_index == 1:
        main_menu()


def start_basic_timer(game_mode):
    sleep(0.5)
    global position, last_position, restart_index, timer_state
    basic_time = game_length
    display_message(f"{basic_time // 60:02d}:{basic_time % 60:02d}")
    clock = monotonic()
    while basic_time > 0:
        ENCB.update()
        if monotonic() - clock >= 1:
            if timer_state:
                basic_time -= 1
                if basic_time < 11:
                    play_track(basic_time + 15)
            display_message(f"{basic_time // 60:02d}:{basic_time % 60:02d}")
            clock = monotonic()
        if basic_time == 30 and timer_state:
            play_track(26)
        if ENCB.short_count != 0:
            timer_state = not timer_state
        if ENCB.long_press:
            break
    sleep(0.5)
    display_message(f"Restart?:\n{RESTART_OPTIONS[restart_index]}")
    while ENC.value:
        position = ENCODER.position
        if position != last_position:
            if position > last_position:
                restart_index = (restart_index + 1) % len(RESTART_OPTIONS)
            elif position < last_position:
                restart_index = (restart_index - 1) % len(RESTART_OPTIONS)
            last_position = position
            display_message(f"Restart?:\n{RESTART_OPTIONS[restart_index]}")
    if restart_index == 0:
        rgb_control("Green")
        standby_screen(game_mode)
    elif restart_index == 1:
        main_menu()


enable()

set_vol(30)

if __name__ == "__main__":
    main_menu()
