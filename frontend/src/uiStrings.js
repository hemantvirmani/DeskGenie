/**
 * Centralized UI strings for Desktop AI Agent frontend.
 * All user-facing strings displayed in the React components are defined here.
 * This makes it easy to update messaging and enables future localization.
 */

export const UIStrings = {
  // App.jsx strings
  APP_TITLE: "DeskGenie",
  CHAT_HISTORY_TITLE: "Chats",
  VERSION_INFO: "DeskGenie v1.0.0",
  LOGS_TITLE: "Logs",
  CLEAR_LOGS: "Clear",
  LOGS_PLACEHOLDER: "Logs will appear here when you chat or run benchmarks",

  // ChatGroupList.jsx strings
  NEW_CHAT_BUTTON: "New Chat",
  RENAME_CHAT: "Rename",
  DELETE_CHAT: "Delete",

  // Custom Questions Modal
  CUSTOM_QUESTIONS_TITLE: "Custom Question Numbers",
  CUSTOM_QUESTIONS_LABEL: "Enter comma-separated question numbers (1-20)",
  CUSTOM_QUESTIONS_PLACEHOLDER: "e.g., 1, 5, 10, 15",
  CUSTOM_QUESTIONS_EXAMPLE: "Example: \"1, 3, 6\" will run questions at indices 0, 2, and 5.",
  CANCEL_BUTTON: "Cancel",
  RUN_BUTTON: "Run",

  // ChatInput.jsx strings
  INPUT_PLACEHOLDER: "Ask a question or give a command...",
  GAIA_PRESETS_BUTTON: "GAIA: All Ques",
  CUSTOM_GAIA_BUTTON: "GAIA: Custom Ques",

  // ChatWindow.jsx strings
  WELCOME_TITLE: "Welcome to DeskGenie!",
  WELCOME_SUBTITLE: "Ask a question or give a command to get started.",

  // MessageBubble.jsx strings
  PROCESSING_TEXT: "Processing...",

};