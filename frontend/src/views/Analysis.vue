<template>
  <div>
    <div v-if="projectStore.reportPreviewMode">
      <ReportPreview @back="projectStore.reportPreviewMode = false" />
    </div>

    <div v-else-if="!projectStore.currentId">
      <el-empty description="请先新建项目，或从侧边栏「历史项目」中打开已有项目" />
    </div>

    <div v-else>
      <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px">
        <el-button @click="showProjectInfo = true; loadProjectInfo()" type="primary" plain>
          {{ projectStore.currentName }}
        </el-button>
        <span style="color: #666; font-size: 13px">
          数据: {{ projectStore.totalRows }} 个文件
        </span>
        <div style="flex: 1" />
        <el-button @click="showUploadDialog = true">上传新数据</el-button>
        <el-button type="primary" @click="openReportDialog">导出报告</el-button>
      </div>

      <el-divider style="margin: 8px 0" />

      <div style="display: flex; gap: 12px; height: calc(100vh - 180px)">
        <!-- 左栏: 对话 (25%) -->
        <div style="width: 25%; display: flex; flex-direction: column; border: 1px solid #eee; border-radius: 8px">
          <div style="padding: 8px 12px; font-weight: 600; border-bottom: 1px solid #eee; font-size: 14px">对话</div>
          <div style="flex: 1; overflow-y: auto; padding: 8px 12px" ref="chatListEl">
            <div v-for="(msg, i) in projectStore.chatHistory" :key="i" style="margin-bottom: 10px">
              <div v-if="msg.role === 'user'" style="color: #1a73e8; font-size: 12px; margin-bottom: 2px">你</div>
              <div v-else style="color: #34a853; font-size: 12px; margin-bottom: 2px">Agent</div>
              <div :style="{
                padding: '8px 10px', borderRadius: '6px', fontSize: '13px', lineHeight: '1.5',
                background: msg.role === 'user' ? '#e8f0fe' : '#f5f5f5'
              }">{{ msg.content }}</div>
            </div>
            <div v-if="streamingResponse" style="font-size: 13px; color: #666; white-space: pre-wrap">{{ streamingResponse }}</div>
          </div>
          <div style="padding: 8px; border-top: 1px solid #eee">
            <el-input v-model="userInput" placeholder="描述你的分析需求..." @keyup.enter="sendMessage" :disabled="projectStore.isRunning" />
            <el-button type="primary" @click="sendMessage" :loading="projectStore.isRunning" style="margin-top: 6px; width: 100%">
              {{ projectStore.isRunning ? '分析中...' : '发送' }}
            </el-button>
          </div>
        </div>

        <!-- 中栏: 结果 (50%) -->
        <div style="width: 50%; border: 1px solid #eee; border-radius: 8px; display: flex; flex-direction: column">
          <div style="padding: 8px 12px; font-weight: 600; border-bottom: 1px solid #eee; font-size: 14px">
            分析结果
            <span v-if="projectStore.workflowState.currentStepIndex > 0" style="color: #999; font-size: 12px; margin-left: 8px">
              (步骤 {{ projectStore.workflowState.currentStepIndex }}/{{ projectStore.steps.length }})
            </span>
          </div>
          <div style="flex: 1; overflow-y: auto; padding: 12px">
            <div v-if="projectStore.workflowState.conclusion" style="margin-bottom: 12px">
              <div style="background: #e6f4ea; border-left: 3px solid #34a853; padding: 10px 12px; border-radius: 4px; font-size: 13px; white-space: pre-wrap">
                <b>综合分析结论:</b>
                <div v-html="renderMarkdown(projectStore.workflowState.conclusion)"></div>
              </div>
            </div>
            <div v-if="projectStore.workflowState.errorMessage" style="margin-bottom: 12px">
              <el-alert type="error" :title="projectStore.workflowState.errorMessage" :closable="false" />
            </div>
            <div v-if="!projectStore.workflowState.results.length && !projectStore.workflowState.conclusion"
                 style="color: #999; display: flex; align-items: center; justify-content: center; height: 100%">
              在对话区描述你的分析需求，Agent 将自动规划并执行分析
            </div>
            <div v-for="(result, i) in projectStore.workflowState.results" :key="i" style="margin-bottom: 10px">
              <el-card shadow="hover">
                <template #header>
                  <span>{{ result.description || '步骤 ' + (result.step_id || i + 1) }}</span>
                  <el-tag size="small" :type="result.status === 'done' ? 'success' : 'danger'" style="margin-left: 8px">
                    {{ result.status === 'done' ? '完成' : '失败' }}
                  </el-tag>
                </template>
                <div v-if="result.text" v-html="renderMarkdown(tryParseToolResult(result.text))" style="font-size: 13px"></div>
              </el-card>
            </div>
          </div>
        </div>

        <!-- 右栏: 分析步骤 (25%) -->
        <div style="width: 25%; border: 1px solid #eee; border-radius: 8px; display: flex; flex-direction: column">
          <div style="padding: 8px 12px; font-weight: 600; border-bottom: 1px solid #eee; font-size: 14px">分析步骤 (LangGraph)</div>
          <div style="flex: 1; overflow-y: auto; padding: 8px">
            <div v-if="!projectStore.steps.length" style="color: #999; text-align: center; margin-top: 20px; font-size: 13px">
              发送分析需求后，AI 将自动生成计划
            </div>
            <el-steps v-else direction="vertical" :active="projectStore.workflowState.currentStepIndex">
              <el-step
                v-for="(step, i) in projectStore.steps"
                :key="i"
                :title="step.description || '步骤 ' + (i + 1)"
                :status="step.status === 'done' ? 'success' : step.status === 'running' ? 'process' : 'wait'"
              />
            </el-steps>
          </div>
        </div>
      </div>
    </div>

    <!-- Dialogs (reused from project1) -->
    <el-dialog v-model="showProjectInfo" title="项目信息" width="400px">
      <el-descriptions v-if="projectInfo" :column="2" border size="small">
        <el-descriptions-item label="名称">{{ projectInfo.name }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ (projectInfo.created_at || '').slice(0, 19) }}</el-descriptions-item>
        <el-descriptions-item label="数据文件">{{ projectInfo.data_files_count }} 个</el-descriptions-item>
        <el-descriptions-item label="总行数">{{ (projectInfo.total_rows || 0).toLocaleString() }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <el-dialog v-model="showUploadDialog" title="向当前项目追加数据" width="500px">
      <el-upload drag :auto-upload="false" :on-change="handleUploadFile" accept=".csv,.xlsx,.xls" :limit="1">
        <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
      </el-upload>
      <div v-if="uploading" style="text-align: center; margin-top: 10px">上传中...</div>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmUpload" :disabled="!pendingUploadFile2" :loading="uploading">确认追加</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showReportDialog" title="导出分析报告" width="550px">
      <el-input v-model="reportTitle" placeholder="报告标题" style="margin-bottom: 16px" />
      <el-input v-model="reportUserNotes" type="textarea" :rows="3" placeholder="工程师补充观点（可选）" style="margin-bottom: 16px" />
      <template #footer>
        <el-button @click="showReportDialog = false">取消</el-button>
        <el-button type="primary" @click="generateAndPreview" :loading="generatingReport">
          AI 结论并预览
        </el-button>
        <el-button type="success" @click="exportReport" :loading="generatingReport">
          导出 HTML
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  getProjectInfo, addDataFile, generateReport,
  streamAnalysis, streamConclude,
} from '../api'
import { useProjectStore } from '../stores/project'
import { ElMessage } from 'element-plus'
import DOMPurify from 'dompurify'
import ReportPreview from './ReportPreview.vue'

