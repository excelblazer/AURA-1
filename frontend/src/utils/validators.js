/**
 * Utility functions for form validation
 */

/**
 * Validate if a string is a valid email address
 * @param {string} email - Email address to validate
 * @returns {boolean} True if email is valid
 */
export const isValidEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate if a password meets minimum requirements
 * @param {string} password - Password to validate
 * @returns {object} Validation result with isValid and message
 */
export const validatePassword = (password) => {
  if (!password) {
    return { isValid: false, message: 'Password is required' };
  }
  
  if (password.length < 8) {
    return { isValid: false, message: 'Password must be at least 8 characters' };
  }
  
  // Check for at least one number
  if (!/\d/.test(password)) {
    return { isValid: false, message: 'Password must contain at least one number' };
  }
  
  // Check for at least one uppercase letter
  if (!/[A-Z]/.test(password)) {
    return { isValid: false, message: 'Password must contain at least one uppercase letter' };
  }
  
  return { isValid: true, message: '' };
};

/**
 * Validate if two passwords match
 * @param {string} password - Original password
 * @param {string} confirmPassword - Confirmation password
 * @returns {boolean} True if passwords match
 */
export const passwordsMatch = (password, confirmPassword) => {
  return password === confirmPassword;
};

/**
 * Validate if a string is not empty
 * @param {string} value - String to validate
 * @returns {boolean} True if string is not empty
 */
export const isNotEmpty = (value) => {
  return value !== null && value !== undefined && value.trim() !== '';
};

/**
 * Validate if a value is a valid number
 * @param {any} value - Value to validate
 * @returns {boolean} True if value is a valid number
 */
export const isValidNumber = (value) => {
  if (value === null || value === undefined || value === '') {
    return false;
  }
  
  return !isNaN(Number(value));
};

/**
 * Validate if a file has an allowed extension
 * @param {File} file - File to validate
 * @param {Array} allowedExtensions - Array of allowed extensions (e.g., ['.xlsx', '.xls'])
 * @returns {boolean} True if file has an allowed extension
 */
export const hasAllowedExtension = (file, allowedExtensions) => {
  if (!file || !file.name) {
    return false;
  }
  
  const fileName = file.name.toLowerCase();
  return allowedExtensions.some(ext => fileName.endsWith(ext.toLowerCase()));
};

/**
 * Validate if a file is within the maximum size limit
 * @param {File} file - File to validate
 * @param {number} maxSizeBytes - Maximum file size in bytes
 * @returns {boolean} True if file is within the size limit
 */
export const isWithinSizeLimit = (file, maxSizeBytes) => {
  if (!file) {
    return false;
  }
  
  return file.size <= maxSizeBytes;
};
