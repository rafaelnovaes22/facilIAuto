import { Routes, Route } from 'react-router-dom'
import { Box } from '@chakra-ui/react'
import HomePage from './pages/HomePage'
import QuestionnairePage from './pages/QuestionnairePage'
import ResultsPage from './pages/ResultsPage'
import AboutPage from './pages/AboutPage'
import DashboardPage from './pages/DashboardPage'
import Header from './components/Header'

function App() {
  return (
    <Box minHeight="100vh" display="flex" flexDirection="column">
      <Header />
      
      <Box flex="1" as="main">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/questionario" element={<QuestionnairePage />} />
          <Route path="/resultados" element={<ResultsPage />} />
          <Route path="/sobre" element={<AboutPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </Box>
      
    </Box>
  )
}

export default App
