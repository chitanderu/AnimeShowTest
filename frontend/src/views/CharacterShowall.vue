<template>
  <div class="character-showcase">
    <!-- 顶部标题 -->
    <header class="header">
      <h1>动漫角色展示</h1>
      <p>从数据库中读取角色信息，展示你的角色收藏</p>
    </header>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">{{ error }}</div>

    <!-- 主体内容 -->
    <main class="container">
      <!-- 空状态 -->
      <div v-if="!loading && characters.length === 0" class="empty-state">
        <div class="empty-state-icon">🎭</div>
        <h3>还没有任何角色数据</h3>
        <p>请先在后端添加角色记录。</p>
      </div>

      <!-- 角色卡片：图片部分完全复刻你的代码 -->
      <div
        v-for="(character, index) in characters"
        :key="character.id"
        class="character-card"
      >
        <div class="image-container">
          <img
            class="character-image"
            :src="character.image.medium || defaultImage"
            :alt="character.name_full || character.name_native || '角色图片'"
            @error="handleImageError"
          />
          <!-- 本地删除，仅前端移除，不动数据库 -->
          <button class="delete-btn" @click="removeCharacter(index)">×</button>
        </div>

        <div class="card-content">
          <div class="character-name">
            {{ character.name_native || character.name_full || '未命名角色' }}
          </div>

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
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  name: 'CharacterShowall',
  data() {
    return {
      characters: [],
      loading: false,
      error: null,
      defaultImage:
        'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect width="200" height="200" fill="%23eee"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" fill="%23999" dy=".3em" font-size="18"%3E暂无图片%3C/text%3E%3C/svg%3E'
    }
  },
  methods: {
    async fetchCharacters() {
      this.loading = true
      this.error = null
      try {
        const data = await request.get('/api/getallcharacters')
        console.log('角色数据:', data)

        if (Array.isArray(data)) {
          this.characters = data
        } else if (data.data && Array.isArray(data.data)) {
          this.characters = data.data
        } else {
          throw new Error('返回数据格式不正确')
        }
      } catch (err) {
        console.error('加载角色失败:', err)
        this.error =
          err.message || '加载角色失败，请检查服务器连接是否正常。'
      } finally {
        this.loading = false
      }
    },

    formatNumber(num) {
      if (!num) return '0'
      if (num >= 10000) {
        return (num / 10000).toFixed(1) + 'K'
      }
      return num.toString()
    },

    handleImageError(e) {
      e.target.src = this.defaultImage
    },

    // 只是前端移除一张卡片，不会改数据库
    removeCharacter(index) {
      this.characters.splice(index, 1)
    }
  },
  mounted() {
    this.fetchCharacters()
  }
}
</script>

<style scoped>
/* ===== 整体布局，可以保持简洁 ===== */
.character-showcase {
  width: 100%;
  padding: 60px 20px;
  background: #f5f5f7;
  min-height: 100vh;
}

.header {
  max-width: 1200px;
  margin: 0 auto 40px;
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

/* 错误提示 */
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

/* 内容网格 */
.container {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 30px;
}

/* 空状态 */
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

/* ===== 从这里开始，完全复刻你那套卡片 & 图片 ===== */

.character-card {
  position: relative;
  background: white;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.character-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

/* 图片容器：和你发的一模一样 */
.image-container {
  position: relative;
  width: 100%;
  height: 320px;
  overflow: hidden;
  background: #f5f5f7;
}

/* 图片样式：和你发的一模一样 */
.character-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

/* hover 放大：和你发的一模一样 */
.character-card:hover .character-image {
  transform: scale(1.05);
}

/* 删除按钮：和你发的后半段样式一致（悬浮出现） */
.delete-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.9);
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

/* 文本内容区域（可以比你的原件简化一点） */
.card-content {
  padding: 20px;
}

.character-name {
  font-size: 1.4em;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 10px;
  letter-spacing: -0.3px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f5f5f7;
  font-size: 0.95rem;
  color: #424245;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
</style>
