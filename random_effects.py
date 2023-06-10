import asyncio
# import struct < not needed atm
# import keyboard < not needed atm
import pyautogui
import math
from wizwalker import ClientHandler
from wizwalker.memory.memory_objects.camera_controller import ElasticCameraController, CameraController
from wizwalker import Client, utils, Orient, XYZ, Keycode, Hotkey, HotkeyListener, ModifierKeys
# from utils.collision import BoxGeomParams, CollisionWorld, CylinderGeomParams, MeshGeomParams, ProxyMesh, ProxyType, SphereGeomParams, TubeGeomParams, get_collision_data, CollisionFlag
import random

# Customize Below:
utils.override_wiz_install_location(r'E:\Kingsisle Entertainment\Wizard101') # Enter your wizard101 path.

# DO NOT TOUCH ANYTHING IN THE DASHES -----------------------------------------------------

def calc_Distance(xyz_1 : XYZ, xyz_2 : XYZ):
    # calculates the distance between 2 XYZs
    return math.sqrt((pow(xyz_1.x - xyz_2.x, 2.0)) + (pow(xyz_1.y - xyz_2.y, 2.0)) + (pow(xyz_1.z - xyz_2.z, 2.0)))

async def is_free(client: Client):
	# Returns True if not in combat, loading screen, or in dialogue.
	return not any([await client.is_loading(), await client.in_battle()])

async def wait_for_free(client: Client, wait_for_not: bool = False, interval: float = 0.25):
    if wait_for_not:
        while await is_free(client):
            await asyncio.sleep(interval)

    else:
        while not await is_free(client):
            await asyncio.sleep(interval)

async def set_player_scale(scale_to_set, client: Client, default_scale: float = 1.0):
    scale = await client.body.scale()
    if scale:
        await client.body.write_scale(scale_to_set)
    else:
        await client.body.write_scale(default_scale)
        await set_player_scale(scale_to_set, client)
        await asyncio.sleep(1)
    # await client.send_key(Keycode.W, 0.1)

async def set_player_speed(speed_to_set, client: Client, default_speed: int = 1):
    speed = await client.client_object.speed_multiplier()
    if speed:
        # print("Set speed!")
        await client.client_object.write_speed_multiplier(speed_to_set)
    else:
        # print("Speed wasn't found for some reason? Trying again...")
        await client.client_object.write_speed_multiplier(default_speed)
        await set_player_speed(speed_to_set, client)
        await asyncio.sleep(1)

async def set_camera_distance(min, max, set, zoom, client: Client, default_distance: float = 300.0):
    camera: ElasticCameraController = await client.game_client.elastic_camera_controller()
    client_object = await client.body.parent_client_object()
    await camera.write_attached_client_object(client_object)
    if set and min and max:
        await camera.write_distance_target(set)
        await camera.write_distance(set)
        await camera.write_min_distance(min)
        await camera.write_max_distance(max)
        if zoom:
            await camera.write_zoom_resolution(zoom)
    else:
        await camera.write_distance_target(default_distance)
        await camera.write_distance(default_distance)
        await camera.write_min_distance(150.0)
        await camera.write_max_distance(450.0)

async def update_camera(pitch, roll, yaw, camera: CameraController):
    camera_rot = await camera.orientation()
    if camera_rot:
        if pitch == None:
            pitch = camera_rot.pitch
        if roll == None:
            roll = camera_rot.roll
        if yaw == None:
            yaw = camera_rot.yaw
        await camera.update_orientation(Orient(pitch, roll, yaw))

async def update_player(pitch, roll, yaw, client: Client):
    player_rot = await client.body.orientation()
    if player_rot:
        if pitch == None:
            pitch = player_rot.pitch
        if roll == None:
            roll = player_rot.roll
        if yaw == None:
            yaw = player_rot.yaw
        await client.body.write_orientation(Orient(pitch, roll, yaw))

enabled = False # Disabling script by default

async def load_check(effect, client: Client, client_camera: CameraController):
    iterations = 0
    while iterations < 60:
        iterations = iterations + 1
        if await client.is_loading() == True:
            print("Detected zone change, reapplying affect...")
            while await client.is_loading() == True:
                await asyncio.sleep(0.1)
            await asyncio.sleep(0.25) # increase if you load slower
            await effect(client, client_camera)
        await asyncio.sleep(1)
# This function checks if you encounter a loading screen (or enter a new zone, which clears all effects)

