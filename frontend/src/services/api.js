import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

/**
 * Get all running containers
 */
export const getContainers = async () => {
  try {
    const response = await apiClient.get('/containers');
    // Backend returns { containers: [...] } or a list. Adjust if needed.
    return response.data.containers || response.data || [];
  } catch (error) {
    console.error("Backend API /containers failed.", error);
    throw new Error("Backend connection failed. Make sure the server is running on port 8000.");
  }
};

/**
 * Simulate a failure
 */
export const simulateFailure = async (type, containerName) => {
  try {
    if (!containerName) {
      containerName = 'backend';
    }
    await apiClient.post(`/simulate_failure?failure_type=${type}&container=${containerName}`);
    return true;
  } catch (error) {
    console.error(`Backend API /simulate_failure failed for ${type}.`, error);
    throw new Error("Failed to simulate failure. Is the backend running?");
  }
};

/**
 * Trigger the healing pipeline
 */
export const triggerPipeline = async (containerName) => {
  try {
    const response = await apiClient.post(`/trigger_pipeline?container_name=${containerName}`);
    const data = response.data;
    const report = data.incidents && data.incidents.length > 0 ? data.incidents[0] : null;

    if (report) {
       return {
         diagnosis: {
           container: report.container,
           issue: report.error_type,
           root_cause: report.suggested_fix,
           action: report.action_taken
         },
         timeline: [
           { time: new Date().toLocaleTimeString(), message: `Anomaly detected: ${report.error_type}` },
           { time: new Date(Date.now() + 500).toLocaleTimeString(), message: "Root cause identified" },
           { time: new Date(Date.now() + 1000).toLocaleTimeString(), message: `Action chosen: ${report.action_taken}` },
           { time: new Date(Date.now() + 1500).toLocaleTimeString(), message: "Recovery executed" },
           { time: new Date(Date.now() + 2000).toLocaleTimeString(), message: `Status: ${report.resolution_status}` }
         ]
       };
    } else {
       return {
          diagnosis: { container: containerName, issue: "No issues detected", root_cause: "-", action: "-" },
          timeline: [ { time: new Date().toLocaleTimeString(), message: data.message || "Pipeline completed normally." } ]
       }
    }
  } catch (error) {
    console.error("Backend API /trigger_pipeline failed.", error);
    throw new Error("Failed to trigger pipeline. Is the backend running?");
  }
};

/**
 * Get incident history
 */
export const getIncidents = async () => {
  try {
    const response = await apiClient.get('/incidents');
    const data = response.data.incidents || response.data || [];
    return data.map(inc => ({
      time: inc.timestamp && !isNaN(new Date(inc.timestamp)) ? new Date(inc.timestamp).toLocaleTimeString() : 'Unknown',
      container: inc.container,
      issue: inc.error_type,
      action: inc.action_taken,
      status: inc.resolution_status
    }));
  } catch (error) {
    console.error("Backend API /incidents failed.", error);
    throw new Error("Failed to fetch incidents data.");
  }
};

/**
 * Restart a container manually
 */
export const restartContainer = async (containerName) => {
  try {
    await apiClient.post(`/restart_container?container_name=${containerName}`);
    return true;
  } catch (error) {
    console.error(`Backend API /restart_container failed for ${containerName}.`, error);
    throw new Error("Failed to restart container.");
  }
};
