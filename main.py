from src.chat_bot import chatBot

bot = chatBot()

options = ["assistant", "samael", "lucifer", "council"]
persona = options[3]

while (question := input("\nAsk your question (q to quit): ")) != "q":
    bot.ask(question, persona)
    print("\nAssistant:\n")