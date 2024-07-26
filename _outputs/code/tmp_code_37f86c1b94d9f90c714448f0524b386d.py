import wikipedia

def get_wiki_summary(name):
  """Fetches a short summary from Wikipedia for a given name.

  Args:
    name: The name of the person or topic to search for.

  Returns:
    A string containing the summary, or an error message if not found.
  """
  try:
    # Search for the page using the exact name first
    return wikipedia.summary(name, sentences=3)
  except wikipedia.exceptions.PageError:
    try:
      # If not found, search for a disambiguated version
      suggestion = wikipedia.suggest(name)
      if suggestion:
        return wikipedia.summary(suggestion, sentences=3)
      else:
        return f"Error: Could not find a Wikipedia page for '{name}'"
    except wikipedia.exceptions.DisambiguationError as e:
      return f"Error: Multiple pages match '{name}'. Please be more specific."
  except wikipedia.exceptions.DisambiguationError as e:
    return f"Error: Multiple pages match '{name}'. Please be more specific."

# Gather information about each participant
participants = ["Harry Potter", "Iron Man", "Darth Vader", "Alan Turing", "Albert Einstein", "Genghis Khan"]
participant_info = {}

for name in participants:
  participant_info[name] = get_wiki_summary(name)

# Prepare the output
print("Welcome to our podcast! Today's topic is Democracy, and we have a very special guest list:")
for name, info in participant_info.items():
  print(f"\n**{name}:**\n{info}")

print("\nLet's hear what our guests have to say about this complex and fascinating topic!") 