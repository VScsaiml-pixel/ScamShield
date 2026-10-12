// In unified single localhost mode, API calls are relative to the current host
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Health check endpoint
 */
export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to connect to backend',
    };
  }
}

/**
 * Scanner service status
 */
export async function getScannerStatus() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/scan/status`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to retrieve scanner status',
    };
  }
}

/**
 * Core AI/ML message analysis endpoint
 */
export async function analyzeMessage(message) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analyze/message`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${response.status})`);
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to communicate with scam detection model',
    };
  }
}

/**
 * URL static lexical scam and phishing analysis endpoint
 */
export async function analyzeURL(url) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/analyze/url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${response.status})`);
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to communicate with URL security scanner',
    };
  }
}

/**
 * Fetch scan history list with optional filters
 */
export async function getScanHistory(params = {}) {
  try {
    const query = new URLSearchParams();
    if (params.limit) query.append('limit', params.limit);
    if (params.offset) query.append('offset', params.offset);
    if (params.scan_type) query.append('scan_type', params.scan_type);
    if (params.risk_level) query.append('risk_level', params.risk_level);

    const queryString = query.toString() ? `?${query.toString()}` : '';
    const response = await fetch(`${API_BASE_URL}/api/scans${queryString}`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${response.status})`);
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to retrieve scan history',
    };
  }
}

/**
 * Fetch full details of a specific scan by ID
 */
export async function getScanById(scanId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/scans/${scanId}`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${response.status})`);
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error.message || `Failed to retrieve scan #${scanId}`,
    };
  }
}

/**
 * Permanently delete a single scan record
 */
export async function deleteScanById(scanId) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/scans/${scanId}`, {
      method: 'DELETE',
      headers: { 'Accept': 'application/json' },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${response.status})`);
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error.message || `Failed to delete scan #${scanId}`,
    };
  }
}

/**
 * Permanently purge all scan history records (Privacy purge)
 */
export async function clearAllScans() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/scans`, {
      method: 'DELETE',
      headers: { 'Accept': 'application/json' },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${response.status})`);
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to clear scan history',
    };
  }
}

/**
 * Fetch aggregated dashboard statistics from SQLite
 */
export async function getDashboardStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/dashboard/stats`, {
      method: 'GET',
      headers: { 'Accept': 'application/json' },
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server error (${response.status})`);
    }

    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: error.message || 'Failed to retrieve dashboard statistics',
    };
  }
}



