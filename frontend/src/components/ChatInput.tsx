import { useState, type KeyboardEvent } from 'react';
import { Box, IconButton, TextField } from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export default function ChatInput({ onSend, disabled = false, placeholder = 'Nachricht schreiben...' }: ChatInputProps) {
  const [value, setValue] = useState('');

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
      <TextField
        fullWidth
        multiline
        maxRows={3}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        size="small"
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: 2,
            bgcolor: 'background.default',
          },
        }}
      />
      <IconButton
        onClick={handleSend}
        disabled={disabled || !value.trim()}
        color="primary"
        sx={{
          bgcolor: 'primary.main',
          color: '#fff',
          '&:hover': { bgcolor: '#009961' },
          '&.Mui-disabled': { bgcolor: 'action.disabledBackground' },
          width: 40,
          height: 40,
        }}
      >
        <SendIcon fontSize="small" />
      </IconButton>
    </Box>
  );
}
