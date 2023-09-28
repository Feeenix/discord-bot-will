from xp_related import *



@client.slash_command(name="settings",description="run this command without args to see current settings, or with args to change them",
)
async def test(interaction: Interaction,  
# midifile_attachment:nextcord.Attachment = SlashOption(description="Midi file to be converted.", required = True, name="midifile_attachment"),
# longnote:float = SlashOption(description="Sustain factor. Higher values = longer sustains. Defaults to 5", required = False,default=5, name="longnote", choices={"0": 0, "1": 1, "2": 2,"3" : 3, "4" : 4, "5 (Default)": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10 }),
# timemultiply:float = SlashOption(description="Time factor. Higher values = longer songs. Defaults to 1.0", required = False,default=1.0, name="timemultiply", min_value=0.1, max_value=10.0),
# spawnproof:int = SlashOption(description="Toggles blocking monster spawning. Defaults to false", required = False,default=False, name="spawnproof", choices = {"true": True, "false (Default)": False}),
# tracks:int = SlashOption(description="*EXPERIMENTAL!* The number of tracks to spread notes between. Default is 14", required = False,default=14, name="tracks", choices = {"1": 1, "2": 2, "3": 3,"4" : 4, "5" : 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "11": 11, "12": 12, "13": 13, "14 (Default)": 14, "15": 15, "16": 16}),
# mp3:int = SlashOption(description="*EXPERIMENTAL!* Export as audio instead of litematic. Defaults to litematic", required = False,default=False, name="audio", choices = {"Audio file": True, "Litematica file (Default)": False}),


setting:str = SlashOption(description="The name of the setting you want to change", required = False, default="", name="setting", choices={"voicexp": "voicexp", "messagexp": "messagexp"}),
value:int = SlashOption(description="the value of the setting, in case of booleans then 0 means false and 1 means true", required = False,default=0, name="value"),
):
    # interaction.response.defer() # let the user know we're working on it
    await interaction.response.send_message("working on it")
    return



#, default_member_permissions=nextcord.Permissions(manage_channels=True)
@client.slash_command(name="voiceleaderboard",description="display the current voice leaderboard"
)
async def display_leaderboard(interaction: Interaction,
pagenum:int = SlashOption(description="Which page number to display", required = False,default=1, name="page"),
sort:str = SlashOption(description="How to sort the leaderboard", required = False,default="xp", name="sort", choices={"xp": "xp", "time": "time", "latest": "latest"}),
                              ):
    voice_xps = load_json(os.path.join("data/guilds/", str(interaction.guild.id),"voice_xp.json"))
    len_voice_xps = len(voice_xps)
    pagesize = 10
    pagenum = max(1,min(pagenum,math.ceil(len_voice_xps/pagesize)))
    embed = make_embed(
        title=interaction.guild.name, 
        description="This is the current practice room leaderboard.\nWho is the most hard working?\n\n"+get_pretty_voice_leaderboard(interaction.guild,sort,(pagenum-1)*pagesize,(pagenum-1)*pagesize+pagesize) + (f"\n\nPage {pagenum}/{math.ceil(len_voice_xps/pagesize)}" if len_voice_xps > pagesize else ""),
        color=0xfceaa8,
        author="Practice Room Leaderboard",
        thumbnail=interaction.guild.icon if interaction.guild.icon else None,
        )
    
    # nextcord.Embed(title="Voice Leaderboard", description="this is the current voice leaderboard")
    

    await interaction.response.send_message("", embed=embed)
    return


