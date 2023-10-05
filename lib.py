from imports_and_constants import *


def copy_file(src, dst):
    shutil.copyfile(src, dst)


def load_json(file_name):
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except json.decoder.JSONDecodeError:
        if os.path.exists(file_name + ".old"):
            copy_file(file_name + ".old", file_name)
            with open(file_name, "r") as file:
                return json.load(file)
        else:
            # raise json.decoder.JSONDecodeError(
            #     "JSON file is corrupted and no backup exists", "", 0)
            print("JSON file is corrupted and no backup exists")
            return {}



def save_json(file_name, data):
    if os.path.exists(file_name):
        copy_file(file_name, file_name + ".old")

    with open(file_name, "w") as file:
        json.dump(data, file, indent=2)


def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.1f} s" # 0..60
    if seconds < 60*60:
        return f"{seconds/60:.1f} m"
    return f"{seconds/60/60:.1f} h"
    
def format_time_large(seconds):
    if seconds < 60:
        return f"{seconds:.1f} s"
    if seconds < 60*60:
        return f"{seconds/60:.1f} m"
    if seconds < 60*60*24:
        return f"{seconds/60/60:.1f} h"
    if seconds < 60*60*24*365:
        return f"{seconds/60/60/24:.2f} d"
    return f"{seconds/60/60/24/365:.2f} y"


def initialize_guild(guild):
    guildID = guild.id
    os.mkdir(os.path.join("data/guilds/", str(guildID)))
    save_json(os.path.join("data/guilds/", str(guildID),
              "settings.json"), default_settings)
    save_json(os.path.join("data/guilds/", str(guildID), "meta.json"),
              {
        "name": guild.name,
        "id": guildID,
        "owner": guild.owner_id,
        "icon": guild.icon.url if guild.icon else None,
    })
    save_json(os.path.join("data/guilds/", str(guildID),
              "text_xp.json"), {}) # {"userid": xp}
    save_json(os.path.join("data/guilds/", str(guildID),
              "voice_times.json"), {}) # {"userid": time_in_voice}
    
    save_json(os.path.join("data/guilds/", str(guildID),
              "practice_sessions.json"), {}) # {"userid": [{"xp_gained":1.0, "total_time":1,"of_which_time_unmuted":1,"current_xp":10.0,"current_total_time":133.0},...]}
    save_json(os.path.join("data/guilds/", str(guildID),
              "voice_session_time.json"), {}) # {"userid": start_time}
    save_json(os.path.join("data/guilds/", str(guildID),
              "voice_xp.json"), {}) # {"userid": {"xp": xp, ... etc}}}
    save_json(os.path.join("data/guilds/", str(guildID),
              "events.json"), {}) # {"event_id" :{"timestamp": timestamp, "type": "message", "xp": xp, "userid": userid}, ... etc}
    
    


def change_settings_for_guild(guild, setting, value):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)
    settings = load_json(os.path.join("data/guilds/", str(guildID),"settings.json"))
    settings[setting] = value
    save_json(os.path.join("data/guilds/", str(guildID),"settings.json"), settings)

def get_settings_for_guild(guild):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)
    settings = load_json(os.path.join("data/guilds/", str(guildID),"settings.json"))
    return settings



def log_practice_session(guild, userID, session_data):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)

    practice_sessions = load_json(os.path.join("data/guilds/", str(guildID),"practice_sessions.json"))
    if not str(userID) in practice_sessions:
        practice_sessions[str(userID)] = []
    practice_sessions[str(userID)].append({
        "xp_gained":session_data["xp_gained"], 
        "total_time":time.time()-session_data["start_time"],
        "of_which_time_unmuted":session_data["time_unmuted"],
        "current_xp":get_voice_xp(guild, userID),
        "current_total_time":get_voice_time(guild, userID),
        "start_time":session_data["start_time"],
        })
    save_json(os.path.join("data/guilds/", str(guildID),"practice_sessions.json"), practice_sessions)


def get_active_voice_sessions(guild):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)
    voice_session_time = load_json(os.path.join("data/guilds/", str(guildID),"voice_session_time.json"))
    return voice_session_time # {"userid": start_time, ... etc}

