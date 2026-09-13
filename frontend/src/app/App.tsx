import { ThemeProvider } from "@emotion/react"
import CssBaseline from "@mui/material/CssBaseline"
import { QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from "react-hot-toast"
import { Navigate, Route, Routes } from "react-router-dom"
import AuthPhonePage from "../pages/Auth/AuthPhonePage"
import AuthVerifyPage from "../pages/Auth/AuthVerifyPage"
import AddFriendPage from "../pages/Chats/AddFriendPage"
import ChatsLayout from "../pages/Chats/ChatLayout"
import HomePage from "../pages/HomePage/HomePage"
import NotFoundPage from "../pages/NotFoundPage/NotFoundPage"
import ProfileCustomizationPage from "../pages/Auth/ProfileSettingsPage"
import { queryClient } from "../shared/api/queryClient"
import { LoginRequiredRoute } from "../shared/routes/LoginRequiredRoute"
import { NoLoginRequiredRoute } from "../shared/routes/NoLoginRequiredRoute"
import { ProfileRequiredRoute } from "../shared/routes/ProfileRequiredRoute"
import { theme, toastTheme } from "./theme"
import ChatPage from "../pages/Chats/ChatPage/ChatPage"

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Toaster
          toastOptions={toastTheme}
        />

        <Routes>
          <Route path="/" element={<HomePage />} />

          <Route path="/auth" element={<NoLoginRequiredRoute />}>
            <Route index element={<Navigate to="/auth/phone" />} />
            <Route path="phone" element={<AuthPhonePage />} />
            <Route path="verify" element={<AuthVerifyPage />} />
          </Route>


          <Route element={<LoginRequiredRoute />}>
            <Route path="/profile/me" element={<ProfileCustomizationPage />} />

            <Route element={<ProfileRequiredRoute />}>
              <Route path="/chats" element={<ChatsLayout />}>
                <Route index element={<AddFriendPage />} />
                <Route path=":uuid" element={<ChatPage />} />
              </Route>
            </Route>
          </Route>

          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </ThemeProvider>
    </QueryClientProvider>
  )
}

export default App