#, default_member_permissions=nextcord.Permissions(manage_channels=True)
@client.slash_command(name="viewsessions",description="display a person's previous practice room sessions"
)
async def display_leaderboard(interaction: Interaction,
                              user:nextcord.Member = SlashOption(description="Which user to display", required = False,default=None, name="user"),
pagenum:int = SlashOption(description="Which page number to display", required = False,default=1, name="page"),
                              ):
    sessions = load_json(os.path.join("data/guilds/", str(interaction.guild.id),"practice_sessions.json"))
    user = user if user else interaction.user
    userID = user.id
    if str(userID) not in sessions:
        sessions[str(userID)] = []
    len_user_sessions = len(sessions[str(userID)])
    pagesize = 10
    pagenum = max(1,min(pagenum,math.ceil(len_user_sessions/pagesize)))
    embed = make_embed(
        title=f"{user.global_name}'s practice sessions.", 
        description=get_pretty_user_session_history(interaction.guild, userID,(pagenum-1)*pagesize,(pagenum-1)*pagesize+pagesize) + (f"\n\nPage {pagenum}/{math.ceil(len_user_sessions/pagesize)}" if len_user_sessions > pagesize else ""),
        color=0xfceaa8,
        thumbnail=user.avatar,
        )
    
    # nextcord.Embed(title="Voice Leaderboard", description="this is the current voice leaderboard")
    

    await interaction.response.send_message("", embed=embed)
    return



@client.slash_command(name="removesessions",description="revert a user's stats to a previous state using the session indices", 
)
async def remove_sessions(interaction: Interaction,
                              user:nextcord.Member = SlashOption(description="Which user to display", required = True,default=None, name="user"),
                              session_index_1:int = SlashOption(description="Remove sessions from this index (inclusive)", required = True,default=None, name="session_index_min"),
                              session_index_2:int = SlashOption(description="remove sessions to this index (inclusive)", required = False,default=None, name="session_index_max"),
                              ):
    if user.id != interaction.user.id:
        if not interaction.user.guild_permissions.manage_channels or interaction.user.id != owner_id:
            await interaction.response.send_message("You can only remove your own sessions", ephemeral=True)
            return

    user = user if user else interaction.user
    userID = user.id
    if session_index_2 is None:
        session_index_1 = max(1,session_index_1)
        session_index_2 = session_index_1
    else:
        session_index_1 = max(1,session_index_1)
        session_index_2 = max(1,session_index_2)
        session_index_1, session_index_2 = min(session_index_1, session_index_2), max(session_index_1, session_index_2)

    
    xp_removed, time_removed,sessions_removed = remove_user_sessions(interaction.guild, userID, session_index_1, session_index_2)
    embed = make_embed(
        title=f"{user.global_name}'s practice sessions.", 
        description=f"Removed `{sessions_removed}` sessions (`{session_index_1}"+(f"-{session_index_1+sessions_removed-1}" if sessions_removed != 1 else "")+f"`), `{xp_removed:.0f}` xp and `{format_time(time_removed)}` of practice time.",
        color=0xfceaa8,
        thumbnail=user.avatar,
        )
    
    

    await interaction.response.send_message("", embed=embed)

    return



@client.slash_command(name="unixtimestamp",description="make a unix timestamp from a date and time", 
)
async def unix_timestamp(interaction: Interaction,
                                date:str = SlashOption(description="date in the format YYYY-MM-DD", required = True,default=None, name="date"),
                                time:str = SlashOption(description="time in the format HH:MM", required = True,default=None, name="time"),
                                hoursystem:str = SlashOption(description="AM or PM or 24 hour system", required = False,default="24", name="hoursystem", choices={"AM": "AM", "PM": "PM", "24": "24"}),
                                timezone:int = SlashOption(description="timezone offset in hours, for UTC+4 write 4", required = False,default=0, name="timezone"),
                                ):
    if hoursystem == "24":
        hoursystem = ""
    else:
        hoursystem = hoursystem.lower()
    try:
        if hoursystem == "":
            timestamp = datetime.datetime.strptime(date+time, "%Y-%m-%d%H:%M")
        else:
            timestamp = datetime.datetime.strptime(date+time+hoursystem, "%Y-%m-%d%I:%M%p")
    except:
        await interaction.response.send_message("Invalid date or time", ephemeral=True)
        return
    timestamp = timestamp.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=timezone)))
    await interaction.response.send_message(f"Unix timestamp: `{timestamp.timestamp()}`")
    return


