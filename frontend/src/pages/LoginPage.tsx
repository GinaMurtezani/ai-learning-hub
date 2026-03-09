import { useEffect, useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Alert,
  Avatar,
  Box,
  Button,
  Card,
  CircularProgress,
  Collapse,
  Grid,
  TextField,
  Typography,
} from '@mui/material';
import { SmartToy as SmartToyIcon, ExpandMore as ExpandMoreIcon } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { fetchDemoUsers } from '../api/endpoints';

interface DemoUser {
  username: string;
  display_name: string;
  avatar_color: string;
  role: string;
}

const DEMO_PASSWORDS: Record<string, string> = {
  demo: 'demo1234',
  anna: 'anna1234',
  marco: 'marco1234',
};

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

export default function LoginPage() {
  const [demoUsers, setDemoUsers] = useState<DemoUser[]>([]);
  const [loadingTile, setLoadingTile] = useState<string | null>(null);
  const [showManual, setShowManual] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchDemoUsers().then(setDemoUsers).catch(() => {});
  }, []);

  const handleTileLogin = async (user: DemoUser) => {
    setError('');
    setLoadingTile(user.username);
    try {
      const pw = DEMO_PASSWORDS[user.username];
      if (!pw) throw new Error('Unknown user');
      await login(user.username, pw);
      navigate('/');
    } catch {
      setError('Login fehlgeschlagen.');
    } finally {
      setLoadingTile(null);
    }
  };

  const handleManualSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/');
    } catch {
      setError('Login fehlgeschlagen. Pr\u00fcfe Username und Passwort.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        p: 2,
      }}
    >
      <Box sx={{ maxWidth: 600, width: '100%' }}>
        {/* Header */}
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <SmartToyIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
          <Typography variant="h4" fontWeight={700}>
            AI Learning Hub
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary', mt: 1 }}>
            Willkommen! W\u00e4hle deinen Account:
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* User Tiles */}
        <Grid
          container
          spacing={2}
          sx={{ mb: 4 }}
          component={motion.div}
          variants={container}
          initial="hidden"
          animate="show"
        >
          {demoUsers.map((user) => (
            <Grid size={{ xs: 12, sm: 4 }} key={user.username} component={motion.div} variants={fadeUp}>
              <Card
                component={motion.div}
                whileHover={{ y: -4 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => !loadingTile && handleTileLogin(user)}
                sx={{
                  p: 3,
                  textAlign: 'center',
                  cursor: loadingTile ? 'wait' : 'pointer',
                  transition: 'border-color 0.2s, box-shadow 0.2s',
                  border: '2px solid transparent',
                  '&:hover': {
                    borderColor: user.avatar_color,
                    boxShadow: `0 4px 20px ${user.avatar_color}22`,
                  },
                }}
              >
                {loadingTile === user.username ? (
                  <Box sx={{ py: 2 }}>
                    <CircularProgress size={48} sx={{ color: user.avatar_color }} />
                  </Box>
                ) : (
                  <>
                    <Avatar
                      sx={{
                        width: 64,
                        height: 64,
                        bgcolor: user.avatar_color,
                        fontSize: 24,
                        fontWeight: 700,
                        mx: 'auto',
                        mb: 1.5,
                      }}
                    >
                      {user.display_name
                        .split(' ')
                        .map((n) => n[0])
                        .join('')}
                    </Avatar>
                    <Typography variant="subtitle1" fontWeight={700}>
                      {user.display_name}
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      {user.role}
                    </Typography>
                  </>
                )}
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* Manual Login Toggle */}
        <Box sx={{ textAlign: 'center' }}>
          <Button
            size="small"
            onClick={() => setShowManual(!showManual)}
            endIcon={
              <ExpandMoreIcon
                sx={{
                  transform: showManual ? 'rotate(180deg)' : 'none',
                  transition: 'transform 0.2s',
                }}
              />
            }
            sx={{ color: 'text.secondary', textTransform: 'none' }}
          >
            Oder manuell einloggen
          </Button>
        </Box>

        <Collapse in={showManual}>
          <Card sx={{ p: 3, mt: 2 }}>
            <form onSubmit={handleManualSubmit}>
              <TextField
                fullWidth
                label="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                sx={{ mb: 2 }}
                size="small"
              />
              <TextField
                fullWidth
                label="Passwort"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                sx={{ mb: 2 }}
                size="small"
              />
              <Button
                fullWidth
                type="submit"
                variant="contained"
                disabled={loading || !username || !password}
                sx={{ fontWeight: 700 }}
              >
                {loading ? <CircularProgress size={20} color="inherit" /> : 'Anmelden'}
              </Button>
            </form>
          </Card>
        </Collapse>
      </Box>
    </Box>
  );
}
