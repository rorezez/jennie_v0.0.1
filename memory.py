# memory.py

PROMPTS = {
    'default_prompt': 'asisten yang sangat membantu',
    'help_prompt': 'Ini adalah prompt bantuan.',
    'error_prompt': 'Ini adalah prompt kesalahan.'
    # Anda bisa menambahkan prompt lainnya di sini
}

def get_prompt(prompt_id):
    return PROMPTS.get(prompt_id, '')
