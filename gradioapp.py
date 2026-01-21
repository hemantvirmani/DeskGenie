import gradio as gr
import config

# --- Build Gradio Interface without Blocks Context ---

run_and_verify_callback = None  # Placeholder for the actual function

def _run_and_verify_langgraph():
    """Run and verify with LangGraph agent."""
    return run_and_verify_callback(active_agent=config.AGENT_LANGGRAPH)

def _run_and_verify_react():
    """Run and verify with ReActLangGraph agent."""
    return run_and_verify_callback(active_agent=config.AGENT_REACT_LANGGRAPH)


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


def create_ui(run_and_verify, run_test_code):
    """Create the Main App with custom layout."""

    global run_and_verify_callback
    run_and_verify_callback = run_and_verify

    def _run_test_with_filter(filter_text: str):
        """Wrapper to run test code with parsed filter indices."""
        filter_indices = _parse_filter_indices(filter_text)
        return run_test_code(filter=filter_indices)

    # --- Build Gradio Interface using Blocks ---
    with gr.Blocks() as demoApp:
        gr.Markdown("# DeskGenie - Desktop AI Agent")
        gr.Markdown(
            """
            **Instructions:**
            1. Click one of the agent buttons below to run evaluation on test questions.
            2. Results will be verified locally against ground truth answers.
            ---
            **Note:** This runs the agent on all questions and verifies answers locally.
            """
        )

        gr.Markdown("### Run Evaluation with Different Agents")

        with gr.Row():
            run_button_langgraph = gr.Button("Run with LangGraph Agent", variant="primary")
            run_button_react = gr.Button("Run with ReAct Agent", variant="secondary")

        status_output = gr.Textbox(label="Verification Results", lines=10, interactive=False)
        results_table = gr.DataFrame(label="Questions and Agent Answers", wrap=True)

        run_button_langgraph.click(
            fn=_run_and_verify_langgraph,
            outputs=[status_output, results_table]
        )

        run_button_react.click(
            fn=_run_and_verify_react,
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