const projectStore = useProjectStore()

const userInput = ref('')
const streamingResponse = ref('')
const showProjectInfo = ref(false)
const projectInfo = ref(null)
const showUploadDialog = ref(false)
const pendingUploadFile2 = ref(null)
const uploading = ref(false)
const showReportDialog = ref(false)
const reportTitle = ref('')
const reportUserNotes = ref('')
const generatingReport = ref(false)

const sendMessage = async () => {
  if (!userInput.value.trim() || projectStore.isRunning) return
  const msg = userInput.value.trim()
  userInput.value = ''
  projectStore.addChatMessage({ role: 'user', content: msg })

  projectStore.isRunning = true
  streamingResponse.value = ''
  let fullPlan = ''

  try {
    await streamAnalysis(projectStore.currentId, msg, {
      onLlmToken: (token) => {
        fullPlan += token
        streamingResponse.value = fullPlan
      },
      onToolStart: (tool) => {
        projectStore.addChatMessage({ role: 'agent', content: `执行工具: ${tool}` })
        // Mark current step as running
        const idx = projectStore.workflowState.currentStepIndex
        const plan = projectStore.workflowState.plan
        if (idx < plan.length) {
          plan[idx] = { ...plan[idx], status: 'running' }
        }
      },
      onToolEnd: (tool, output) => {
        if (output && !output.success) {
          projectStore.addChatMessage({ role: 'agent', content: `${tool} 执行异常: ${output.error}` })
        }
      },
      onNodeEnd: (node, stateUpdate) => {
        if (stateUpdate) {
          projectStore.updateFromGraphEvent('chain_end', stateUpdate)
          streamingResponse.value = stateUpdate.context_summary || stateUpdate.conclusion || ''
        }
      },
      onDone: () => {
        projectStore.isRunning = false
        const conclusion = projectStore.workflowState.conclusion
        if (conclusion) {
          projectStore.addChatMessage({ role: 'agent', content: conclusion })
        } else {
          projectStore.addChatMessage({ role: 'agent', content: fullPlan || '分析完成' })
        }
        streamingResponse.value = ''
      },
      onError: (msg) => {
        projectStore.isRunning = false
        projectStore.updateFromGraphEvent('error', msg)
        ElMessage.error('分析失败: ' + msg)
      },
    })
  } catch (e) {
    projectStore.isRunning = false
    ElMessage.error('请求失败: ' + e.message)
  }
}

