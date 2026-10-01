with open('frontend/src/api/client.ts', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = """http.interceptors.request.use((config) => {
  const token = lerToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  const tenantId = localStorage.getItem('@pride:tenant_id')
  if (tenantId) {
    config.headers['X-Tenant-ID'] = tenantId
  }
  return config
})"""

text = text.replace("""http.interceptors.request.use((config) => {
  const token = lerToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})""", replacement)

with open('frontend/src/api/client.ts', 'w', encoding='utf-8') as f:
    f.write(text)
