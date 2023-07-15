# memory.py

PROMPTS = {
    'default_prompt': 'kamu adalah asisten bernama jennie yang akan menjadi pendengar yang baik, dan berbicara seperti gen z yang suka menggunakan emoji untuk mengungkapkan perasaan',
    'help_prompt': 'Ini adalah prompt bantuan.',
    'error_prompt': 'Ini adalah prompt kesalahan.'
    # Anda bisa menambahkan prompt lainnya di sini
}

def get_prompt(prompt_id):
    return PROMPTS.get(prompt_id, '')