async def unhook_ww(client: Client, client_camera: CameraController, handler: ClientHandler):
    print("Disabling Script...")
    await set_player_scale(1.0, client)
    await set_player_speed(0, client)
    await set_camera_distance(150, 450, 300, 150, client)
    await update_camera(None, 0.0, None, client_camera)
    await update_player(0.0, None, None, client)
    await handler.close()
    raise KeyboardInterrupt
# DO NOT TOUCH ANYTHING IN THE DASHES -----------------------------------------------------

current_effect = None

async def disable_effect(client, camera):    
    if current_effect == "scale" or current_effect == "first_person":
        await set_player_scale(1.0, client)
        await set_camera_distance(150, 450, 300, 150, client)
        await set_player_speed(1, client)
    elif current_effect == "speed":
        await set_player_speed(1, client)
    elif current_effect == "camera":
        await update_camera(None, 0.0, None, camera)
    elif current_effect == "player":
        await update_player(0.0, None, None, client)
    # elif current_effect == "hotkey":
    #     await invert_controls(client, camera)
    
async def fast(client, camera):
    global current_effect
    print("Activating fast effect...")
    try:
        await set_player_speed(5000, client)
    except:
        print("Failed to set player speed.")
    current_effect = "speed"

async def slow(client, camera):
    global current_effect
    print("Activating slow effect...")
    try:
        await set_player_speed(-50, client)
    except:
        print("Failed to set player speed.")
    current_effect = "speed"

async def giant(client, camera):
    global current_effect
    print("Activating giant effect...")
    await set_player_scale(3, client)
    await set_player_speed(100, client)
    await set_camera_distance(600, 900, 750, 600, client)
    current_effect = "scale"

async def titan(client, camera):
    global current_effect
    print("Activating TITAN effect...")
    await set_player_scale(10, client)
    await set_player_speed(300, client)
    await set_camera_distance(3000, 3500, 3500, 3500, client)
    current_effect = "scale"

async def tiny(client, camera):
    global current_effect
    print("Activating tiny effect...")
    await set_player_scale(0.5, client)
    await set_player_speed(-35, client)
    await set_camera_distance(100, 150, 125, 100, client)
    current_effect = "scale"

async def invisible(client, camera):
    global current_effect
    print("Activating invisible effect...")
    await set_player_scale(0, client)
    current_effect = "scale"

async def upside_down_camera(client, camera):
    global current_effect
    print("Activating upside down CAMERA effect...")
    await update_camera(None, 3.14, None, camera)
    current_effect = "camera"

async def flip_world(client, camera):
    global current_effect
    print("Activating upside down WORLD effect...")
    await update_camera(None, 3.14, None, camera)
    current_effect = "camera"

# async def first_person(client, camera):
#     global current_effect
#     print("Activating first person effect...")
#     iterations = 0
#     current_effect = "first_person"
#     while iterations < 600:
#         iterations = iterations + 1
#         if current_effect == "first_person":
#             await set_camera_distance(0.1, 0.1, 0.1, 0.1, client)
#             await asyncio.sleep(0.01)
#         else:
#             iterations = 601

# ^^^ ❌ This isn't working well. Don't enable it. ^^^

async def drunk(client: Client, camera: CameraController):
    global current_effect
    print("Activating drunk effect...")
    current_effect = "control"
    keys = [Keycode.A, Keycode.D]
    seconds = 0
    while seconds <= 60:
        seconds = seconds + 1
        if random.random() <= 0.1:
            await client.send_key(random.choice(keys), random.random() * 10 / 4)
        await asyncio.sleep(1)

# async def invert_controls(client: Client, camera):
#     global current_effect
#     print("Activating inverted controls effect...")

#     listener = HotkeyListener()

#     # await listener.remove_hotkey(Keycode.W, modifiers=ModifierKeys.NOREPEAT)
#     # await listener.remove_hotkey(Keycode.A, modifiers=ModifierKeys.NOREPEAT)
#     # await listener.remove_hotkey(Keycode.S, modifiers=ModifierKeys.NOREPEAT)
#     # await listener.remove_hotkey(Keycode.D, modifiers=ModifierKeys.NOREPEAT) 

#     async def callback():
#         keys = {Keycode.W: Keycode.S, Keycode.S: Keycode.W, Keycode.A: Keycode.D, Keycode.D: Keycode.A}
#         for key in keys:
#             if keyboard.is_pressed(key.value):
#                 await client.send_key(keys[key])