def set_voice_session_start(guild, userID, start):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)
    voice_session_time = load_json(os.path.join("data/guilds/", str(guildID),"voice_session_time.json"))
    voice_session_time[str(userID)] = {"start_time":start, "xp_gained":0.0, "time_unmuted":0.0}
    save_json(os.path.join("data/guilds/", str(guildID),"voice_session_time.json"), voice_session_time)


def remove_voice_session_list(guild, list_of_userIDs): # more efficient than calling remove_voice_session for each user
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)
    voice_session_time = load_json(os.path.join("data/guilds/", str(guildID),"voice_session_time.json"))
    for userID in list_of_userIDs:
        # add to logs
        log_practice_session(guild, userID, voice_session_time[str(userID)])
        del voice_session_time[str(userID)]
    save_json(os.path.join("data/guilds/", str(guildID),"voice_session_time.json"), voice_session_time)

def remove_voice_session(guild, userID):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)
    voice_session_time = load_json(os.path.join("data/guilds/", str(guildID),"voice_session_time.json"))
    del voice_session_time[str(userID)]
    save_json(os.path.join("data/guilds/", str(guildID),"voice_session_time.json"), voice_session_time)


def add_voice_xp(guild, userID, xp):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)
    
    voicexp = load_json(os.path.join("data/guilds/", str(guildID),"voice_xp.json"))
    if not str(userID) in voicexp:
        voicexp[str(userID)] = 0
    voicexp[str(userID)] += xp
    save_json(os.path.join("data/guilds/", str(guildID),"voice_xp.json"), voicexp)


def get_voice_xp(guild, userID):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)
    voicexp = load_json(os.path.join("data/guilds/", str(guildID),"voice_xp.json"))
    if not str(userID) in voicexp:
        return 0
    return voicexp[str(userID)]

def add_voice_time(guild, userID, time):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)

    voice_times = load_json(os.path.join("data/guilds/", str(guildID),"voice_times.json"))
    if not str(userID) in voice_times:
        voice_times[str(userID)] = 0.0
    voice_times[str(userID)] += time
    save_json(os.path.join("data/guilds/", str(guildID),"voice_times.json"), voice_times)

def get_voice_time(guild, userID):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)

    voice_times = load_json(os.path.join("data/guilds/", str(guildID),"voice_times.json"))
    if not str(userID) in voice_times:
        return 0.0
    return voice_times[str(userID)]

def xp_rate(session_time):
    if session_time < 60*5:
        return session_time / (60*5) # 0..1
    if session_time < 60*60*2.5:
        return 1
    return 2**(-((session_time-60*60*2.5)/3600)*2)


def make_embed(title="", description="", color=0x00ff00, footer=None, image=None, thumbnail=None, author=None,
               fields=None, top_icon_url="", bottom_icon_url="", url=""):
    embed = nextcord.Embed(title=title, description=description, color=color, url=url)
    if footer: embed.set_footer(text=footer, icon_url=bottom_icon_url)
    if image:  embed.set_image(url=image)
    if thumbnail: embed.set_thumbnail(url=thumbnail)
    if top_icon_url == None:
        top_icon_url = ""
    if bottom_icon_url == None:
        bottom_icon_url = ""
    if author: embed.set_author(name=author, icon_url=top_icon_url)
    if fields:
        for field in fields:
            embed.add_field(name=field[0], value=field[1], inline=field[2])
    return embed

