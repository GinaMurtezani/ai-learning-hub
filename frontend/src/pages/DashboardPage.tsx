import {
  Avatar,
  Box,
  Button,
  Card,
  Chip,
  Grid,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableRow,
  Typography,
} from '@mui/material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { RocketLaunch as RocketIcon } from '@mui/icons-material';
import StatCard from '../components/StatCard';

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

const STAT_CARDS = [
  { emoji: '\u{1F3C6}', label: 'Level', value: 1, suffix: 'Anf\u00e4nger', color: '#FFC107' },
  { emoji: '\u26A1', label: 'XP Punkte', value: 0, suffix: '/ 100', color: '#00A76F' },
  { emoji: '\u{1F525}', label: 'Streak', value: 0, suffix: 'Tage', color: '#FF5630' },
  {
    emoji: '\u2705',
    label: 'Missionen',
    value: 0,
    suffix: 'abgeschlossen',
    color: '#00B8D9',
    displayOverride: (v: number) => `${v} / 12`,
  },
];

const LEARNING_PATHS = [
  { title: 'AI Grundlagen', emoji: '\u{1F9E0}', lessons: 4, progress: 0, level: 'Einsteiger', chipColor: '#00A76F' },
  { title: 'Prompt Engineering', emoji: '\u270D\uFE0F', lessons: 3, progress: 0, level: 'Mittel', chipColor: '#FFC107' },
  { title: 'Agentic Workflows', emoji: '\u{1F916}', lessons: 5, progress: 0, level: 'Fortgeschritten', chipColor: '#FF5630' },
];

const LEADERBOARD = [
  { rank: '\u{1F947}', name: 'Anna M.', level: 5, xp: 520, color: '#FFC107' },
  { rank: '\u{1F948}', name: 'Marco L.', level: 4, xp: 410, color: '#919EAB' },
  { rank: '\u{1F949}', name: 'Sarah K.', level: 3, xp: 350, color: '#CD7F32' },
  { rank: '4', name: 'Jonas B.', level: 3, xp: 290, color: '#8E33FF' },
  { rank: '5', name: 'Lisa W.', level: 2, xp: 180, color: '#00B8D9' },
];

function SectionHeader({ title, linkText, linkTo }: { title: string; linkText: string; linkTo: string }) {
  const navigate = useNavigate();
  return (
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
      <Typography variant="h6" fontWeight={700}>{title}</Typography>
      <Typography
        variant="body2"
        sx={{ color: 'primary.main', cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
        onClick={() => navigate(linkTo)}
      >
        {linkText}
      </Typography>
    </Box>
  );
}

export default function DashboardPage() {
  const navigate = useNavigate();

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
      {/* Zone 1 — Stat Cards */}
      <Grid
        container
        spacing={3}
        sx={{ mb: 4 }}
        component={motion.div}
        variants={container}
        initial="hidden"
        animate="show"
      >
        {STAT_CARDS.map((card) => (
          <Grid size={{ xs: 12, sm: 6, md: 3 }} key={card.label} component={motion.div} variants={fadeUp}>
            <StatCard {...card} />
          </Grid>
        ))}
      </Grid>

      {/* Zone 2 — Learning Paths */}
      <Box sx={{ mb: 4 }}>
        <SectionHeader title="Lernpfade" linkText="Alle anzeigen" linkTo="/learn" />
        <Grid
          container
          spacing={3}
          component={motion.div}
          variants={container}
          initial="hidden"
          animate="show"
        >
          {LEARNING_PATHS.map((path) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={path.title} component={motion.div} variants={fadeUp}>
              <Card
                sx={{
                  p: 3,
                  cursor: 'pointer',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': { transform: 'translateY(-2px)', boxShadow: `0 8px 24px ${path.chipColor}22` },
                }}
                onClick={() => navigate('/learn')}
              >
                <Typography variant="h3" sx={{ mb: 1 }}>{path.emoji}</Typography>
                <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 0.5 }}>{path.title}</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <Chip
                    label={path.level}
                    size="small"
                    sx={{ bgcolor: `${path.chipColor}22`, color: path.chipColor, fontWeight: 600 }}
                  />
                  <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                    {path.lessons} Lektionen
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={path.progress}
                  sx={{
                    height: 6,
                    borderRadius: 3,
                    bgcolor: 'rgba(255,255,255,0.08)',
                    '& .MuiLinearProgress-bar': { bgcolor: path.chipColor, borderRadius: 3 },
                  }}
                />
                <Typography variant="caption" sx={{ color: 'text.secondary', mt: 1, display: 'block' }}>
                  {path.progress}% abgeschlossen
                </Typography>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Zone 3 — Leaderboard + Next Mission */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 7 }}>
          <Card sx={{ p: 3 }}>
            <SectionHeader title="Top Lernende" linkText="Alle anzeigen" linkTo="/leaderboard" />
            <Table size="small">
              <TableBody>
                {LEADERBOARD.map((entry) => (
                  <TableRow key={entry.name} sx={{ '&:last-child td': { borderBottom: 0 } }}>
                    <TableCell sx={{ width: 40, pl: 0 }}>
                      <Typography variant="body1">{entry.rank}</Typography>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: entry.color, fontSize: 14 }}>
                          {entry.name.split(' ').map((n) => n[0]).join('')}
                        </Avatar>
                        <Typography variant="body2" fontWeight={600}>{entry.name}</Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        Level {entry.level}
                      </Typography>
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" sx={{ color: 'primary.main', fontWeight: 600 }}>
                        {entry.xp} XP
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </Grid>

        <Grid size={{ xs: 12, md: 5 }}>
          <Card
            sx={{
              p: 4,
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              alignItems: 'center',
              textAlign: 'center',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <Box
              sx={{
                position: 'absolute',
                inset: 0,
                background: 'radial-gradient(circle at bottom left, rgba(0,167,111,0.12) 0%, transparent 70%)',
                pointerEvents: 'none',
              }}
            />
            <RocketIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>
              N\u00e4chste Mission
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 3, maxWidth: 280 }}>
              Starte deine Reise mit den AI Grundlagen
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/learn')}
              sx={{
                px: 4,
                fontWeight: 700,
                bgcolor: 'primary.main',
                '&:hover': { bgcolor: '#009961' },
              }}
            >
              Jetzt starten
            </Button>
          </Card>
        </Grid>
      </Grid>
    </motion.div>
  );
}
