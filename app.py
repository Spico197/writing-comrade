import openai
import gradio as gr


instructions = {
    "completion": "Please help me complete the text",
    "correction": "Please help me correct mistakes in the text",
    "polishing": "Please help me polish the language and improve my writing",
    "paraphrase": "Please help me paraphrase the text",
    "translation": "Please help me translate the text",
    "freestyle": "",
}

template = "{instruction}:\n\nText: {text}"


def chat(task_type: str, text: str, api_key: str, tgt_lang: str = "") -> str:
    openai.api_key = api_key

    prompt = ""
    task_type = task_type[1:].strip().lower()
    if task_type == "freestyle":
        prompt = text
    else:
        instruction = instructions[task_type]
        if task_type == "translation":
            if tgt_lang:
                instruction += f" into {tgt_lang.strip()}"
            else:
                raise ValueError("Target language cannot be empty when translating")
        prompt = template.format(instruction=instruction, text=text)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful writing assistant to help correct grammar mistakes, polish and paraphrase texts.",
        },
        {"role": "user", "content": prompt},
    ]
    finish_reason = None
    while finish_reason != "stop":
        if len(messages) > 2 and messages[-1]["role"] == "assistant":
            messages.append({"role": "user", "content": "please continue"})
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=messages,
        )
        messages.append(res["choices"][0]["message"])
        finish_reason = res["choices"][0]["finish_reason"]
        if len(messages) >= 5:
            break

    response_text = " ".join(
        [msg["content"] for msg in messages if msg["role"] == "assistant"]
    )
    return response_text


with gr.Blocks(css="") as demo:
    gr.Markdown("# ✒️ Writing Comrade")
    gr.Markdown("Comrade, I'm your faithful writing fellow powered by ChatGPT. Destination, commander?")
    gr.Markdown(
        "🎮 This demo is hosted on: [Huggingface Spaces](https://huggingface.co/spaces/Spico/writing-comrade) <br />"
        "⭐ Star me on GitHub: [Spico197/writing-comrade](https://github.com/Spico197/writing-comrade) <br />"
        "You may want to follow [this instruction](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key) to get an API key."
    )

    with gr.Row():
        api_key = gr.Textbox(label='OpenAI API Key', type="password")

    with gr.Row().style(equal_height=True):
        with gr.Column(scale=3):
            emojis = "🪄🥊💎🫧🚌🎤"
            task_type = gr.Radio([f"{emojis[i]}{k.title()}" for i, k in enumerate(instructions.keys())], label="Task")
        with gr.Column(min_width=100):
            tgt_lang = gr.Textbox(label="Target language in translation")
        with gr.Column():
            text_button = gr.Button("Can~ do!", variant="primary")

    with gr.Row():
        with gr.Column():
            text_input = gr.TextArea(lines=15, label="Input")
        with gr.Column():
            text_output = gr.TextArea(lines=15, label="Output")

        text_button.click(
            chat, inputs=[task_type, text_input, api_key, tgt_lang], outputs=text_output
        )

demo.launch()