def get_pretty_voice_leaderboard(guild,sort,start,end):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)
    if sort == "xp":
        voicexps = load_json(os.path.join("data/guilds/", str(guildID),"voice_xp.json"))
        voicexps = [(struserid, int(userxp)) for struserid, userxp in voicexps.items()]
        voicexps.sort(key=lambda x: x[1], reverse=True) # sort by xp
        voicexps = voicexps[start:end]

        if len(voicexps) == 0:
            return "**The leaderboard is empty...**"
        
        numbers = [("🥇🥈🥉"[i] if i <= 2 else f"**#{i+1}**" ) for i in range(start,start+len(voicexps))]
        names = [f"<@{userid}>\n<:spacer:1156978605759418388>Exp `{int(xp)}`" for userid, xp in voicexps]
        return "\n".join([f"{numbers[i]} → {names[i]}" for i in range(len(numbers))])
    if sort == "time":
        voicetimes = load_json(os.path.join("data/guilds/", str(guildID),"voice_times.json"))
        voicetimes = [(struserid, int(usertime)) for struserid, usertime in voicetimes.items()]
        voicetimes.sort(key=lambda x: x[1], reverse=True) # sort by time
        voicetimes = voicetimes[start:end]

        if len(voicetimes) == 0:
            return "**The leaderboard is empty...**"
        
        numbers = [("🥇🥈🥉"[i] if i <= 2 else f"**#{i+1}**" ) for i in range(start,start+len(voicetimes))]
        names = [f"<@{userid}>\n<:spacer:1156978605759418388>Time `{format_time_large(time)}`" for userid, time in voicetimes]
        return "\n".join([f"{numbers[i]} → {names[i]}" for i in range(len(numbers))])
    if sort == "latest":
        practice_sessions = load_json(os.path.join("data/guilds/", str(guildID),"practice_sessions.json"))
        practice_sessions = [(struserid, int(session[-1]["start_time"])) for struserid, session in practice_sessions.items()]
        practice_sessions.sort(key=lambda x: x[1], reverse=True)
        practice_sessions = practice_sessions[start:end]

        if len(practice_sessions) == 0:
            return "**The leaderboard is empty...**"
        
        numbers = [("🥇🥈🥉"[i] if i <= 2 else f"**#{i+1}**" ) for i in range(start,start+len(practice_sessions))]
        names = [f"<@{userid}>\n<:spacer:1156978605759418388>Time <t:{int(session_time)}:R>" for userid, session_time in practice_sessions]
        return "\n".join([f"{numbers[i]} → {names[i]}" for i in range(len(numbers))])


def get_pretty_user_session_history(guild,userID,start,end):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)
    currently_active_sessions = get_active_voice_sessions(guild)
    is_in_vc = str(userID) in currently_active_sessions
        
    practice_sessions = load_json(os.path.join("data/guilds/", str(guildID),"practice_sessions.json"))
    if not str(userID) in practice_sessions and not is_in_vc:
        return "**No practice sessions found...**"
    if len(practice_sessions[str(userID)]) == 0 and not is_in_vc:
        return "**No practice sessions found...**"
    practice_sessions = practice_sessions[str(userID)][start:end]

    numbers = [f"**#{i+1}**" for i in range(start,start+len(practice_sessions))]
    names = [(f"<t:{int(session['start_time'])}:D>"+\
            f"\n<:spacer:1156978605759418388>Session time: `{format_time(session['total_time'])}`, time unmuted: `{format_time(session['of_which_time_unmuted'])}`"+\
            f"\n<:spacer:1156978605759418388>Exp gained: `{int(session['xp_gained'])}` (current total: `{int(session['current_xp'])})`\n") for session in practice_sessions]
    
    numbers.reverse()
    names.reverse()

# "315851790967111680": {
#     "start_time": 1696447047.2198226,
#     "xp_gained": 171.9957894349813,
#     "time_unmuted": 0.0
#   }
    prefix = ""
    if is_in_vc:
        current_xp = int(get_voice_xp(guild, userID))
        prefix = f"**Current session** → <t:{int(currently_active_sessions[str(userID)]['start_time'])}:D>"+\
            f"\n<:spacer:1156978605759418388>Session time: `{format_time(time.time()-currently_active_sessions[str(userID)]['start_time'])}`, time unmuted: `{format_time(currently_active_sessions[str(userID)]['time_unmuted'])}`"+\
            f"\n<:spacer:1156978605759418388>Exp gained: `{int(currently_active_sessions[str(userID)]['xp_gained'])}` (current total: `{current_xp})`\n\n"

    return prefix +"\n".join([f"{numbers[i]} → {names[i]}" for i in range(len(numbers))])