#     await listener.add_hotkey(Keycode.W, callback, modifiers=ModifierKeys.NOREPEAT)
#     await listener.add_hotkey(Keycode.S, callback, modifiers=ModifierKeys.NOREPEAT)
#     await listener.add_hotkey(Keycode.A, callback, modifiers=ModifierKeys.NOREPEAT)
#     await listener.add_hotkey(Keycode.D, callback, modifiers=ModifierKeys.NOREPEAT)

#     listener.start()
#     current_effect = "control"

# ^^^ ❌ This isn't working well. Don't enable it. ^^^


async def laying_down_player(client, camera):
    global current_effect
    print("Activating laying down PLAYER effect...")
    await update_player(3.14 / 2, None, None, client)
    current_effect = "player"

# Get the screen dimensions
screen_width, screen_height = pyautogui.size()

async def move_mouse_randomly(client, camera):
    global current_effect
    print("Activating mouse effect...")
    current_effect = "control"
    seconds = 0
    while seconds <= 60:
        seconds = seconds + 1
        if random.random() <= 0.5:
            movement_duration = random.random() / 2
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
    
            # Move the mouse to the random coordinates
            pyautogui.moveTo(x, y, duration=movement_duration)
        await asyncio.sleep(1)
    
screen_width, screen_height = pyautogui.size()

async def random_entity_tp(client: Client, camera):
    global current_effect
    print("Activating tp effect...")
    current_effect = "tp"
    seconds = 0
    entity_list = []
    while seconds <= 60:
        seconds = seconds + 1
        if seconds <= 1:
            ent_list = await client.get_base_entity_list()
            for entity in ent_list:
                if await entity.display_name():
                    if calc_Distance(await client.body.position(), await entity.location()) < 25000:
                        entity_list.append(entity)
            chosen_entity = random.choice(entity_list)
            await client.teleport(await chosen_entity.location())
            print(f"Teleported to {await chosen_entity.display_name()}.")
        await asyncio.sleep(1) # wait 1s for 1 min timer

    # Generate random coordinates within the screen boundaries

# List of available effects
effects = [drunk, slow, fast, tiny, giant, upside_down_camera, laying_down_player, invisible, titan, move_mouse_randomly, random_entity_tp]  # Add more effects here if you know what you're doing.
effects_with_timer = [drunk, move_mouse_randomly, random_entity_tp]

async def main():
    print("Starting in 3 seconds...") # Feel free to change the 3 to any amount of delay before it starts. 
    await asyncio.sleep(3) # Change this too if you do
    try:
        handler = ClientHandler()
        client = handler.get_new_clients()[0]
        client_camera = await client.game_client.selected_camera_controller()
        global enabled

        try:
            print("Hooking clients...")
            await client.activate_hooks()
            enabled = True
            # await client.mouse_handler.activate_mouseless() # <-- Dont activate this unless you know what you're doing.
            print("Activated hooks!")
        except:
            print("Failed to hook clients.")

        default_scale = await client.body.scale()
        default_speed_multi = await client.client_object.speed_multiplier()
        # Testing commands:
        await set_player_scale(1.0, client)
        await set_player_speed(0, client)
        await set_camera_distance(150, 450, 300, 150, client)
        await update_camera(None, 0.0, None, client_camera)
        await update_player(0.0, None, None, client)
        zone_name = await client.zone_name()
        print(f'Current Stats:\nScale: {default_scale}\nSpeed: {default_speed_multi}')

        while enabled == True:
            
            # Disable the current effect
            if not current_effect == None:
                print(f"Disabling {current_effect} effect...")
                await disable_effect(client, client_camera)
                print("Disabled!")

            # Choose a random effect from the list
            print("Choosing random effect...")
            effect = random.choice(effects)

            # Activate the chosen effect
            await effect(client, client_camera)
            print("Activated!")
            if not effect in effects_with_timer:
                await load_check(effect, client, client_camera) # 60 Second Timer
            
            print("Waiting for Wizard to be available.")
            await wait_for_free(client) # Waits for the client to not be loading or in battle.
            print("Wizard detected as available.")

            # Add small delay 
            await asyncio.sleep(0.01)
        
        await unhook_ww(client, client_camera, handler)
    except:
        await unhook_ww(client, client_camera, handler)
    
if __name__ == "__main__":
    asyncio.run(main())    