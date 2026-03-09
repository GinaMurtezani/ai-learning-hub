import { Box, Typography } from '@mui/material';
import { motion } from 'framer-motion';

interface ChatBubbleProps {
  message: string;
  role: 'user' | 'assistant';
}

export default function ChatBubble({ message, role }: ChatBubbleProps) {
  const isUser = role === 'user';

  return (
    <Box
      component={motion.div}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 1.5,
      }}
    >
      <Box
        sx={{
          maxWidth: '80%',
          px: 2,
          py: 1.5,
          bgcolor: isUser ? 'primary.main' : 'background.paper',
          color: isUser ? '#fff' : 'text.primary',
          borderRadius: isUser
            ? '16px 16px 4px 16px'
            : '16px 16px 16px 4px',
          wordBreak: 'break-word',
        }}
      >
        <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
          {message}
        </Typography>
      </Box>
    </Box>
  );
}