def remove_user_sessions(guild, userID, index_1, index_2):
    sessions = load_json(os.path.join("data/guilds/", str(guild.id),"practice_sessions.json"))
    if not str(userID) in sessions:
        return 0.0, 0.0,0
    if len(sessions[str(userID)]) == 0:
        return 0.0, 0.0,0
    
    amount = index_2 - index_1 + 1
    removing = sessions[str(userID)][index_1-1:index_2]
    xp_removed = sum([session["xp_gained"] for session in removing])
    time_removed = sum([session["total_time"] for session in removing])

    for session in sessions[str(userID)][index_2:]: # update the xp and time of the sessions after the removed ones
        session["current_xp"] -= xp_removed
        session["current_total_time"] -= time_removed

    del sessions[str(userID)][index_1-1:index_2] # this is the line that actually removes the sessions
    save_json(os.path.join("data/guilds/", str(guild.id),"practice_sessions.json"), sessions)
    voicexp = load_json(os.path.join("data/guilds/", str(guild.id),"voice_xp.json"))
    voicexp[str(userID)] -= xp_removed
    save_json(os.path.join("data/guilds/", str(guild.id),"voice_xp.json"), voicexp)
    voice_times = load_json(os.path.join("data/guilds/", str(guild.id),"voice_times.json"))
    voice_times[str(userID)] -= time_removed
    save_json(os.path.join("data/guilds/", str(guild.id),"voice_times.json"), voice_times)


    return xp_removed, time_removed, amount


def get_events_for_guild(guild):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)

    events = load_json(os.path.join("data/guilds/", str(guildID),"events.json"))
    return events

def parse_time(unparsed:str):
    try:
        return float(unparsed),datetime.datetime.fromtimestamp(float(unparsed)).isoformat(timespec="seconds")  # unix timestamp
    except:
        pass
    try:
        return datetime.datetime.fromisoformat(unparsed).timestamp(), unparsed # iso8601
    except:
        pass
    raise ValueError("Invalid time format. Use ISO8601 format \"YYYY-MM-DDTHH:MM:SS+diff\" or unix timestamp")


def create_vc_room_event(guild,name,description,roleID,channelID,unparsed_time,author_id,edit_event_id=""):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)
    isotime = ""
    try:
        timestamp,isotime = parse_time(unparsed_time)
    except ValueError:
        return ("Invalid time format. Use ISO8601 format \"YYYY-MM-DDTHH:MM:SS+diff\" or unix timestamp",0,"")
    
    if not edit_event_id:
        offset = 0
        while True:
            event_id = str(guildID)[0:3] +"_"+ str((int(time.time())%10000)+offset)[-3:] +"_"+ str(author_id)[0:3]
            if not event_id in events:
                break
            offset += 1
    else:
        event_id = edit_event_id	

    events = load_json(os.path.join("data/guilds/", str(guildID),"events.json"))
    events[event_id] = {
        "name":name,
        "description":description,
        "roleID":roleID,
        "roleName": guild.get_role(roleID).name if roleID else None,
        "channelID":channelID,
        "channelName": guild.get_channel(channelID).name if channelID else None,
        "time":timestamp,
        "participants":{},
        "author_id":author_id, 
        "event_id":event_id,
        "iso_time":isotime
        }
    save_json(os.path.join("data/guilds/", str(guildID),"events.json"), events)


    return ("OK",timestamp,event_id)


def view_event_pretty(guild,event_id):
    guildID = guild.id
    events = load_json(os.path.join("data/guilds/", str(guildID),"events.json"))
    if not "_" in event_id and len(event_id) == 9:
        event_id = event_id[0:3] +"_"+ event_id[3:6] +"_"+ event_id[6:9]

    if not event_id in events:
        return "**Event not found...**"
    event = events[event_id]
    participants = event["participants"]
    if len(participants) == 0:
        participants_str = "None yet..."
    elif len(participants) == 1:
        participants_str = f"<@{participants[0]['id']}>"
    else:
        suffix = f" and <@{participants[-1]['id']}>"
        participants_str = ", ".join([f"<@{participant['id']}>" for participant in participants[:-1]]) + suffix
    fields = []
    fields.append(["Name", event["name"], False])
    fields.append(["Description", event["description"], False])
    fields.append(["When", f"<t:{int(event['time'])}:R>", False]) 
    fields.append(["Registered Participants", participants_str, False])
    fields.append(["Channel to post in", f"<#{event['channelID']}>", False])
    fields.append(["Role to ping", f"<@&{event['roleID']}>" if event['roleID'] else "None", False])
    fields.append(["Event created by", f"<@{event['author_id']}>", False])
    return make_embed(title=guild.name, 
                      author="Event Info",
                      fields=fields, 
                      description=f"Event with the id: `{event_id}`", 
                      color=0xfceaa8, 
                      thumbnail=guild.icon.url if guild.icon else None,
                    )

