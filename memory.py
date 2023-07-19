# memory.py

PROMPTS = {
    'default_prompt': 'kamu adalah fans dari rapper korea sik k dan kamu akan mejawab segala pertanyaan dan menghubungkan dengan sik k',
    'help_prompt': 'Ini adalah prompt bantuan.',
    'error_prompt': 'Ini adalah prompt kesalahan.'
    # Anda bisa menambahkan prompt lainnya di sini
}

def get_prompt(prompt_id):
    return PROMPTS.get(prompt_id, '')
