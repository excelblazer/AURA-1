/**
 * Utility functions for formatting data in the UI
 */

/**
 * Format a date string to a localized date format
 * @param {string} dateString - ISO date string
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date string
 */
export const formatDate = (dateString, options = {}) => {
  if (!dateString) return '';
  
  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  };
  
  const mergedOptions = { ...defaultOptions, ...options };
  
  return new Date(dateString).toLocaleDateString(undefined, mergedOptions);
};

/**
 * Format a date string to a localized date and time format
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date and time string
 */
export const formatDateTime = (dateString) => {
  if (!dateString) return '';
  
  return new Date(dateString).toLocaleString();
};

/**
 * Format a file size in bytes to a human-readable format
 * @param {number} bytes - File size in bytes
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted file size
 */
export const formatFileSize = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * Truncate a string if it exceeds a maximum length
 * @param {string} str - String to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated string
 */
export const truncateString = (str, maxLength = 50) => {
  if (!str) return '';
  if (str.length <= maxLength) return str;
  
  return str.slice(0, maxLength) + '...';
};

/**
 * Format a validation issue type to a human-readable format
 * @param {string} type - Issue type
 * @returns {string} Formatted issue type
 */
export const formatIssueType = (type) => {
  if (!type) return '';
  
  // Convert snake_case to Title Case
  return type
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

/**
 * Format a document type to a human-readable format
 * @param {string} type - Document type
 * @returns {string} Formatted document type
 */
export const formatDocumentType = (type) => {
  if (!type) return '';
  
  const typeMap = {
    'attendance_record': 'Attendance Record',
    'progress_report': 'Progress Report',
    'invoice': 'Invoice',
    'service_log': 'Service Log'
  };
  
  return typeMap[type] || type;
};

/**
 * Format a job status to a human-readable format
 * @param {string} status - Job status
 * @returns {string} Formatted job status
 */
export const formatJobStatus = (status) => {
  if (!status) return '';
  
  const statusMap = {
    'pending': 'Pending',
    'processing': 'Processing',
    'completed': 'Completed',
    'failed': 'Failed'
  };
  
  return statusMap[status] || status;
};