const loadProjectInfo = async () => {
  if (!projectStore.currentId) return
  try {
    const res = await getProjectInfo(projectStore.currentId)
    projectInfo.value = res.data
  } catch (e) {
    ElMessage.error('加载项目信息失败')
  }
}

const handleUploadFile = (file) => { pendingUploadFile2.value = file.raw }

const confirmUpload = async () => {
  if (!pendingUploadFile2.value) return
  uploading.value = true
  try {
    const res = await addDataFile(projectStore.currentId, pendingUploadFile2.value)
    projectStore.dataFiles = res.data.data_files || []
    showUploadDialog.value = false
    pendingUploadFile2.value = null
    ElMessage.success('数据已追加，请重新描述分析需求以使用新数据')
  } catch (e) {
    ElMessage.error('追加失败: ' + e.message)
  } finally {
    uploading.value = false
  }
}

const openReportDialog = () => {
  reportTitle.value = `${projectStore.currentName} 分析报告`
  reportUserNotes.value = ''
  showReportDialog.value = true
}

const generateAndPreview = async () => {
  generatingReport.value = true
  showReportDialog.value = false
  let conclusionText = ''
  try {
    await streamConclude(projectStore.currentId, reportUserNotes.value, {
      onToken: (chunk) => { conclusionText += chunk },
      onDone: () => {},
      onError: (msg) => { ElMessage.warning('AI 结论生成失败: ' + msg) },
    })
  } catch (e) {
    ElMessage.warning('AI 结论生成失败')
  }

  try {
    await generateReport(projectStore.currentId, reportTitle.value, reportUserNotes.value)
    if (conclusionText) {
      projectStore.workflowState.conclusion = conclusionText
    }
    projectStore.reportPreviewMode = true
  } catch (e) {
    ElMessage.error('生成失败: ' + e.message)
  } finally {
    generatingReport.value = false
  }
}

const exportReport = async () => {
  generatingReport.value = true
  try {
    const res = await generateReport(projectStore.currentId, reportTitle.value, reportUserNotes.value)
    ElMessage.success('报告已保存: ' + (res.data.path || 'OK'))
    showReportDialog.value = false
  } catch (e) {
    ElMessage.error('生成失败: ' + e.message)
  } finally {
    generatingReport.value = false
  }
}

const tryParseToolResult = (text) => {
  if (!text) return ''
  try {
    const data = typeof text === 'string' ? JSON.parse(text) : text
    if (Array.isArray(data) && data.length > 0 && data[0].tool) {
      return data.map(d => `【${d.tool}】${d.result?.success ? '(成功)' : '(失败: ' + (d.result?.error || '') + ')'}`).join('\n')
    }
  } catch (_) { /* pass */ }
  return text
}

const renderMarkdown = (text) => {
  if (!text) return ''
  let html = String(text)
    .replace(/### (.+)/g, '<h4>$1</h4>')
    .replace(/## (.+)/g, '<h3>$1</h3>')
    .replace(/- (.+)/g, '<li>$1</li>')
    .replace(/```json\n?([\s\S]*?)```/g, '<pre style="background:#f5f5f5;padding:8px;border-radius:4px;font-size:12px">$1</pre>')
    .replace(/\n\n/g, '<br/><br/>')
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: ['h3', 'h4', 'li', 'pre', 'br', 'strong', 'em', 'code', 'b', 'i', 'ul', 'ol', 'p', 'span'],
    ALLOWED_ATTRS: ['style'],
  })
}
</script>
