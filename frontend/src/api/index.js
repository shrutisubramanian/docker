import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  }
});

export const getContainers = async () => {
  const response = await api.get('/containers');
  return response.data.containers;
};

export const getIncidents = async () => {
  const response = await api.get('/incidents');
  return response.data;
};

export const triggerPipeline = async (containerName) => {
  const response = await api.post('/trigger_pipeline', null, {
    params: { container_name: containerName }
  });
  return response.data;
};

export const simulateFailure = async (failureType, container) => {
  const response = await api.post('/simulate_failure', null, {
    params: { failure_type: failureType, container: container }
  });
  return response.data;
};

export default api;
