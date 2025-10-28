// 💻 Tech Lead + 🎨 UX Especialist: App principal
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Box } from '@chakra-ui/react'
import HomePage from '@/pages/HomePage'
import QuestionnairePage from '@/pages/QuestionnairePage'
import ResultsPage from '@/pages/ResultsPage'
import { PageErrorBoundary } from '@/components/common'

function App() {
  return (
    <BrowserRouter>
      <Box minH="100vh" bg="gray.50">
        <Routes>
          <Route
            path="/"
            element={
              <PageErrorBoundary>
                <HomePage />
              </PageErrorBoundary>
            }
          />
          <Route
            path="/questionario"
            element={
              <PageErrorBoundary>
                <QuestionnairePage />
              </PageErrorBoundary>
            }
          />
          <Route
            path="/resultados"
            element={
              <PageErrorBoundary>
                <ResultsPage />
              </PageErrorBoundary>
            }
          />
        </Routes>
      </Box>
    </BrowserRouter>
  )
}

export default App