def list_vc_room_events(guild,start,end, future=True):
    guildID = guild.id
    events = load_json(os.path.join("data/guilds/", str(guildID),"events.json"))
    events=list(events.items())    
    if len(events) == 0:
        return "**No events found...**"
    
    events.sort(key=lambda x: x[1]["time"])
    if future:
        events = [(event_id, event) for event_id, event in events if event["time"] > time.time()]

    events = events[start:end]
    if len(events) == 0:
        return "**No future events found...**"
    
    participants_strs = {}
    max_listed_participants = 5
    for event_id, event in events:
        participants = event["participants"]
        if len(participants) == 0:
            participants_strs[event_id] = "None yet..."
        elif len(participants) == 1:
            participants_strs[event_id] = f"<@{list(participants.keys())[0]}>"
        elif len(participants) > max_listed_participants:
            suffix = f" + {len(participants)-max_listed_participants} more..."
            participants_strs[event_id] = ", ".join([f"<@{participant}>" for participant in list(participants.keys())[:max_listed_participants]]) + suffix
        else:
            suffix = f" and <@{list(participants.keys())[-1]}>"
            participants_strs[event_id] = ", ".join([f"<@{participant}>" for participant in list(participants.keys())[:-1]]) + suffix

    numbers = [f"**#{i+1}**" for i in range(start,start+len(events))]
    names = [f"Event ID: `{event_id}`. <t:{int(event['time'])}:R>\n<:spacer:1156978605759418388>Name: {event['name']}\n<:spacer:1156978605759418388>Desc: {event['description']}\n<:spacer:1156978605759418388>Registered Participants: {participants_strs[event_id]}" for event_id, event in events]
    
    numbers.reverse()
    names.reverse()
    return "\n".join([f"{numbers[i]} → {names[i]}" for i in range(len(numbers))])



