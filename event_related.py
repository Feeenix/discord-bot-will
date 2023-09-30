from commands import *

def event_posting_loop():
    global task_queue, guilds_initialized
    while not guilds_initialized: # waits for both client.is_ready() and for the guild initialization to be done
        time.sleep(1)

    last_poll = time.time()
    while True:
        guilds = os.listdir("data/guilds")
        for guildID in guilds:
            guild = client.get_guild(int(guildID))
            if guild:
                settings = get_settings_for_guild(guild)
                if not settings["events_enabled"]:
                    continue
                events = get_events_for_guild(guild) # [{"timestamp": timestamp, "type": "message", "xp": xp, "userid": userid}, ... etc]
                if len(events) == 0:
                    continue
                events.sort(key=lambda x: x["timestamp"])
                if events[0]["timestamp"] < last_poll:
                    continue
                for event in events:
                    task_queue.append((event["timestamp"], post_event, (guild, event), {}, False))




                    if event["timestamp"] < last_poll:
                        break

        last_poll = time.time()
        time.sleep(1)





# class NewModal(nextcord.ui.Modal):