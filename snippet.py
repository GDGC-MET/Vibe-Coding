user_input = input("you: ")
response =
engine.get_response(user_input)

typing_indicator(bot_name=personality_name)
print(f"{personality_name}:
{response}")
