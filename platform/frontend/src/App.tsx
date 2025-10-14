// 💻 Tech Lead + 🎨 UX Especialist: App principal
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Box } from '@chakra-ui/react'
import HomePage from '@/pages/HomePage'
import QuestionnairePage from '@/pages/QuestionnairePage'
import ResultsPage from '@/pages/ResultsPage'

function App() {
  return (
    <BrowserRouter>
      <Box minH="100vh" bg="gray.50">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/questionario" element={<QuestionnairePage />} />
          <Route path="/resultados" element={<ResultsPage />} />
        </Routes>
      </Box>
    </BrowserRouter>
  )
}

export default App