class CreateEventModal(nextcord.ui.Modal, ):
    def __init__(self,
                 title, 
                 default_name = "", 
                 default_description = "", 
                 default_role = "", 
                 default_channel = "",
                 default_iso_time = "",
                 event_id_edit = ""):
        super().__init__(title, timeout=60*30)
        self.event_id_edit = event_id_edit
        self.field1 = nextcord.ui.TextInput(
            label="Event Name", 
            placeholder="Event Name", 
            min_length=1, 
            max_length=100,
            default_value=default_name,
            style=nextcord.TextInputStyle.short,
        )
        self.field2 = nextcord.ui.TextInput(
            label="Event Description", 
            placeholder="Event Description", 
            min_length=1, max_length=1800,
            default_value=default_description,
            style=nextcord.TextInputStyle.paragraph
        )
        # which role to ping for the event
        self.field3 = nextcord.ui.TextInput( 
            label="Which role to ping?",
            placeholder="Role name or ID",
            min_length=1,
            max_length=100,
            required=False,
            default_value=default_role,
            style=nextcord.TextInputStyle.short,
        )
        # which channel to post in
        self.field4 = nextcord.ui.TextInput( 
            label="Which channel to post in?",
            placeholder="Channel name or ID",
            min_length=1,
            max_length=100,
            default_value=default_channel,
            style=nextcord.TextInputStyle.short,
        )
        self.field5 = nextcord.ui.TextInput(
            label="When? (example: \"2023-09-29T20:52:33+02:00\")", 
            # placeholder="Use ISO8601 format \"YYYY-MM-DDTHH:MM:SS+diff\" or unix timestamp.\nExample: \"2023-09-29T20:52:33+02:00\" for UTC+2, or timestamp: \"1696013553\"", 
            placeholder="Use ISO8601 format: \"2023-09-29T20:52:33+02:00\" for UTC+2, or unix timestamp: \"1696013553\"", 
            min_length=1, 
            max_length=150,
            default_value=default_iso_time if default_iso_time else (datetime.datetime.fromtimestamp(time.time()+60*60*24).isoformat(timespec="seconds")),
            style=nextcord.TextInputStyle.paragraph,
        )

        self.add_item(self.field1)
        self.add_item(self.field2)
        self.add_item(self.field3)
        self.add_item(self.field4)
        self.add_item(self.field5)

    async def callback(self, interaction: Interaction) -> None:
        channelnameOrID = self.field4.value
        if channelnameOrID.startswith("#"): channelnameOrID = channelnameOrID[1:]
        if channelnameOrID.startswith("<#") and channelnameOrID.endswith(">"):
            channelnameOrID = (channelnameOrID[2:-1])
            # verify that the channel exists
        if channelnameOrID.replace(".","").isdecimal():
            channel = interaction.guild.get_channel_or_thread(int((channelnameOrID)))
            if not channel:
                await interaction.response.send_message("Invalid channel (1)", ephemeral=True)
                return
            channelID = channel.id
            if channel.type != nextcord.ChannelType.text and channel.type != nextcord.ChannelType.news:
                await interaction.response.send_message("Invalid channel. Channel must be a text channel (4)", ephemeral=True)
                return
        else:
            channels_in_guild = interaction.guild.channels
            channel = None
            channelID = None
            channels_for_testing = []

            for guildchannel in channels_in_guild: # tests all channels without case sensitivity, puts them in channels_for_testing
                if guildchannel.name.lower() == channelnameOrID.lower():
                    channels_for_testing.append(guildchannel)
            if len(channels_for_testing) == 0: # no channels found that matched
                await interaction.response.send_message("Invalid channel (2)", ephemeral=True)
                return
            if len(channels_for_testing) == 1: # one channel found that matched
                channel = channels_for_testing[0]
                channelID = channel.id
            else: # this means len(channels_for_testing) > 1
                textchannels = [] # if there are multiple channels that matched, only text channels are considered
                for guildchannel in channels_for_testing:
                    if guildchannel.type == nextcord.ChannelType.text or guildchannel.type == nextcord.ChannelType.news:
                        textchannels.append(guildchannel)
                if len(textchannels) == 0: # if no text channels matched
                    await interaction.response.send_message("Invalid channel. Channel must be a text channel (3)", ephemeral=True)
                    return
                if len(textchannels) == 1: # if there is only one text channel that matched
                    channel = textchannels[0]
                    channelID = channel.id
                elif len(textchannels) > 1: # if there are multiple text channels that matched
                    # test for case sensitivity
                    for guildchannel in textchannels:
                        if guildchannel.name == channelnameOrID:
                            channelID = guildchannel.id
                            channel = guildchannel
                            break
                    if not channelID:
                        # if no channel matched, use the first one
                        channel = textchannels[0]
                        channelID = channel.id
                    
            if not channelID:
                await interaction.response.send_message("Invalid channel (2)", ephemeral=True)
                return
            if channel.type != nextcord.ChannelType.text and channel.type != nextcord.ChannelType.news:
                await interaction.response.send_message("Invalid channel. Channel must be a text channel (3)", ephemeral=True)

        
        
        rolenameOrID = self.field3.value
        if rolenameOrID != "":
        
            if rolenameOrID.startswith("<@&") and rolenameOrID.endswith(">"):
                rolenameOrID = (rolenameOrID[3:-1])
                # verify that the role exists
            if rolenameOrID.replace(".","").isdecimal():
                role = interaction.guild.get_role(int((rolenameOrID)))
                if not role:
                    await interaction.response.send_message("Invalid role (1)", ephemeral=True)
                    return
                roleID = role.id
            else:
                roles_in_guild = interaction.guild.roles
                role = None
                roleID = None
                for role in roles_in_guild:
                    if role.name.lower() == rolenameOrID.lower():
                        roleID = role.id
                        break
                if not roleID:
                    await interaction.response.send_message("Invalid role (2)", ephemeral=True)
                    return
        else:
            roleID = 0

        result = create_vc_room_event(interaction.guild, self.field1.value, self.field2.value, roleID, channelID, self.field5.value,interaction.user.id, edit_event_id=self.event_id_edit)
        if not self.event_id_edit:
            if result[0] != "OK":
                await interaction.response.send_message(result[0], ephemeral=True,)
                return
            await interaction.send(f"Event created for <t:{int(result[1])}:F>, named \"{self.field1.value}\". eventID is `{result[2]}`", ephemeral=False, )
        else:
            if result[0] != "OK":
                await interaction.response.send_message(result[0], ephemeral=True,)
                return
            await interaction.send(f"Event edited for <t:{int(result[1])}:F>, named \"{self.field1.value}\". eventID is `{result[2]}`", ephemeral=False, )
        return
    






