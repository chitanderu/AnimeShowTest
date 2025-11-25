 <template>
  <div class="character-showcase">
    <!-- 顶部标题 -->
    <header class="header">
      <h1>动漫角色展示</h1>
      <p>搜索并添加你喜欢的角色，一键导出精美卡片</p>
    </header>

    <!-- 操作区 -->
    <section class="action-bar">
      <div class="search-container">
        <input
          v-model="searchName"
          type="text"
          class="search-input"
          placeholder="输入角色名字（如：Asuna, Naruto, Spike...）"
          @keypress.enter="searchCharacter"
          :disabled="loading"
        />
        <button
          class="add-btn"
          @click="searchCharacter"
          :disabled="loading"
        >
          {{ loading ? '搜索中…' : '搜索并添加' }}
        </button>
      </div>

      <div class="action-info">
        <span class="character-count">已添加 <b>{{ characters.length }}</b> 个角色</span>
        <button
          class="export-btn"
          @click="exportAllCharacters"
          :disabled="characters.length === 0"
        >
          导出全部
        </button>
      </div>
    </section>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">{{ error }}</div>

    <!-- 搜索结果弹窗 -->
    <div v-if="showSearchResults" class="search-results-modal" @click.self="closeSearchResults">
      <div class="search-results-container">
        <div class="search-results-header">
          <h3>找到 {{ searchResults.length }} 个匹配的角色</h3>
          <button class="close-btn" @click="closeSearchResults">×</button>
        </div>

        <div class="search-results-list">
          <div
            v-for="character in searchResults"
            :key="character.id"
            class="search-result-item"
            @click="selectCharacter(character)"
          >
            <div class="result-image">
              <img :src="character.image.medium" :alt="character.name.full" @error="handleImageError" />
            </div>
            <div class="result-info">
              <div class="result-name">{{ character.name.full }}</div>
              <div class="result-native">{{ character.name.native }}</div>
              <div class="result-details">
                <span v-if="character.gender">{{ character.gender }}</span>
                <span v-if="character.age">{{ character.age }} 岁</span>
                <span>{{ formatNumber(character.favourites) }} 收藏</span>
              </div>
              <div v-if="character.media.length > 0" class="result-media">
                出现作品：{{ character.media[0].title }}
                <span v-if="character.media.length > 1">等 {{ character.media.length }} 部</span>
              </div>
            </div>
            <div class="select-arrow">→</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主体内容 -->
    <main class="container">
      <div v-if="characters.length === 0 && !loading" class="empty-state">
        <h3>还没有添加任何角色</h3>
        <p>在上方搜索框输入角色名字，添加你喜欢的角色吧。</p>
      </div>

      <div
        v-for="(character, index) in characters"
        :key="character.id"
        class="character-card"
      >
        <div class="image-container">
          <img
            class="character-image"
            :src="character.image.large"
            :alt="character.name.full"
            @error="handleImageError"
          />
          <button class="delete-btn" @click="removeCharacter(index)">×</button>
        </div>

        <div class="card-content">
          <div class="character-name">{{ character.name.full }}</div>
          <div class="native-name">{{ character.name.native }}</div>

          <div class="info-row">
            <div class="info-item">
              <span>性别：</span>{{ character.gender || '未知' }}
            </div>
            <div class="info-item">
              <span>年龄：</span>{{ character.age || '未知' }}
            </div>
            <div class="info-item">
              <span>收藏：</span>{{ formatNumber(character.favourites) }}
            </div>
          </div>

          <div class="tags">
            <span v-if="character.dateOfBirth.month && character.dateOfBirth.day">
              {{ character.dateOfBirth.month }}月{{ character.dateOfBirth.day }}日
            </span>
            <span
              v-for="(media, idx) in character.media.slice(0, 2)"
              :key="idx"
            >
              {{ media.title }}
            </span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import request from '@/utils/request'  // 使用 axios 实例

