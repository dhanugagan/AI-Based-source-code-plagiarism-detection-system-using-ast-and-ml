import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  register: (data) => api.post('/api/auth/register', data),
  login: (email, password) => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    return api.post('/api/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },
  me: () => api.get('/api/auth/me'),
}

export const submissionsApi = {
  upload: (file) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/api/submissions/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  list: () => api.get('/api/submissions'),
  get: (id) => api.get(`/api/submissions/${id}`),
  source: (id) => api.get(`/api/submissions/${id}/source`),
  delete: (id) => api.delete(`/api/submissions/${id}`),
}

export const comparisonsApi = {
  analyze: (submission1_id, submission2_id) =>
    api.post('/api/comparisons/analyze', { submission1_id, submission2_id }),
  list: () => api.get('/api/comparisons'),
  get: (id) => api.get(`/api/comparisons/${id}`),
  batch: (submission_ids) => api.post('/api/comparisons/batch', { submission_ids }),
}

export const reportsApi = {
  generate: (comparisonId) => api.post(`/api/reports/${comparisonId}/generate`),
  download: (reportId) =>
    api.get(`/api/reports/${reportId}`, { responseType: 'blob' }),
}

export const dashboardApi = {
  summary: () => api.get('/api/dashboard/summary'),
}

export const adminApi = {
  users: () => api.get('/api/admin/users'),
  submissions: () => api.get('/api/admin/submissions'),
  comparisons: () => api.get('/api/admin/comparisons'),
  highRisk: () => api.get('/api/admin/comparisons/high-risk'),
  statistics: () => api.get('/api/admin/statistics'),
  deleteSubmission: (id) => api.delete(`/api/admin/submissions/${id}`),
}

export default api
