<template>
  <div class="home-page">
    <!-- Dota2背景轮播 -->
    <div class="background-carousel">
      <div class="bg-slide bg-slide-1"></div>
      <div class="bg-slide bg-slide-2"></div>
      <div class="bg-slide bg-slide-3"></div>
      <div class="bg-slide bg-slide-4"></div>
    </div>
    
    <div class="container">
      <header class="header">
        <h1 class="title">Dota2战绩分析</h1>
        <div class="search-box">
          <input
            v-model="accountId"
            type="text"
            class="input"
            placeholder="输入Steam账号ID（纯数字）"
            @keyup.enter="handleSearch"
          />
          <button class="btn btn-primary" @click="handleSearch" :disabled="loading">
            <span v-if="loading" class="loading"></span>
            <span v-else>查询</span>
          </button>
        </div>
      </header>

      <div v-if="error" class="error-message card">
        {{ error }}
      </div>

      <div v-if="analysis" class="analysis-content">
        <!-- 一句话点评 -->
        <div class="comment-card card">
          <h2 class="section-title">一句话点评</h2>
          <p class="comment-text">{{ analysis.comment }}</p>
        </div>

        <!-- 胜率曲线 -->
        <div class="chart-card card">
          <h2 class="section-title">近期胜率曲线</h2>
          <div ref="winRateChartRef" class="chart-container"></div>
        </div>

        <!-- 最佳战友和最爱损友 -->
        <div class="teammates-section">
          <div class="teammate-card card">
            <h2 class="section-title">最佳战友</h2>
            <div v-if="analysis.best_teammates.length === 0" class="empty-state">
              暂无组队数据（需要与同一队友组队超过1次）
            </div>
            <div v-else ref="bestTeammatesChartRef" class="chart-container-small"></div>
          </div>
          <div class="teammate-card card">
            <h2 class="section-title">最爱损友</h2>
            <div v-if="analysis.worst_teammates.length === 0" class="empty-state">
              暂无组队数据（需要与同一队友组队超过1次）
            </div>
            <div v-else ref="worstTeammatesChartRef" class="chart-container-small"></div>
          </div>
        </div>

        <!-- 数据概括 -->
        <div class="stats-grid">
          <div class="stat-card card">
            <h3 class="stat-label">总击杀数</h3>
            <p class="stat-value">{{ analysis.statistics.total_kills }}</p>
            <p class="stat-avg">平均: {{ analysis.statistics.avg_kills }}</p>
          </div>
          <div class="stat-card card">
            <h3 class="stat-label">总死亡数</h3>
            <p class="stat-value">{{ analysis.statistics.total_deaths }}</p>
            <p class="stat-avg">平均: {{ analysis.statistics.avg_deaths }}</p>
          </div>
          <div class="stat-card card">
            <h3 class="stat-label">总助攻数</h3>
            <p class="stat-value">{{ analysis.statistics.total_assists }}</p>
            <p class="stat-avg">平均: {{ analysis.statistics.avg_assists }}</p>
          </div>
          <div class="stat-card card">
            <h3 class="stat-label">总正补数</h3>
            <p class="stat-value">{{ analysis.statistics.total_last_hits }}</p>
            <p class="stat-avg">平均: {{ analysis.statistics.avg_last_hits }}</p>
          </div>
          <div class="stat-card card">
            <h3 class="stat-label">总英雄伤害</h3>
            <p class="stat-value">{{ analysis.statistics.total_hero_damage }}</p>
            <p class="stat-avg">平均: {{ analysis.statistics.avg_hero_damage }}</p>
          </div>
        </div>
      </div>
      
      <!-- 版权和作者信息 -->
      <footer class="footer">
        <div class="footer-content">
          <p class="copyright">版权归嘟嘟可大冒险公会所有</p>
          <p class="author">作者：ydd</p>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import axios from 'axios'

interface WinRatePoint {
  match_num: number
  win_rate: number
  is_win: boolean
  match_id?: number
  kills: number
  deaths: number
  assists: number
  hero_id?: number
  duration: number
}

