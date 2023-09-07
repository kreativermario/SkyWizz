import time

import skywizz


def __init__():
    print('\n' * 100)
    print("""
         _____  __             _       __ _                
      / ___/ / /__ __  __   | |     / /(_)____ ____      
      \\__ \\ / //_// / / /   | | /| / // //_  //_  /      
     ___/ // ,<  / /_/ /    | |/ |/ // /  / /_ / /_      
    /____//_/|_| \\__, /     |__/|__//_/  /___//___/      
                /____/                      
        NOTE: You can change the settings later in .env             
    """)
    input_bot_token = input("Discord bot token: ")
    input_bot_prefix = input("Command Prefix: ")
    input_bot_status = input("Bot status: (Playing xxx) ")
    # TODO implement mySQL
    try:
        config = f"""CONFIG_VERSION={skywizz.config_version()}
BOT_TOKEN={input_bot_token}
BOT_PREFIX={input_bot_prefix}
BOT_STATUS={input_bot_status}
"""
        # TODO fix writing .env file first before starting bot. Bug
        with open('./.env', 'w') as env_file:
            env_file.write(config)
            env_file.flush()  # Flush changes to the file immediately
        print("\n[*] Successfully created .env file!")
        print("SkyWizz.py setup complete! Starting bot in 5 seconds...")
        time.sleep(5)
        print('\n' * 100)
    except Exception as e:
        print("\n[!] An error occurred when creating config file.\n" + str(e))
        quit()
