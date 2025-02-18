import paho.mqtt.client as mqtt_client
import asyncio
import json
import os
from pylitterbot import Account, LitterRobot3, LitterRobot4, FeederRobot

LB2MQTT_BROKER = os.environ['LB2MQTT_BROKER']
LB2MQTT_USERNAME = os.environ['LB2MQTT_USERNAME']
LB2MQTT_PASSWORD = os.environ['LB2MQTT_PASSWORD']
LB2MQTT_PORT = os.environ['LB2MQTT_PORT']
LB2MQTT_TOPIC_PREFIX = os.environ['LB2MQTT_TOPIC_PREFIX']
LB_USERNAME = os.environ['LB_USERNAME']
LB_PASSWORD = os.environ['LB_PASSWORD']

async def lb_main():
    # Create an account.
    account = Account()

    try:
        # Connect to the API and load robots.
        await account.connect(username=LB_USERNAME, password=LB_PASSWORD, load_robots=True, load_pets=True)

        # Print robots associated with account.
        print("Robots:")
        for robot in account.robots:
            print(robot)

        print("Pets:")
        for pet in account.pets:
            print(pet)
            weight_history = await pet.fetch_weight_history()
            for weight in weight_history:
                print(weight)

    finally:
        # Disconnect from the API.
        await account.disconnect()


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client("litterbot")
    client.username_pw_set(LB2MQTT_USERNAME, LB2MQTT_PASSWORD)
    client.on_connect = on_connect
    client.connect(LB2MQTT_BROKER, LB2MQTT_PORT)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received message: topic: `{msg.topic}` payload:`{msg.payload.decode()}` ")
        asyncio.run(handle_message(client, msg))

    client.on_message = on_message
    client.subscribe(f"{LB2MQTT_TOPIC_PREFIX}/#")

async def handle_message(client, msg):
    topic_parts = msg.topic.split('/')
    if len(topic_parts) < 3:
        return

    command = topic_parts[2]
    payload = json.loads(msg.payload)
    print(f"command is: {command}")

    account = Account()
    try:
        await account.connect(username=LB_USERNAME, password=LB_PASSWORD, load_robots=True, load_pets=True)

        if command == "refresh":
            await account.refresh_robots()
        elif command == "start_cleaning":
            robot_id = payload.get("robot_id")
            robot = account.get_robot(robot_id)
            if robot:
                await robot.start_cleaning()
        elif command == "reset_settings":
            robot_id = payload.get("robot_id")
            robot = account.get_robot(robot_id)
            if robot:
                await robot.reset_settings()
        elif command == "set_panel_lockout":
            robot_id = payload.get("robot_id")
            value = payload.get("value")
            robot = account.get_robot(robot_id)
            if robot:
                await robot.set_panel_lockout(value)
        elif command == "set_night_light":
            robot_id = payload.get("robot_id")
            value = payload.get("value")
            robot = account.get_robot(robot_id)
            if robot:
                await robot.set_night_light(value)
        elif command == "set_power_status":
            robot_id = payload.get("robot_id")
            value = payload.get("value")
            robot = account.get_robot(robot_id)
            if robot:
                await robot.set_power_status(value)
        elif command == "set_sleep_mode":
            robot_id = payload.get("robot_id")
            value = payload.get("value")
            sleep_time = payload.get("sleep_time")
            robot = account.get_robot(robot_id)
            if robot:
                await robot.set_sleep_mode(value, sleep_time)
        elif command == "set_wait_time":
            robot_id = payload.get("robot_id")
            wait_time = payload.get("wait_time")
            robot = account.get_robot(robot_id)
            if robot:
                await robot.set_wait_time(wait_time)
        elif command == "set_name":
            robot_id = payload.get("robot_id")
            name = payload.get("name")
            robot = account.get_robot(robot_id)
            if robot:
                await robot.set_name(name)
        elif command == "get_activity_history":
            robot_id = payload.get("robot_id")
            limit = payload.get("limit", 100)
            robot = account.get_robot(robot_id)
            if robot:
                history = await robot.get_activity_history(limit)
                for data in history:
                    print(data)

#                client.publish(f"{LB2MQTT_TOPIC_PREFIX}/response", json.dumps(history))
        elif command == "get_insight":
            robot_id = payload.get("robot_id")
            days = payload.get("days", 30)
            timezone_offset = payload.get("timezone_offset")
            robot = account.get_robot(robot_id)
            if robot:
                insight = await robot.get_insight(days, timezone_offset)
                for data in insight:
                    print(insight)
#                client.publish(f"{LB2MQTT_TOPIC_PREFIX}/response", json.dumps(insight))

    finally:
        # Disconnect from the API.
        await account.disconnect()





def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

if __name__ == "__main__":
    asyncio.run(lb_main())
    run()