interface Statistics {
  total_kills: number
  avg_kills: number
  total_deaths: number
  avg_deaths: number
  total_assists: number
  avg_assists: number
  total_last_hits: number
  avg_last_hits: number
  total_hero_damage: number
  avg_hero_damage: number
}

interface TeammateInfo {
  account_id: number
  name: string
  team_count: number
  win_count: number
  loss_count: number
  win_rate: number
}

interface Analysis {
  account_id: number
  comment: string
  win_rate_curve: WinRatePoint[]
  best_teammates: TeammateInfo[]
  worst_teammates: TeammateInfo[]
  statistics: Statistics
}

const accountId = ref('')
const loading = ref(false)
const error = ref('')
const analysis = ref<Analysis | null>(null)
const winRateChartRef = ref<HTMLDivElement | null>(null)
const bestTeammatesChartRef = ref<HTMLDivElement | null>(null)
const worstTeammatesChartRef = ref<HTMLDivElement | null>(null)
let winRateChart: echarts.ECharts | null = null
let bestTeammatesChart: echarts.ECharts | null = null
let worstTeammatesChart: echarts.ECharts | null = null

// 获取API基础URL（生产环境使用环境变量，开发环境使用代理）
const getApiBaseUrl = () => {
  // 生产环境：使用环境变量或直接使用完整URL
  if (import.meta.env.PROD) {
    const apiUrl = import.meta.env.VITE_API_BASE_URL || ''
    return apiUrl ? `$192.168.1.6:8001/api` : '/api'
  }
  // 开发环境：使用代理
  return '/api'
}

const handleSearch = async () => {
  if (!accountId.value.trim()) {
    error.value = '请输入Steam账号ID'
    return
  }

  const id = parseInt(accountId.value.trim())
  if (isNaN(id)) {
    error.value = '账号ID必须是数字'
    return
  }

  loading.value = true
  error.value = ''
  analysis.value = null

  try {
    const apiBaseUrl = getApiBaseUrl()
    const response = await axios.get(`${apiBaseUrl}/v1/players/${id}/analysis`)
    analysis.value = response.data
    await nextTick()
    renderWinRateChart()
    renderTeammatesCharts()
  } catch (err: any) {
    if (err.response?.status === 404) {
      error.value = '未找到该账号数据，请检查账号ID是否正确'
    } else {
      error.value = err.response?.data?.detail || '数据获取失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}

const renderWinRateChart = () => {
  if (!winRateChartRef.value || !analysis.value) return

  if (winRateChart) {
    winRateChart.dispose()
  }

  winRateChart = echarts.init(winRateChartRef.value, 'dark')

  const data = analysis.value.win_rate_curve
  const matchNums = data.map((d) => d.match_num)
  const winRates = data.map((d) => d.win_rate)

  const option = {
    backgroundColor: 'transparent',
    grid: {
      left: '10%',
      right: '10%',
      top: '10%',
      bottom: '15%',
    },
    xAxis: {
      type: 'category',
      data: matchNums,
      name: '场次',
      nameTextStyle: {
        color: '#999',
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)',
        },
      },
      axisLabel: {
        color: '#999',
      },
    },
    yAxis: {
      type: 'value',
      name: '胜率 (%)',
      nameTextStyle: {
        color: '#999',
      },
      min: 0,
      max: 100,
      axisLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.3)',
        },
      },
      axisLabel: {
        color: '#999',
        formatter: '{value}%',
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
    },
    tooltip: {
      trigger: 'axis',  // 改为axis，鼠标靠近整个区域都能触发
      backgroundColor: 'rgba(0, 0, 0, 0.9)',
      borderColor: 'rgba(255, 255, 255, 0.3)',
      borderWidth: 1,
      textStyle: {
        color: '#fff',
        fontSize: 12,
      },
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: 'rgba(74, 144, 226, 0.5)',
        },
      },
      formatter: (params: any) => {
        if (Array.isArray(params)) {
          const point = data[params[0].dataIndex]
          return `
            <div style="padding: 10px;">
              <div style="font-weight: bold; margin-bottom: 6px;">第${point.match_num}场</div>
              <div>胜率: <span style="color: #4a90e2;">${point.win_rate.toFixed(2)}%</span></div>
              <div>结果: <span style="color: ${point.is_win ? '#4a90e2' : '#e24a4a'};">${point.is_win ? '胜利' : '失败'}</span></div>
              <div>KDA: ${point.kills}/${point.deaths}/${point.assists}</div>
              <div>时长: ${Math.floor(point.duration / 60)}分钟</div>
            </div>
          `
        }
        return ''
      },
    },
    series: [
      {
        type: 'line',
        data: winRates,
        smooth: true,
        symbol: 'circle',
        symbolSize: 10,  // 增大节点大小
        lineStyle: {
          color: '#4a90e2',
          width: 2,
        },
        itemStyle: {
          color: '#4a90e2',
          borderColor: '#fff',
          borderWidth: 2,
        },
        emphasis: {
          // 鼠标悬停时放大节点
          symbolSize: 16,
          itemStyle: {
            borderWidth: 3,
          },
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: 'rgba(74, 144, 226, 0.3)',
              },
              {
                offset: 1,
                color: 'rgba(74, 144, 226, 0.05)',
              },
            ],
          },
        },
      },
    ],
  }

  winRateChart.setOption(option)

  // 响应式调整
  window.addEventListener('resize', () => {
    winRateChart?.resize()
  })
}

