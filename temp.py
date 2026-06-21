from src.chat_bot import chatBot

bot = chatBot()

while True:
    q = input("question: ")

    print("\n", end="")

    response = ""
    for chunk in bot.ask(q, "samael"):
        print(chunk, end="", flush=True)
        response += chunk

    print("\n")