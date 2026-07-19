import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useProjectStore = defineStore('project', () => {
  const currentId = ref(null)
  const currentName = ref('')
  const dataFiles = ref([])
  const selectedDataFiles = ref([])

  // LangGraph workflow state
  const workflowState = ref({
    plan: [],
    currentStepIndex: 0,
    results: [],
    contextSummary: '',
    nextAction: 'execute',
    errorMessage: '',
    ragContext: '',
    conclusion: '',
  })

  const chatHistory = ref([])
  const isRunning = ref(false)
  const currentTokens = ref('')
  const reportPreviewMode = ref(false)

  // Computed
  const steps = computed(() => workflowState.value.plan || [])
  const doneSteps = computed(() => steps.value.filter(s => s.status === 'done'))
  const allDoneSteps = computed(() => doneSteps.value)
  const totalRows = computed(() => selectedDataFiles.value.length)

  function setProject(id, name) {
    currentId.value = id
    currentName.value = name
  }

  function updateFromGraphEvent(eventType, payload) {
    switch (eventType) {
      case 'chain_end':
        if (payload && payload.state_update) {
          const update = payload.state_update
          if (update.plan) workflowState.value.plan = update.plan
          if (update.current_step_index !== undefined)
            workflowState.value.currentStepIndex = update.current_step_index
          if (update.results) workflowState.value.results = update.results
          if (update.context_summary) workflowState.value.contextSummary = update.context_summary
          if (update.next_action) workflowState.value.nextAction = update.next_action
          if (update.error_message !== undefined)
            workflowState.value.errorMessage = update.error_message
          if (update.rag_context) workflowState.value.ragContext = update.rag_context
          if (update.conclusion) workflowState.value.conclusion = update.conclusion
        }
        break
      case 'done':
        isRunning.value = false
        break
      case 'error':
        workflowState.value.errorMessage = payload
        isRunning.value = false
        break
    }
  }

  function addChatMessage(msg) {
    chatHistory.value.push(msg)
  }

  function clearProject() {
    currentId.value = null
    currentName.value = ''
    dataFiles.value = []
    selectedDataFiles.value = []
    workflowState.value = {
      plan: [], currentStepIndex: 0, results: [],
      contextSummary: '', nextAction: 'execute',
      errorMessage: '', ragContext: '', conclusion: '',
    }
    chatHistory.value = []
    currentTokens.value = ''
    reportPreviewMode.value = false
  }

  return {
    currentId, currentName, dataFiles, selectedDataFiles,
    workflowState, chatHistory, isRunning, currentTokens,
    reportPreviewMode, steps, doneSteps, allDoneSteps, totalRows,
    setProject, updateFromGraphEvent, addChatMessage, clearProject,
  }
})
