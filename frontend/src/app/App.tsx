import { ThemeProvider } from "@emotion/react"
import CssBaseline from "@mui/material/CssBaseline"
import { QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from "react-hot-toast"
import { Route, Routes } from "react-router-dom"
import AuthPhonePage from "../pages/AuthPage/AuthPhonePage"
import AuthVerifyPage from "../pages/AuthPage/AuthVerifyPage"
import HomePage from "../pages/HomePage/HomePage"
import NotFoundPage from "../pages/NotFoundPage/NotFoundPage"
import { queryClient } from "../shared/api/queryClient"
import theme from "./theme"

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Toaster
          toastOptions={{
            className: '',
            style: {
              background: '#151515',
              color: '#fff',
            }
          }}
        />

        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/auth/phone" element={<AuthPhonePage />} />
          <Route path="/auth/verify" element={<AuthVerifyPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
