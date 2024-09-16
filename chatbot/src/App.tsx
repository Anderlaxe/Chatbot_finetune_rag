import { Box, useTheme } from '@mui/material'
import { Chatbot } from './components/Chatbot';

function App() {
  const theme = useTheme();

  return (
    // Box qui fait toute la taille qui contient le bouton en bas à droite
    // Composants : MainPage, Chatbot (qui contient boîte et bouton), ChatbotButton, ChatbotBox, Message (avec des conditions pour User et Chatbot), TopBar, InputBox
    <Box sx={{
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      width: '100vw',
      bgcolor: theme.palette.common.white,
      color: 'white',
      fontSize: '3rem',
      fontWeight: 'bold',
    }}>
      <Chatbot />
    </Box>
  )
}

export default App
