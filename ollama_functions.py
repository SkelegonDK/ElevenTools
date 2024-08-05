import subprocess
import time
import html


def enhance_script_with_ollama(script, enhancement_prompt="", progress_callback=None):
    """
    Enhance the given script using the Ollama llama3.1:8b model.

    :param script: The script to enhance
    :param enhancement_prompt: Optional prompt for enhancement guidance
    :param progress_callback: Optional callback function to update progress
    :return: Tuple (success, result), where success is a boolean and result is either the enhanced script or an error message
    """
    ollama_command = [
        "ollama",
        "run",
        "llama3.1:8b",
        f"""Enhance the following script for text-to-speech purposes, focusing on creating a natural and expressive output. Apply the following techniques:

1. Pauses: Use <break> tags to add natural pauses in speech. Example: "I can't believe it. <break time="1s" /> You actually did it!"

2. Emotional context: Use <emotional context> tags to convey emotions without explicitly stating them. Example: "I got the job! <emotional context="excited"> This is going to change everything. </emotional context>"

3. Emphasis: Apply strategic capitalization for important words or phrases to create vocal emphasis. Example: "This is not just ANY vacation, it's THE vacation of a lifetime!"

4. Pacing: Add descriptive language to control the speed and rhythm of speech. Example: "He took a deep breath and said slowly, 'We need to talk about what happened.'"

5. Question emphasis: Use multiple question marks for enhanced question emphasis, particularly for rhetorical or dramatic effect. Example: "Do you really think you can get away with this???"

6. Dynamic speech: Create "peaks and valleys" in sentences for more engaging speech by varying sentence structure and emphasis. Example: "The sun rose SLOWLY over the horizon. Birds began to chirp. <break time="0.5s" /> And then, SUDDENLY, the alarm clock blared."

7. Pronunciation: Use <phoneme> tags for specific or unusual pronunciations when necessary. Example: "The <phoneme alphabet="ipa" ph="ˈnjuːkliːər">nuclear</phoneme> physicist explained the concept."

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
        error_message = f"Error enhancing script: {e}\nError output: {e.stderr}"
        return False, error_message
