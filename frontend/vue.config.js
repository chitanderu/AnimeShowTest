const { defineConfig } = require('@vue/cli-service')
module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // FastAPI 后端地址
        changeOrigin: true,
        pathRewrite: { '^/api': '/api' } // 保留 /api 前缀
      }
    }
  }
}

