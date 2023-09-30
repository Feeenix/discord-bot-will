from lib import *





# a function that runs as a thread in the background
# it loops for every guild in the file system, and tests if the guild has a voice xp enabled
# the thread constantly checks every voice channel in the server and updates the voice xp of every user in it
# the thread also checks if the user has leveled up, and if so, sends a message to the user once they no longer are in a voice channel

def voice_xp():
    global guilds_initialized
    while not client.is_ready():
        time.sleep(1)

    print(client.guilds)
    for guild in client.guilds:
        if not os.path.exists(os.path.join("data/guilds/", str(guild.id))):
            initialize_guild(guild)
    guilds_initialized = True
    last_poll = time.time()
    while True:
        guilds = os.listdir("data/guilds")
        for guildID in guilds:
            guild = client.get_guild(int(guildID))
            if guild:
                settings = get_settings_for_guild(guild)
                if not settings["voicexp"]:
                    continue
                active_users = []
                sessions = get_active_voice_sessions(guild)
                for channel in guild.voice_channels:
                    active_users.extend([member.id for member in channel.members if not member.bot])
                    if len(channel.members) == 0:
                        continue
                    loneliness_modifier = 1
                    if len(channel.members) == 1:
                        # if the user is alone in a voice channel
                        loneliness_modifier = 0.8
                        # continue #? maybe we should give them xp for being alone?  
                    for member in channel.members:
                        if member.bot:
                            continue
                        if not member.voice: # if the user is not in a voice channel
                            continue
                        if member.voice.afk: # if the user is in an afk channel
                            continue
                        
                        xp_modifier = 1.0
                        if member.voice.self_stream: # if the user is streaming
                            xp_modifier = 1.0
                        if member.voice.self_video: # if the user is streaming
                            xp_modifier = 1.0
                        if member.voice.self_mute: # if the user is muted
                            xp_modifier = 0.1
                        if member.voice.self_deaf: # if the user is deafened
                            xp_modifier = 0.1
                        if member.voice.mute: # if the user is server muted
                            xp_modifier = 0.1
                        if member.voice.deaf: # if the user is server deafened
                            xp_modifier = 0.1
                        
                        this_time = time.time()
                        if not str(member.id) in sessions:
                            set_voice_session_start(guild, member.id, this_time)
                            sessions[str(member.id)] = {"start_time":this_time, "xp_gained":0.0, "time_unmuted":0.0}
                            print(member.id, "joined voice channel")
                        time_diff = this_time - last_poll
                        xp_rate_modifier = xp_rate(this_time - sessions[str(member.id)]["start_time"])
                        xp = (time_diff * settings["voicexp"] * xp_modifier*xp_rate_modifier*loneliness_modifier)
                        
                        if xp_modifier == 1.0: # unmuted
                            sessions[str(member.id)]["time_unmuted"] += time_diff
                        sessions[str(member.id)]["xp_gained"] += xp
                        add_voice_xp(guild, member.id, xp)
                        add_voice_time(guild, member.id, time_diff)
                        
                save_json(os.path.join("data/guilds/", str(guild.id),"voice_session_time.json"), sessions)
                to_be_removed = []
                if len(sessions) != len(active_users):
                    for strUserID in sessions:
                        if not int(strUserID) in active_users:
                            to_be_removed.append(strUserID)
                
                        print(strUserID, "left voice channel")
                    remove_voice_session_list(guild, to_be_removed)
                    
        # print("voice xp loop")
        last_poll = time.time()
        time.sleep(1)

