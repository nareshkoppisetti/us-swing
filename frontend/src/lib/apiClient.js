/**
 * File: frontend/src/lib/apiClient.js
 * Re-export alias for the main API client (lib/api.js).
 * The apiClient wrapper passes through directly since our api already
 * returns parsed JSON (not an axios response envelope).
 */
import { api } from './api';

export const apiClient = {
  get:    (url, config = {}) => api.get(url, config),
  post:   (url, data, config = {}) => api.post(url, data, config),
  put:    (url, data, config = {}) => api.put(url, data, config),
  patch:  (url, data, config = {}) => api.patch(url, data, config),
  delete: (url, config = {}) => api.delete(url, config),
};

export default apiClient;
