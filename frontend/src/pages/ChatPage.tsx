import { useState, useEffect } from 'react';
import { Box, Chip, CircularProgress, Stack, Typography } from '@mui/material';
import ChatPanel from '../components/ChatPanel';
import { fetchAgents, type ChatAgentData } from '../api/endpoints';

export default function ChatPage() {
  const [agents, setAgents] = useState<ChatAgentData[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAgents()
      .then((data) => {
        setAgents(data);
        if (data.length > 0) setSelectedAgent(data[0].slug);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const activeAgent = agents.find((a) => a.slug === selectedAgent);

  const welcomeMessage = activeAgent
    ? `${activeAgent.icon} ${activeAgent.description}`
    : 'Hallo! Ich bin dein AI-Assistent. Frag mich alles \u00fcber K\u00fcnstliche Intelligenz!';

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', pt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ height: 'calc(100vh - 100px)', display: 'flex', flexDirection: 'column' }}>
      {agents.length > 1 && (
        <Stack direction="row" spacing={1} sx={{ px: 2, py: 1.5 }}>
          {agents.map((agent) => (
            <Chip
              key={agent.slug}
              label={`${agent.icon} ${agent.name}`}
              onClick={() => setSelectedAgent(agent.slug)}
              variant={selectedAgent === agent.slug ? 'filled' : 'outlined'}
              sx={{
                fontWeight: 600,
                borderColor: agent.color,
                ...(selectedAgent === agent.slug && {
                  bgcolor: agent.color,
                  color: '#fff',
                  '&:hover': { bgcolor: agent.color },
                }),
              }}
            />
          ))}
          {activeAgent && (
            <Typography
              variant="caption"
              sx={{ color: 'text.secondary', alignSelf: 'center', ml: 1 }}
            >
              {activeAgent.description}
            </Typography>
          )}
        </Stack>
      )}

      <Box sx={{ flexGrow: 1, minHeight: 0 }}>
        <ChatPanel
          key={selectedAgent}
          agentSlug={selectedAgent}
          welcomeMessage={welcomeMessage}
        />
      </Box>
    </Box>
  );
}