export default {
  name: 'CharacterShowcaseView',
  data() {
    return {
      searchName: '',
      characters: [],
      searchResults: [],  // 搜索结果列表
      showSearchResults: false,  // 是否显示搜索结果
      loading: false,
      error: null
    }
  },
  methods: {
    async searchCharacter() {
      if (!this.searchName.trim()) {
        this.error = '请输入角色名字'
        return
      }

      this.loading = true
      this.error = null
      this.showSearchResults = false

      try {
        console.log('搜索角色:', this.searchName)

        // 调用后端 API
        const data = await request.get('/api/character/search', {
          params: {
            name: this.searchName.trim()
          }
        })

        console.log('API响应数据:', data)
        console.log('data的类型:', typeof data)
        console.log('data.data:', data.data)

        // 处理响应数据
        let characterList = []

        if (data.data && data.data.characters) {
          // 格式1: { code: 0, message: 'success', data: { characters: [...] } }
          characterList = data.data.characters
          console.log('使用格式1: data.data.characters')
        } else if (data.characters) {
          // 格式2: { characters: [...] } (axios拦截器可能已经解包)
          characterList = data.characters
          console.log('使用格式2: data.characters')
        } else if (Array.isArray(data.data)) {
          // 格式3: { data: [...] }
          characterList = data.data
          console.log('使用格式3: data.data 是数组')
        } else if (Array.isArray(data)) {
          // 格式4: 直接是数组
          characterList = data
          console.log('使用格式4: data 是数组')
        } else {
          console.error('未知的数据格式:', data)
          console.error('data的所有key:', Object.keys(data))
          this.error = `数据格式错误 - 请查看控制台`
          return
        }

        if (characterList.length > 0) {
          // 显示搜索结果供用户选择
          this.searchResults = characterList
          this.showSearchResults = true
          console.log(`找到 ${characterList.length} 个匹配的角色`)
        } else {
          this.error = '未找到该角色'
        }

      } catch (err) {
        console.error('搜索失败:', err)

        if (err.response) {
          // 服务器返回错误
          if (err.response.status === 404) {
            this.error = `未找到角色: ${this.searchName}`
          } else if (err.response.status === 400) {
            this.error = '请输入有效的角色名字'
          } else {
            this.error = `搜索失败: ${err.response.data?.detail || '未知错误'}`
          }
        } else if (err.request) {
          // 请求发送但没收到响应
          this.error = '无法连接到服务器，请检查后端是否启动'
        } else {
          // 其他错误
          this.error = `错误: ${err.message}`
        }
      } finally {
        this.loading = false
      }
    },

    async selectCharacter(character) {
      // 检查是否已存在
      const exists = this.characters.some(c => c.id === character.id)
      if (exists) {
        this.error = '该角色已经添加过了'
      } else {
        // 添加到列表
        await request.post('/api/character/save', character)
        this.characters.push(character)
        console.log('角色添加成功:', character.name.full)

        // 关闭搜索结果
        this.showSearchResults = false
        this.searchResults = []
        this.searchName = ''
        this.error = null
      }
    },

    closeSearchResults() {
      this.showSearchResults = false
      this.searchResults = []
    },

    removeCharacter(index) {
      this.characters.splice(index, 1)
      console.log('角色已删除')
    },

    exportAllCharacters() {
      if (this.characters.length === 0) {
        alert('还没有添加任何角色哦！')
        return
      }

      // TODO: 实现真正的导出功能
      console.log('准备导出角色:', this.characters)
      alert(`准备导出 ${this.characters.length} 个角色！\n\n功能开发中：\n- 生成高清卡片图片\n- 批量导出为ZIP\n- 一键分享`)
    },

    formatNumber(num) {
      if (!num) return '0'
      if (num >= 10000) {
        return (num / 10000).toFixed(1) + 'K'
      }
      return num.toString()
    },

    handleImageError(e) {
      // 设置默认图片
      e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23ddd" width="100" height="100"/%3E%3Ctext fill="%23999" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E暂无图片%3C/text%3E%3C/svg%3E'
    }
  }
}
</script>

<style scoped>

