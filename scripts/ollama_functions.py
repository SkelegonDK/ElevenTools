import subprocess
import time
import html
from typing import Optional


def enhance_script_with_ollama(script, enhancement_prompt="", progress_callback=None):
    """
    Enhance the given script using the Ollama llama3.2:3b model.

    :param script: The script to enhance
    :param enhancement_prompt: Optional prompt for enhancement guidance
    :param progress_callback: Optional callback function to update progress
    :return: Tuple (success, result), where success is a boolean and result is either the enhanced script or an error message
    """
    ollama_command = [
        "ollama",
        "run",
        "llama3.2:3b",
        f"""# Enhance the following script for text-to-speech purposes, focusing on creating a natural and expressive output.
        
        ## Apply the following techniques:

1. **Pauses:** Use <break> tags to add natural pauses in speech. 
Example: "I can't believe it. <break time="1s" /> You actually did it!"

2. **Emotional context:** Use <emotional context> tags to convey emotions without explicitly stating them. 
Example: "I got the job! <extremely excited> This is going to change everything."

3. **Emphasis:** Apply strategic capitalization for important words or phrases to create vocal emphasis. 
Example: "This is not just ANY vacation, it's THE vacation of a lifetime!"

4. **Pacing:** Add descriptive language to control the speed and rhythm of speech. 
Example: He took a deep breath and said slowly, 'We need to talk about what happened.'
Use line breaks to control pacing and create dramatic effect. Line breaks also crearly separate the context between two different sentences.
Example: "He took a deep breath and said slowly, 'We need to talk about what happened.' <break time="1s" /> 'It's important that we address this now.'"

5. **Question emphasis:** Use multiple question marks for enhanced question emphasis, particularly for rhetorical or dramatic effect. 
Example: "Do you really think you can get away with this???"

6. **Dynamic speech:** Create "peaks and valleys" in sentences for more engaging speech by varying sentence structure and emphasis. 
Example: "The sun rose SLOWLY over the horizon. Birds began to chirp. <break time="0.5s" /> And then, SUDDENLY, the alarm clock blared."

7. **Pronunciation:** Use <phoneme> tags for specific or unusual pronunciations when necessary. 
Example: "The <phoneme alphabet="ipa" ph="ˈnjuːkliːər">nuclear</phoneme> physicist explained the concept."

When enhancing the script:
- Consider the context and tone of the script.
- Aim for a balance between expressiveness and naturalness.
- Vary your techniques. Don't rely too heavily on any single method of enhancement.
- Think about the intended audience and adjust the level of complexity accordingly.

{html.unescape(enhancement_prompt) if enhancement_prompt else 'Use the existing context to improve the script, keeping in mind the techniques and examples provided above.'}

Script to enhance:
{html.unescape(script)}

IMPORTANT: Provide ONLY the enhanced script as your response. Do not include any explanations, notes, or additional text. The enhanced script should be ready for text-to-speech synthesis and maintain the overall flow and coherence of the original text.""",
    ]

    try:
        if progress_callback:
            progress_callback(0.0)  # Always call at least once at the start

        process = subprocess.Popen(
            ollama_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        output = []
        start_time = time.time()
        while True:
            if process.poll() is not None:
                break

            if progress_callback:
                elapsed_time = time.time() - start_time
                progress_callback(
                    min(elapsed_time / 30, 0.99)
                )  # Assume max 30 seconds, cap at 99%

            time.sleep(0.1)

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, ollama_command, stderr
            )

        enhanced_script = stdout.strip()
        return True, enhanced_script
    except subprocess.CalledProcessError as e:
        error_message = f"Error occurred"
        return False, error_message


def convert_word_to_phonetic(word: str, language: str, model: str) -> Optional[str]:
    """Convert a word to its phonetic spelling in a given language using Ollama.

    Uses the Ollama LLM to convert a word into its phonetic spelling for the specified language.
    The conversion style depends on the model type selected.

    Args:
        word (str): The word to convert to phonetic spelling.
        language (str): The target language for phonetic conversion.
        model (str): The model to use for conversion ('eleven_monolingual_v1' or 'eleven_multilingual_v2').

    Returns:
        Optional[str]: The phonetic spelling of the word if successful, None if conversion fails.
            For example, "hello" might return "/həˈloʊ/".

    Raises:
        subprocess.CalledProcessError: If the Ollama command fails to execute.
    """
    multilingual_v2_prompt = f"""
    You speak perfect {language}.
    Your goal is to pronounce this word correctly and help me not sound like a tourist. 
    When I type something in English, you will translate and also give me the phonetic pronunciation.
    Only respond with the phonetic pronunciation of the word, nothing else.
    """
    model_1_prompt = f"""
    You speak perfect {language}.
    Convert the word {word} into the phonetic spelling appropriate for the {language} language
    Only respond with the phonetic spelling of the word, nothing else.
    """

    prompt = (
        model_1_prompt if model == "eleven_monolingual_v1" else multilingual_v2_prompt
    )

    ollama_command = [
        "ollama",
        "run",
        "llama3.2:3b",
        f"""You are an expert linguist and translator.

{prompt}

Word to convert: {word}
""",
    ]

    try:
        process = subprocess.Popen(
            ollama_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, ollama_command, stderr
            )

        phonetic_spelling = stdout.strip()
        return phonetic_spelling
    except subprocess.CalledProcessError as e:
        error_message = (
            f"Error converting word to phonetic: {e}\nError output: {e.stderr}"
        )
        return None


def get_ollama_response(prompt: str) -> str:
    """Get a response from Ollama using the llama3.2:3b model.

    Makes a call to the Ollama API with the provided prompt and returns the model's response.

    Args:
        prompt (str): The input prompt to send to the Ollama model.

    Returns:
        str: The response from the Ollama model, or an error message if the call fails.

    Raises:
        subprocess.CalledProcessError: If the Ollama command fails to execute.
    """
    ollama_command = [
        "ollama",
        "run",
        "llama3.2:3b",
        prompt,
    ]

    try:
        process = subprocess.Popen(
            ollama_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        stdout, stderr = process.communicate()

        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, ollama_command, stderr
            )

        return stdout.strip()
    except subprocess.CalledProcessError as e:
        error_message = f"Error getting Ollama response: {e}\nError output: {e.stderr}"
        return error_message
