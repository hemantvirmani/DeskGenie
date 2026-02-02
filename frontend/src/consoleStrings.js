/**
 * Centralized console strings for Desktop AI Agent frontend.
 * All console.log, console.error, console.warn messages are defined here.
 * This makes it easy to update messaging and enables future localization.
 * 
 * Benefits:
 * - Consistent console messaging
 * - Easy maintenance and updates
 * - Professional, well-formatted messages
 * - Potential for future localization
 * - Easier testing and validation
 */

export const ConsoleStrings = {
  // Data loading messages
  CHAT_LOAD_FAILED: 'Failed to load chats: {error}',
  CONFIG_FETCH_FAILED: 'Failed to fetch config: {error}',
  
  // Chat operations
  CHAT_SAVE_FAILED: 'Failed to save chat: {error}',
  CHAT_DELETE_FAILED: 'Failed to delete chat: {error}',
  
  // API operations
  API_REQUEST_FAILED: 'API request failed: {error}',
  API_RESPONSE_ERROR: 'API returned error: {error}',
  
  // Component lifecycle
  COMPONENT_MOUNT: '{componentName} mounted',
  COMPONENT_UNMOUNT: '{componentName} unmounted',
  
  // State management
  STATE_UPDATE: 'State updated: {stateKey}',
  STATE_ERROR: 'State error: {error}',
  
  // Event handling
  EVENT_HANDLER: 'Event handler triggered: {eventName}',
  EVENT_ERROR: 'Event handler error: {eventName} - {error}',
};

/**
 * Helper function to format console strings with placeholders
 * @param {string} template - The template string with {placeholder} syntax
 * @param {object} values - Object containing values to replace placeholders
 * @returns {string} Formatted string
 */
export const formatConsole = (template, values = {}) => {
  let result = template;
  for (const [key, value] of Object.entries(values)) {
    result = result.replace(`{${key}}`, value);
  }
  return result;
};

/**
 * Logger utility that uses the centralized console strings
 */
export const Logger = {
  /**
   * Log informational message
   * @param {string} key - ConsoleStrings key
   * @param {object} values - Values to format the message
   */
  info(key, values = {}) {
    console.info(formatConsole(ConsoleStrings[key] || key, values));
  },

  /**
   * Log warning message
   * @param {string} key - ConsoleStrings key
   * @param {object} values - Values to format the message
   */
  warn(key, values = {}) {
    console.warn(formatConsole(ConsoleStrings[key] || key, values));
  },

  /**
   * Log error message
   * @param {string} key - ConsoleStrings key
   * @param {object} values - Values to format the message
   */
  error(key, values = {}) {
    console.error(formatConsole(ConsoleStrings[key] || key, values));
  },

  /**
   * Log debug message
   * @param {string} key - ConsoleStrings key
   * @param {object} values - Values to format the message
   */
  debug(key, values = {}) {
    if (process.env.NODE_ENV === 'development') {
      console.debug(formatConsole(ConsoleStrings[key] || key, values));
    }
  },
};

export default ConsoleStrings;