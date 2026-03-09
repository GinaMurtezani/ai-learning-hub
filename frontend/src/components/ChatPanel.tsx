import { useState, useRef, useEffect } from 'react';
import { Box, Typography } from '@mui/material';
import { SmartToy as SmartToyIcon } from '@mui/icons-material';
import { sendChatMessage } from '../api/endpoints';
import ChatBubble from './ChatBubble';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatPanelProps {
  lessonId?: number;
  lessonTitle?: string;
  welcomeMessage?: string;
  agentSlug?: string;
}

export default function ChatPanel({
  lessonId,
  lessonTitle,
  welcomeMessage = 'Hallo! Ich bin dein AI-Assistent. Frag mich alles \u00fcber K\u00fcnstliche Intelligenz!',
  agentSlug,
}: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async (content: string) => {
    setError(null);
    setMessages((prev) => [...prev, { role: 'user', content }]);
    setIsLoading(true);

    try {
      const data = await sendChatMessage(content, lessonId, agentSlug);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.response },
      ]);
    } catch {
      setError('Nachricht konnte nicht gesendet werden.');
    } finally {
      setIsLoading(false);
    }
  };

  const title = lessonTitle ? `AI Tutor \u2014 ${lessonTitle}` : 'AI Chat \u2014 Freier Modus';

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        borderRadius: 2,
        overflow: 'hidden',
        bgcolor: 'background.paper',
      }}
    >
      {/* Header */}
      <Box
        sx={{
          px: 2,
          py: 1.5,
          borderBottom: '1px solid',
          borderColor: 'divider',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}
      >
        <SmartToyIcon sx={{ color: 'primary.main' }} />
        <Typography variant="subtitle1" fontWeight={700} noWrap>
          {title}
        </Typography>
      </Box>

      {/* Messages */}
      <Box
        ref={scrollRef}
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          p: 2,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {messages.length === 0 && !isLoading && (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              flexGrow: 1,
              textAlign: 'center',
              gap: 1,
              py: 4,
            }}
          >
            <SmartToyIcon sx={{ fontSize: 48, color: 'text.secondary' }} />
            <Typography variant="body2" sx={{ color: 'text.secondary', maxWidth: 280 }}>
              {welcomeMessage}
            </Typography>
          </Box>
        )}
        {messages.map((msg, i) => (
          <ChatBubble key={i} message={msg.content} role={msg.role} />
        ))}
        {isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
            <Box sx={{ bgcolor: 'background.paper', borderRadius: 2, px: 1 }}>
              <TypingIndicator />
            </Box>
          </Box>
        )}
        {error && (
          <Typography variant="caption" sx={{ color: 'error.main', textAlign: 'center', mt: 1 }}>
            {error}
          </Typography>
        )}
      </Box>

      {/* Input */}
      <Box sx={{ p: 2, borderTop: '1px solid', borderColor: 'divider' }}>
        <ChatInput
          onSend={handleSend}
          disabled={isLoading}
          placeholder="Stelle eine Frage..."
        />
      </Box>
    </Box>
  );
}
