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
              "events.json"), []) # [{"timestamp": timestamp, "type": "message", "xp": xp, "userid": userid}, ... etc]
    
    


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

    practice_sessions = load_json(os.path.join("data/guilds/", str(guildID),"practice_sessions.json"))
    if not str(userID) in practice_sessions:
        return "**No practice sessions found...**"
    if len(practice_sessions[str(userID)]) == 0:
        return "**No practice sessions found...**"
    practice_sessions = practice_sessions[str(userID)][start:end]

    numbers = [f"**#{i+1}**" for i in range(start,start+len(practice_sessions))]
    names = [f"<t:{int(session['start_time'])}:D>\n<:spacer:1156978605759418388>Session time: `{format_time(session['total_time'])}`, time unmuted: `{format_time(session['of_which_time_unmuted'])}`\n<:spacer:1156978605759418388>Exp gained: `{int(session['xp_gained'])}` (current total: `{int(session['current_xp'])})`\n" for session in practice_sessions]
    
    numbers.reverse()
    names.reverse()
    return "\n".join([f"{numbers[i]} → {names[i]}" for i in range(len(numbers))])

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
        return float(unparsed) # unix timestamp
    except:
        pass
    try:
        return datetime.datetime.fromisoformat(unparsed).timestamp()
    except:
        pass
    raise ValueError("Invalid time format. Use ISO8601 format \"YYYY-MM-DDTHH:MM:SS+diff\" or unix timestamp")


def create_event(guild,name,description,roleID,channelID,unparsed_time,author_id):
    guildID = guild.id
    # if not os.path.exists(os.path.join("data/guilds/", str(guildID))):
    #     initialize_guild(guild)

    try:
        timestamp = parse_time(unparsed_time)
    except ValueError:
        return ("Invalid time format. Use ISO8601 format \"YYYY-MM-DDTHH:MM:SS+diff\" or unix timestamp",0)
    
    events = load_json(os.path.join("data/guilds/", str(guildID),"events.json"))
    events.append({"name":name,"description":description,"roleID":roleID,"channelID":channelID,"time":timestamp,"participants":[],"author_id":author_id})
    save_json(os.path.join("data/guilds/", str(guildID),"events.json"), events)


    return ("OK",timestamp)


class CreateEventModal(nextcord.ui.Modal, ):
    def __init__(self,title):
        super().__init__(title, timeout=60*30)
        self.field1 = nextcord.ui.TextInput(
            label="Event Name", 
            placeholder="Event Name", 
            min_length=1, 
            max_length=100,
            style=nextcord.TextInputStyle.short,
        )
        self.field2 = nextcord.ui.TextInput(
            label="Event Description", 
            placeholder="Event Description", 
            min_length=1, max_length=1800,
            style=nextcord.TextInputStyle.paragraph
        )
        # which role to ping for the event
        self.field3 = nextcord.ui.TextInput( 
            label="Which role to ping?",
            placeholder="Role name or ID",
            min_length=1,
            max_length=100,
            required=False,
            style=nextcord.TextInputStyle.short,
        )
        # which channel to post in
        self.field4 = nextcord.ui.TextInput( 
            label="Which channel to post in?",
            placeholder="Channel name or ID",
            min_length=1,
            max_length=100,
            style=nextcord.TextInputStyle.short,
        )
        self.field5 = nextcord.ui.TextInput(
            label="When? (example: \"2023-09-29T20:52:33+02:00\")", 
            # placeholder="Use ISO8601 format \"YYYY-MM-DDTHH:MM:SS+diff\" or unix timestamp.\nExample: \"2023-09-29T20:52:33+02:00\" for UTC+2, or timestamp: \"1696013553\"", 
            placeholder="Use ISO8601 format: \"2023-09-29T20:52:33+02:00\" for UTC+2, or unix timestamp: \"1696013553\"", 
            min_length=1, 
            max_length=150,
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

            
        result = create_event(interaction.guild, self.field1.value, self.field2.value, roleID, channelID, self.field5.value,interaction.user.id)
        if result[0] != "OK":
            await interaction.response.send_message(result[0], ephemeral=True,)
            return
        await interaction.send(f"Event created for <t:{int(result[1])}:F>, named \"{self.field1.value}\"", ephemeral=False, )


if __name__ == "__main__":
    # save_json("test.json", {"cdb": "test"})
    print(load_json("test.json"))
