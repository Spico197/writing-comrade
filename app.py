import openai
import gradio as gr


instructions = {
    "completion": "Please help me complete the text",
    "correction": "Please help me correct mistakes in the text",
    "polishing": "Please help me polish the language and improve my writing",
    "paraphrase": "Please help me paraphrase the text",
    "freestyle": "",
}

template = "{instruction}:\n\nText: {text}"


def chat(task_type: str, text: str, api_key: str) -> str:
    openai.api_key = api_key

    prompt = ""
    task_type = task_type.lower()
    if task_type == "freestyle":
        prompt = text
    else:
        prompt = template.format(instruction=instructions[task_type], text=text)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful writing assistant to help correct grammar mistakes and polish or paraphrase texts.",
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
        "🎮 This demo is hosted on: https://huggingface.co/spaces/Spico/writing-comrade <br />⭐ Star me on GitHub: https://github.com/Spico197/writing-comrade"
    )

    with gr.Row():
        api_key = gr.Textbox(label="OpenAI API Key")

    with gr.Row():
        task_type = gr.Radio([k.title() for k in instructions.keys()], label="Task")
        text_button = gr.Button("Can~ do!")

    with gr.Row():
        text_input = gr.TextArea(lines=15, label="Input")
        text_output = gr.TextArea(lines=15, label="Output")

        text_button.click(
            chat, inputs=[task_type, text_input, api_key], outputs=text_output
        )

demo.launch()
