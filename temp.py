from src.chat_bot import chatBot

bot = chatBot()

while True:
    q = input('question: ')
    resp = bot.ask(q, 'samael')
    print(f'\n{resp}\n')