const renderTeammatesCharts = () => {
  if (!analysis.value) return

  // 渲染最佳战友图表
  if (analysis.value.best_teammates.length > 0 && bestTeammatesChartRef.value) {
    if (bestTeammatesChart) {
      bestTeammatesChart.dispose()
    }
    bestTeammatesChart = echarts.init(bestTeammatesChartRef.value, 'dark')

    const bestData = analysis.value.best_teammates.slice(0, 10) // 最多显示10个
    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        textStyle: { color: '#fff' },
        formatter: (params: any) => {
          const data = bestData[params.dataIndex]
          return `
            <div style="padding: 8px;">
              <div><strong>${data.name || `玩家${data.account_id}`}</strong></div>
              <div>账号ID: ${data.account_id}</div>
              <div>组队次数: ${data.team_count}</div>
              <div>胜利: ${data.win_count}场</div>
              <div>失败: ${data.loss_count}场</div>
              <div>胜率: ${data.win_rate.toFixed(1)}%</div>
            </div>
          `
        },
      },
      grid: {
        left: '15%',
        right: '10%',
        top: '10%',
        bottom: '15%',
      },
      xAxis: {
        type: 'value',
        name: '胜场数',
        nameTextStyle: { color: '#999' },
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.3)' } },
        axisLabel: { color: '#999' },
      },
      yAxis: {
        type: 'category',
        data: bestData.map((t) => t.name || `玩家${t.account_id}`),
        nameTextStyle: { color: '#999' },
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.3)' } },
        axisLabel: { color: '#999', fontSize: 10 },
      },
      series: [
        {
          type: 'bar',
          data: bestData.map((t) => t.win_count),
          itemStyle: {
            color: '#4a90e2',
          },
          label: {
            show: true,
            position: 'right',
            color: '#fff',
            formatter: '{c}场',
          },
        },
      ],
    }
    bestTeammatesChart.setOption(option)
  }

  // 渲染最爱损友图表
  if (analysis.value.worst_teammates.length > 0 && worstTeammatesChartRef.value) {
    if (worstTeammatesChart) {
      worstTeammatesChart.dispose()
    }
    worstTeammatesChart = echarts.init(worstTeammatesChartRef.value, 'dark')

    const worstData = analysis.value.worst_teammates.slice(0, 10) // 最多显示10个
    const option = {
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: 'rgba(255, 255, 255, 0.2)',
        textStyle: { color: '#fff' },
        formatter: (params: any) => {
          const data = worstData[params.dataIndex]
          return `
            <div style="padding: 8px;">
              <div><strong>${data.name || `玩家${data.account_id}`}</strong></div>
              <div>账号ID: ${data.account_id}</div>
              <div>组队次数: ${data.team_count}</div>
              <div>胜利: ${data.win_count}场</div>
              <div>失败: ${data.loss_count}场</div>
              <div>胜率: ${data.win_rate.toFixed(1)}%</div>
            </div>
          `
        },
      },
      grid: {
        left: '15%',
        right: '10%',
        top: '10%',
        bottom: '15%',
      },
      xAxis: {
        type: 'value',
        name: '败场数',
        nameTextStyle: { color: '#999' },
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.3)' } },
        axisLabel: { color: '#999' },
      },
      yAxis: {
        type: 'category',
        data: worstData.map((t) => t.name || `玩家${t.account_id}`),
        nameTextStyle: { color: '#999' },
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.3)' } },
        axisLabel: { color: '#999', fontSize: 10 },
      },
      series: [
        {
          type: 'bar',
          data: worstData.map((t) => t.loss_count),
          itemStyle: {
            color: '#e24a4a',
          },
          label: {
            show: true,
            position: 'right',
            color: '#fff',
            formatter: '{c}场',
          },
        },
      ],
    }
    worstTeammatesChart.setOption(option)
  }

  // 响应式调整
  window.addEventListener('resize', () => {
    bestTeammatesChart?.resize()
    worstTeammatesChart?.resize()
  })
}

