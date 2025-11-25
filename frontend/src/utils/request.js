import axios from 'axios'

// 根据环境自动切换
// const baseURL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000'

const request = axios.create({
  baseURL: '/',
  timeout: 60000000000, // 图像处理可能需要更长时间
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    console.log('请求URL:', config.baseURL + config.url)

    // 如果是文件上传，修改 Content-Type
    if (config.data instanceof FormData) {
      config.headers['Content-Type'] = 'multipart/form-data'
    }

    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('请求失败:', error)

    // 统一错误处理
    let errorMessage = '请求失败'

    if (error.response) {
      // 服务器返回错误
      errorMessage = error.response.data?.detail || error.response.data?.message || `错误码: ${error.response.status}`
    } else if (error.request) {
      // 请求发出但没有收到响应
      errorMessage = '服务器无响应，请检查网络连接'
    } else {
      // 请求配置出错
      errorMessage = error.message
    }

    return Promise.reject(new Error(errorMessage))
  }
)


// ⭐ 添加流式请求方法
export const streamRequest = async (url, data, onChunk, onComplete, onError) => {
  try {
    const response = await fetch(`/api${url}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let isStreaming = true

    while (isStreaming) {
      const { value, done } = await reader.read()

      if (done) {
        isStreaming = false
        break
      }

      buffer += decoder.decode(value, { stream: true })

      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6))

            if (data.error) {
              onError && onError(data.error)
              isStreaming = false
              break
            }

            if (data.content) {
              onChunk && onChunk(data.content)
            }

            if (data.done) {
              onComplete && onComplete()
              isStreaming = false
            }
          } catch (e) {
            console.error('解析数据错误:', e)
          }
        }
      }
    }
  } catch (error) {
    console.error('流式请求错误:', error)
    onError && onError(error.message)
  }
}



export default request