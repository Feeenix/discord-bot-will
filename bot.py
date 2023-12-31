from background_loop import *





@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await client.change_presence(activity=nextcord.Game(name="with Joe"))


def main():




    task_queue = []#(timestamp, func, args, kwargs, is_async)
    background_loop = threading.Thread(target=start_background_loop, args=(task_queue,))
    background_loop.start()

    voice_xp_thread = threading.Thread(target=voice_xp)
    voice_xp_thread.start()

    event_posting_loop_thread = threading.Thread(target=event_posting_loop)
    event_posting_loop_thread.start()









    with open('token.txt', 'r') as f:
        token = f.read()
    client.run(token)


if __name__ == '__main__':
    main()