// 💻 Tech Lead + 🎨 UX Especialist: App principal
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Box } from '@chakra-ui/react'
import HomePage from '@/pages/HomePage'
import QuestionnairePage from '@/pages/QuestionnairePage'
import ResultsPage from '@/pages/ResultsPage'
import DealershipInventoryPage from '@/pages/DealershipInventoryPage'
import { PageErrorBoundary } from '@/components/common'
import Header from '@/components/common/Header'

function App() {
  return (
    <BrowserRouter>
      <Box minH="100vh" bg="gray.50">
        <Header />
        <Box>
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
            <Route
              path="/admin/inventory"
              element={
                <PageErrorBoundary>
                  <DealershipInventoryPage />
                </PageErrorBoundary>
              }
            />
          </Routes>
        </Box>
      </Box>
    </BrowserRouter>
  )
}

export default App

