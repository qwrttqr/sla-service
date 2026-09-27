import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 120000, // 2 minutes, planning can take a bit with geocoding
})

export async function checkBackendHealth() {
  try {
    await client.get('/docs', { timeout: 3000 })
    return true
  } catch (err) {
    return false
  }
}

export async function submitPlanningCsv(engineersFile, requestsFile) {
  const formData = new FormData()
  formData.append('engineers_file', engineersFile)
  formData.append('requests_file', requestsFile)

  try {
    const response = await client.post('/v1/plan/csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  } catch (err) {
    if (err.response?.status === 404) {
      const fallbackRes = await client.post('/plan/csv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return fallbackRes.data
    }
    throw err
  }
}
