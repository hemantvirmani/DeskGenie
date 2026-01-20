import gradio as gr
import config

# --- Build Gradio Interface without Blocks Context ---

run_and_submit_all_callback = None  # Placeholder for the actual function

def _run_and_submit_all_local(profile: gr.OAuthProfile | None = None, active_agent: str = None):
    """Run and submit with specified agent type."""
    username = None

    if profile is not None:
        username = f"{profile.username}"
        print(f"User logged in: {username}")
    else:
        print("User not logged in.")
        return "Please Login to Hugging Face with the button.", None

    return run_and_submit_all_callback(username, active_agent)

def _run_and_submit_langgraph(profile: gr.OAuthProfile | None = None):
    """Run and submit with LangGraph agent."""
    return _run_and_submit_all_local(profile, active_agent=config.AGENT_LANGGRAPH)

def _run_and_submit_react(profile: gr.OAuthProfile | None = None):
    """Run and submit with ReActLangGraph agent."""
    return _run_and_submit_all_local(profile, active_agent=config.AGENT_REACT_LANGGRAPH)

def _run_and_submit_llamaindex(profile: gr.OAuthProfile | None = None):
    """Run and submit with LlamaIndex agent."""
    return _run_and_submit_all_local(profile, active_agent=config.AGENT_LLAMAINDEX)


def _parse_filter_indices(filter_text: str):
    """Parse comma-separated filter indices from text input.

    Args:
        filter_text: Comma-separated indices (e.g., "4, 7, 15") or empty for all questions

    Returns:
        tuple of indices or None if empty/invalid
    """
    if not filter_text or not filter_text.strip():
        return None  # Run all questions

    try:
        indices = tuple(int(idx.strip()) for idx in filter_text.split(',') if idx.strip())
        return indices if indices else None
    except ValueError:
        return None  # Invalid input, run all questions


def create_ui(run_and_submit_all, run_test_code):
    """Create the Main App with custom layout to include LoginButton"""

    global run_and_submit_all_callback
    run_and_submit_all_callback = run_and_submit_all

    def _run_test_with_filter(filter_text: str):
        """Wrapper to run test code with parsed filter indices."""
        filter_indices = _parse_filter_indices(filter_text)
        return run_test_code(filter=filter_indices)

    # --- Build Gradio Interface using Blocks ---
    with gr.Blocks() as demoApp:
        gr.Markdown("# Basic Agent Evaluation Runner")
        gr.Markdown(
            """
            **Instructions:**
            1.  Please clone this space, then modify the code to define your agent's logic, the tools, the necessary packages, etc ...
            2.  Log in to your Hugging Face account using the button below. This uses your HF username for submission.
            3.  Click 'Run Evaluation & Submit All Answers' to fetch questions, run your agent, submit answers, and see the score.
            ---
            **Disclaimers:**
            Once clicking on the "submit button, it can take quite some time ( this is the time for the agent to go through all the questions).
            This space provides a basic setup and is intentionally sub-optimal to encourage you to develop your own, more robust solution. For instance for the delay process of the submit button, a solution could be to cache the answers and submit in a seperate action or even to answer the questions in async.
            """
        )

        gr.LoginButton()

        gr.Markdown("### Run Evaluation with Different Agents")

        with gr.Row():
            run_button_langgraph = gr.Button("Run with LangGraph Agent", variant="primary")
            run_button_react = gr.Button("Run with ReAct Agent", variant="secondary")
            run_button_llamaindex = gr.Button("Run with LlamaIndex Agent", variant="secondary")

        status_output = gr.Textbox(label="Run Status / Submission Result", lines=5, interactive=False)
        # Removed max_rows=10 from DataFrame constructor
        results_table = gr.DataFrame(label="Questions and Agent Answers", wrap=True)

        run_button_langgraph.click(
            fn=_run_and_submit_langgraph,
            outputs=[status_output, results_table]
        )

        run_button_react.click(
            fn=_run_and_submit_react,
            outputs=[status_output, results_table]
        )

        run_button_llamaindex.click(
            fn=_run_and_submit_llamaindex,
            outputs=[status_output, results_table]
        )

        gr.Markdown("---")
        gr.Markdown("### Test Mode")
        gr.Markdown("Run agent on specific questions for testing. Leave empty to run all questions.")

        test_filter_input = gr.Textbox(
            label="Question Indices (comma-separated)",
            placeholder="e.g., 4, 7, 15 (leave empty for all questions)",
            value="",
            interactive=True
        )
        test_button = gr.Button("Run Test Examples")
        test_results_table = gr.DataFrame(label="Test Answers from Agent", wrap=True)
        test_button.click(
            fn=_run_test_with_filter,
            inputs=[test_filter_input],
            outputs=[test_results_table]
        )

    return demoApp
