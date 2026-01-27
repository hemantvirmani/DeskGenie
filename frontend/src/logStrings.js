/**
 * Centralized log strings for DeskGenie frontend.
 * All log messages displayed in the Logs panel are defined here.
 * This makes it easy to update messaging and enables future localization.
 */

export const LogStrings = {
  // Separators
  LOG_SEPARATOR: '='.repeat(30),

  // Benchmark logs
  STARTING_BENCHMARK_ALL: 'Starting GAIA benchmark (all questions)...',
  STARTING_BENCHMARK_CUSTOM: 'Starting GAIA benchmark (questions: {questions})...',
  BENCHMARK_COMPLETED: 'Benchmark completed successfully',
  BENCHMARK_FAILED: 'Benchmark failed: {error}',
  BENCHMARK_ERROR: 'Benchmark error: {error}',

  // Chat logs
  CHAT_PREFIX: 'Chat: "{preview}"',

  // Task logs
  TASK_STARTED: 'Task started (ID: {taskId}...)',

  // Error logs
  ERROR_PREFIX: 'Error: {error}',
  ERROR_INVALID_INDICES: 'Please enter valid comma-separated question numbers between 1 and 20.',

  // Message placeholders
  RUNNING_BENCHMARK: 'Running benchmark...',
  NO_RESPONSE: 'No response',
};

// Helper function to format strings with placeholders
export const formatLog = (template, values) => {
  let result = template;
  for (const [key, value] of Object.entries(values)) {
    result = result.replace(`{${key}}`, value);
  }
  return result;
};