.character-showcase {
  background: #f9f9fb;
  color: #1d1d1f;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
  min-height: 100vh;
  padding: 40px 5%;
  transition: background 0.3s ease;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}
.header h1 {
  font-size: 2.5rem;
  font-weight: 600;
  margin-bottom: 10px;
}
.header p {
  color: #6e6e73;
  font-size: 1rem;
}

.action-bar {
  display: flex;
  flex-direction: column;
  gap: 15px;
  align-items: center;
  margin-bottom: 40px;
}

.search-container {
  display: flex;
  width: 100%;
  max-width: 600px;
}
.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #d2d2d7;
  border-radius: 8px 0 0 8px;
  outline: none;
  font-size: 16px;
}
.search-input:focus {
  border-color: #0071e3;
  box-shadow: 0 0 0 2px rgba(0,113,227,0.1);
}

.add-btn {
  padding: 12px 24px;
  background: #0071e3;
  color: white;
  border: none;
  border-radius: 0 8px 8px 0;
  cursor: pointer;
  transition: background 0.2s ease;
}
.add-btn:hover {
  background: #0077ed;
}
.add-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-info {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
}
.export-btn {
  padding: 10px 20px;
  border: 1px solid #0071e3;
  background: white;
  color: #0071e3;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.export-btn:hover {
  background: #0071e3;
  color: white;
}

.error-message {
  color: #ff3b30;
  text-align: center;
  margin: 10px 0;
}

.container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
}

.character-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.character-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.1);
}

.image-container {
  position: relative;
  height: 280px;
  overflow: hidden;
}
.character-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.delete-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255,255,255,0.8);
  border: none;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  font-size: 18px;
  cursor: pointer;
  transition: background 0.2s ease;
}
.delete-btn:hover {
  background: rgba(255,255,255,1);
}

.card-content {
  padding: 16px;
}
.character-name {
  font-size: 1.2rem;
  font-weight: 600;
}
.native-name {
  color: #6e6e73;
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 0.95rem;
  color: #424245;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.tags span {
  background: #f2f2f7;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.85rem;
}

.empty-state {
  text-align: center;
  color: #6e6e73;
  margin-top: 100px;
}



.character-showcase {
  width: 100%;
  padding: 60px 20px;
  background: #f5f5f7;
  min-height: 100vh;
}

.header {
  max-width: 1200px;
  margin: 0 auto 50px;
  text-align: center;
}

.header h1 {
  font-size: 3em;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 15px;
  letter-spacing: -0.5px;
}

.header p {
  font-size: 1.2em;
  color: #6e6e73;
  font-weight: 400;
}

.action-bar {
  max-width: 1200px;
  margin: 0 auto 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 18px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  gap: 15px;
}

.search-container {
  flex: 1;
  display: flex;
  gap: 10px;
}

.search-input {
  flex: 1;
  padding: 12px 20px;
  border: 2px solid #e5e5e7;
  border-radius: 980px;
  font-size: 1em;
  outline: none;
  transition: all 0.3s ease;
  font-family: inherit;
}

.search-input:focus {
  border-color: #06c;
  box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1);
}

.search-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.add-btn {
  background: #06c;
  color: white;
  border: none;
  padding: 12px 28px;
  border-radius: 980px;
  font-size: 1em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.add-btn:hover:not(:disabled) {
  background: #0077ed;
  transform: scale(1.02);
}

.add-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.character-count {
  font-size: 1.1em;
  color: #1d1d1f;
  font-weight: 500;
  white-space: nowrap;
}

.character-count span {
  color: #06c;
  font-weight: 600;
}

.export-btn {
  background: #34c759;
  color: white;
  border: none;
  padding: 12px 28px;
  border-radius: 980px;
  font-size: 1em;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.export-btn:hover:not(:disabled) {
  background: #30d158;
  transform: scale(1.02);
}

.export-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  max-width: 1200px;
  margin: 0 auto 20px;
  padding: 15px 20px;
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
  border-radius: 12px;
  text-align: center;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 30px;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 80px 20px;
  color: #86868b;
}

.empty-state-icon {
  font-size: 4em;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state h3 {
  font-size: 1.5em;
  color: #1d1d1f;
  margin-bottom: 10px;
  font-weight: 600;
}

.empty-state p {
  font-size: 1.1em;
  color: #6e6e73;
}

.character-card {
  position: relative;
  background: white;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.character-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.12);
}

.image-container {
  position: relative;
  width: 100%;
  height: 360px;
  overflow: hidden;
  background: #f5f5f7;
}

.character-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.character-card:hover .character-image {
  transform: scale(1.05);
}

.subtle-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 100px;
  background: linear-gradient(to top, rgba(255,255,255,0.95), transparent);
  pointer-events: none;
}