class ParticipateInEventModal(nextcord.ui.Modal, ):
    def __init__(self,
                 title, 
                 event_id,
                 default_topic = "", 
                    ):
        super().__init__(title, timeout=60*30)
        self.field1 = nextcord.ui.TextInput(
            label="Event ID", 
            placeholder="111_222_333", 
            min_length=1, 
            max_length=100,
            default_value=event_id,
            style=nextcord.TextInputStyle.short,
        )
        self.field2 = nextcord.ui.TextInput(
            label="What are you playing?", 
            placeholder="rach g minor prelude", 
            min_length=1, max_length=1800,
            default_value=default_topic,
            style=nextcord.TextInputStyle.paragraph
        )

        self.add_item(self.field1)
        self.add_item(self.field2)
    async def callback(self, interaction: Interaction) -> None:




        events = load_json(os.path.join("data/guilds/", str(interaction.guild.id),"events.json"))
        if not "_" in self.field1.value and len(self.field1.value) == 9:
            self.field1.value = self.field1.value[0:3] +"_"+ self.field1.value[3:6] +"_"+ self.field1.value[6:9]

        if not self.field1.value in events:
            await interaction.response.send_message("Event not found", ephemeral=True)
            return
        
        result = participate_add_to_event(interaction.guild, self.field1.value, self.field2.value, interaction.user.id)
        if result[0] != "OK":
            await interaction.response.send_message(result[0], ephemeral=True,)
            return
        await interaction.send(f"You are participating in the event named: {result[1]}", ephemeral=False, )
        return
    
def participate_add_to_event(guild, event_id, topic, user_id):
    guildID = guild.id
    events = load_json(os.path.join("data/guilds/", str(guildID),"events.json"))
    if not "_" in event_id and len(event_id) == 9:
        event_id = event_id[0:3] +"_"+ event_id[3:6] +"_"+ event_id[6:9]

    if not event_id in events:
        return ("Event not found...","0")
    event = events[event_id]
    if event["time"] < time.time():
        return ("Event has already passed...","0")
    
    str_user_id = str(user_id)
    if str_user_id in event["participants"]:
        event["participants"][str_user_id]["topic"] = topic
    else:
        event["participants"][str_user_id] = {"topic":topic}
    save_json(os.path.join("data/guilds/", str(guildID),"events.json"), events)
    return ("OK",event["name"])


def get_pretty_commands_list():
    fields = [("**Practice time logging**", 
               "</voiceleaderboard:1159116918637211648> → Shows the voice leaderboard.\n"+\
               "</viewsessions:1159117001512472586> → Shows the practice session history of yourself or another user.\n"+\
               "</removesessions:1159116920214274068> → Removes practice sessions of yourself or another user. Removal of other user's sessions requires privileges\n"               
               ,False),
              ("**Events**", 
               "</participate:1159188414646718464> → Participate in an event.\n"+\
               "</viewevent:1159116917253083236> → View details on an event.\n"+\
               "</listfutureevents:1159116914795221093> → List future events.\n"+\
               "</listallevents:1159243978059829358> → List all events.\n"+\
               "</createevent:1159117003731255376> → Create an event.\n"+\
               "</editevent:1159117000350650398> → Edit/change the specifics of an event.\n"+\
               "</copyevent:1159127602485792909> → Copy/duplicate an event.\n"
               
               ,False),
               ("**Misc**",
                "</help:1159218778018689095> → Shows this message.\n"+\
                "</unixtimestamp:1159117002594590776> → Converts date and time to unix timestamp.\n"
                
                ,False),
               ]
    return fields










if __name__ == "__main__":
    # save_json("test.json", {"cdb": "test"})
    print(load_json("test.json"))
