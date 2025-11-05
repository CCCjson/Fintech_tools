import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 行业相关API
export const industryAPI = {
  getIndustries: () => api.get('/industries'),
  getIndustry: (code) => api.get(`/industries/${code}`),
  getIndustryRanking: () => api.get('/industries/ranking')
}

// 股票相关API
export const stockAPI = {
  getStocks: (params) => api.get('/stocks', { params }),
  getStock: (code) => api.get(`/stocks/${code}`),
  getFinancial: (code) => api.get(`/stocks/${code}/financial`),
  getValuation: (code) => api.get(`/stocks/${code}/valuation`),
  filterStocks: (filters) => api.post('/stocks/filter', filters)
}

// 分析相关API
export const analysisAPI = {
  getRecommendations: (params) => api.get('/analysis/recommendations', { params }),
  getGrahamAnalysis: (code) => api.get(`/analysis/graham/${code}`)
}

// 任务相关API
export const taskAPI = {
  triggerCrawl: (data) => api.post('/tasks/crawl/trigger', data),
  getTaskStatus: (taskId) => api.get(`/tasks/status/${taskId}`)
}

export default api