.delete-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 36px;
  height: 36px;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(20px);
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1.2em;
  opacity: 0;
  z-index: 2;
}

.character-card:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: #ff3b30;
  color: white;
  transform: scale(1.1);
}

.card-content {
  padding: 20px;
}

.character-name {
  font-size: 1.4em;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 5px;
  letter-spacing: -0.3px;
}

.native-name {
  font-size: 1em;
  color: #6e6e73;
  margin-bottom: 15px;
  font-weight: 400;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-top: 1px solid #f5f5f7;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 0.75em;
  color: #86868b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 500;
}

.info-value {
  font-size: 1em;
  color: #1d1d1f;
  font-weight: 500;
}

.favorites-number {
  color: #06c;
  font-weight: 600;
}

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 12px;
}

.tag {
  background: #f5f5f7;
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 0.85em;
  color: #1d1d1f;
  font-weight: 500;
}

@media (max-width: 968px) {
  .header h1 {
    font-size: 2em;
  }

  .action-bar {
    flex-direction: column;
  }

  .search-container {
    width: 100%;
  }
}

@media (max-width: 768px) {
  .container {
    grid-template-columns: 1fr;
  }
}

/* 搜索结果弹窗 */
.search-results-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.search-results-container {
  background: white;
  border-radius: 20px;
  max-width: 700px;
  width: 100%;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.search-results-header {
  padding: 25px 30px;
  border-bottom: 1px solid #e5e5e7;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-results-header h3 {
  font-size: 1.5em;
  color: #1d1d1f;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  width: 36px;
  height: 36px;
  background: #f5f5f7;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.2em;
  color: #6e6e73;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #e5e5e7;
  transform: scale(1.1);
}

.search-results-list {
  overflow-y: auto;
  padding: 15px;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: white;
  border: 2px solid #f5f5f7;
  border-radius: 16px;
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-result-item:hover {
  border-color: #06c;
  background: #f9f9fb;
  transform: translateX(5px);
}

.result-image {
  flex-shrink: 0;
  width: 80px;
  height: 100px;
  border-radius: 12px;
  overflow: hidden;
  background: #f5f5f7;
}

.result-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.result-info {
  flex: 1;
  min-width: 0;
}

.result-name {
  font-size: 1.2em;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-native {
  font-size: 1em;
  color: #6e6e73;
  margin-bottom: 10px;
}

.result-details {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.detail-badge {
  background: #f5f5f7;
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.85em;
  color: #1d1d1f;
  font-weight: 500;
}

.detail-badge.favorites {
  color: #06c;
}

.result-media {
  font-size: 0.9em;
  color: #86868b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.select-arrow {
  flex-shrink: 0;
  font-size: 1.5em;
  color: #06c;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.search-result-item:hover .select-arrow {
  opacity: 1;
}

/* 响应式 - 搜索结果弹窗 */
@media (max-width: 768px) {
  .search-results-modal {
    padding: 0;
  }

  .search-results-container {
    border-radius: 0;
    max-height: 100vh;
    height: 100vh;
  }

  .search-result-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .result-image {
    width: 100%;
    height: 150px;
  }

  .result-name {
    white-space: normal;
  }

  .result-media {
    white-space: normal;
  }
}
</style>