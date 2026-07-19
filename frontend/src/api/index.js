import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 30000 })

// Config
export const getConfig = () => api.get('/config')
export const saveConfig = (config) => api.post('/config', config)
export const testConnection = (config) => api.post('/config/test', config)

// Data (preview)
export const uploadData = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/data/upload', form)
}

// Projects
export const listProjects = () => api.get('/projects')
export const createProject = (name, file) => {
  const form = new FormData()
  form.append('name', name)
  form.append('file', file)
  return api.post('/projects', form)
}
export const getProject = (id) => api.get(`/projects/${id}`)
export const deleteProject = (id) => api.delete(`/projects/${id}`)
export const getProjectInfo = (id) => api.get(`/projects/${id}/info`)

// Data files
export const listDataFiles = (id) => api.get(`/projects/${id}/data`)
export const addDataFile = (id, file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post(`/projects/${id}/data`, form)
}
export const mergeDataFiles = (id, selectedFiles) =>
  api.post(`/projects/${id}/data/merge`, { selected_files: selectedFiles })

// Reports
export const listReports = (id) => api.get(`/projects/${id}/reports`)
export const generateReport = (projectId, title, userNotes) =>
  api.post('/report/generate', {
    project_id: projectId, title, user_notes: userNotes || '',
  })

// ============ LangGraph SSE Streams ============

export function streamAnalysis(projectId, userInput, callbacks) {
  const { onLlmToken, onToolStart, onToolEnd, onNodeEnd, onDone, onError } = callbacks
  let buffer = ''

  return fetch('/api/analysis/run/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id: projectId, user_input: userInput }),
  }).then(async (res) => {
    const reader = res.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        try {
          const data = JSON.parse(line.slice(6))
          switch (data.type) {
            case 'llm_token':
              onLlmToken?.(data.content)
              break
            case 'tool_start':
              onToolStart?.(data.tool)
              break
            case 'tool_end':
              onToolEnd?.(data.tool, data.output)
              break
            case 'chain_end':
              onNodeEnd?.(data.node, data.state_update)
              break
            case 'done':
              onDone?.()
              return
            case 'error':
              onError?.(data.message)
              return
          }
        } catch (_) { /* skip malformed SSE */ }
      }
    }
  }).catch((err) => onError?.(err.message))
}

export function streamConclude(projectId, userNotes, callbacks) {
  const { onToken, onDone, onError } = callbacks
  let buffer = ''

  return fetch('/api/report/conclude/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id: projectId, user_notes: userNotes || '' }),
  }).then(async (res) => {
    const reader = res.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        try {
          const data = JSON.parse(line.slice(6))
          if (data.type === 'token') onToken?.(data.content)
          else if (data.type === 'done') { onDone?.(); return }
          else if (data.type === 'error') { onError?.(data.message); return }
        } catch (_) { /* skip */ }
      }
    }
  }).catch((err) => onError?.(err.message))
}