onMounted(() => {
  // 组件挂载后可以做一些初始化工作
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  padding: 40px 0;
  position: relative;
  overflow-x: hidden;
}

/* Dota2背景轮播 */
.background-carousel {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}

.bg-slide {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 0;
  animation: backgroundFade 16s infinite;
  filter: blur(1px) brightness(0.5);
  z-index: 0;
}

/* 为每个背景图片添加遮罩层 */
.bg-slide::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.3));
  z-index: 1;
}

.bg-slide-1 {
  background-image: url('/4093acdbbad01c89357dea1e63d7115a1590566293.jpg');
  animation-delay: 0s;
}

.bg-slide-2 {
  background-image: url('/d2d3ca9b5ecd16a224a7a1110bd499cc1590566379.jpg');
  animation-delay: 4s;
}

.bg-slide-3 {
  background-image: url('/d7b1f56bb9d2ccb542e55481d9493bff1590566087.jpg');
  animation-delay: 8s;
}

.bg-slide-4 {
  /* 使用第1张图片作为第4张，实现循环 */
  background-image: url('/4093acdbbad01c89357dea1e63d7115a1590566293.jpg');
  animation-delay: 12s;
}


@keyframes backgroundFade {
  0% {
    opacity: 0;
  }
  2% {
    opacity: 1;
  }
  21% {
    opacity: 1;
  }
  25% {
    opacity: 0;
  }
  100% {
    opacity: 0;
  }
}

.container {
  position: relative;
  z-index: 1;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.title {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 24px;
}

.search-box {
  display: flex;
  gap: 12px;
  max-width: 500px;
  margin: 0 auto;
}

.search-box .input {
  flex: 1;
  min-width: 0;
}

.search-box .btn {
  min-width: 100px;
}

.error-message {
  background-color: rgba(226, 74, 74, 0.1);
  border-color: var(--color-danger);
  color: var(--color-danger);
  text-align: center;
  margin-bottom: 24px;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.comment-card {
  text-align: center;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.comment-text {
  font-size: 18px;
  font-weight: 500;
  color: var(--color-success);
}

.chart-card {
  min-height: 400px;
}

.chart-container {
  width: 100%;
  height: 350px;
}

.teammates-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.teammate-card {
  min-height: 300px;
}

.chart-container-small {
  width: 100%;
  height: 250px;
}

.empty-state {
  text-align: center;
  color: var(--text-muted);
  padding: 40px 20px;
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.stat-avg {
  font-size: 14px;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .title {
    font-size: 24px;
  }

  .search-box {
    flex-direction: column;
  }

  .teammates-section {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }
}

/* 版权和作者信息 */
.footer {
  margin-top: 60px;
  padding: 30px 0;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.copyright {
  color: var(--text-muted);
  font-size: 14px;
  margin: 0;
}

.author {
  color: var(--text-muted);
  font-size: 12px;
  margin: 0;
  opacity: 0.7;
}

@media (max-width: 768px) {
  .footer {
    margin-top: 40px;
    padding: 20px 0;
  }
  
  .copyright,
  .author {
    font-size: 12px;
  }
}
</style>

