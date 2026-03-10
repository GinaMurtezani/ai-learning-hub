import { useEffect, useState } from 'react';
import {
  Avatar,
  Box,
  Button,
  Card,
  Chip,
  Grid,
  LinearProgress,
  Skeleton,
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
import { fetchProfile, fetchPaths, fetchLeaderboard } from '../api/endpoints';

interface ProfileData {
  xp: number;
  level: number;
  streak_days: number;
}

interface PathData {
  id: number;
  slug: string;
  title: string;
  icon: string;
  difficulty: string;
  lessons_count: number;
  completed_count: number;
  progress_percent: number;
}

interface LeaderboardEntry {
  id: number;
  username: string;
  display_name: string;
  xp: number;
  level: number;
  avatar_color: string;
}

const DIFFICULTY_LABELS: Record<string, string> = {
  beginner: 'Einsteiger',
  intermediate: 'Mittel',
  advanced: 'Fortgeschritten',
};

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: '#00A76F',
  intermediate: '#FFC107',
  advanced: '#FF5630',
};

const LEVEL_NAMES: Record<number, string> = {
  1: 'Anfaenger',
  2: 'Entdecker',
  3: 'Fortgeschritten',
  4: 'Experte',
  5: 'Meister',
};

const MEDALS: Record<number, string> = { 1: '\u{1F947}', 2: '\u{1F948}', 3: '\u{1F949}' };

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

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

function StatSkeleton() {
  return (
    <>
      {Array.from({ length: 4 }).map((_, i) => (
        <Grid size={{ xs: 12, sm: 6, md: 3 }} key={i}>
          <Card sx={{ p: 3 }}>
            <Skeleton width={40} height={40} sx={{ mb: 1 }} />
            <Skeleton width={80} height={16} sx={{ mb: 1 }} />
            <Skeleton width={100} height={32} />
          </Card>
        </Grid>
      ))}
    </>
  );
}

function PathSkeleton() {
  return (
    <>
      {Array.from({ length: 3 }).map((_, i) => (
        <Grid size={{ xs: 12, sm: 6, md: 4 }} key={i}>
          <Card sx={{ p: 3 }}>
            <Skeleton width={48} height={48} sx={{ mb: 1 }} />
            <Skeleton width="60%" height={24} sx={{ mb: 1 }} />
            <Skeleton width="40%" height={16} sx={{ mb: 2 }} />
            <Skeleton height={6} sx={{ borderRadius: 3 }} />
          </Card>
        </Grid>
      ))}
    </>
  );
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [paths, setPaths] = useState<PathData[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchProfile(), fetchPaths(), fetchLeaderboard()])
      .then(([p, pa, lb]) => {
        setProfile(p);
        setPaths(pa);
        setLeaderboard(lb.slice(0, 5));
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const totalLessons = paths.reduce((s, p) => s + p.lessons_count, 0);
  const completedLessons = paths.reduce((s, p) => s + p.completed_count, 0);

  const statCards = profile
    ? [
        { emoji: '\u{1F3C6}', label: 'Level', value: profile.level, suffix: LEVEL_NAMES[profile.level] || '', color: '#FFC107' },
        { emoji: '\u26A1', label: 'XP Punkte', value: profile.xp, suffix: `/ ${(profile.level) * 100}`, color: '#00A76F' },
        { emoji: '\u{1F525}', label: 'Streak', value: profile.streak_days, suffix: 'Tage', color: '#FF5630' },
        {
          emoji: '\u2705',
          label: 'Missionen',
          value: completedLessons,
          suffix: 'abgeschlossen',
          color: '#00B8D9',
          displayOverride: (v: number) => `${v} / ${totalLessons}`,
        },
      ]
    : [];

  // Find first incomplete path for "next mission"
  const nextPath = paths.find((p) => p.progress_percent < 100);

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
        {loading ? (
          <StatSkeleton />
        ) : (
          statCards.map((card) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={card.label} component={motion.div} variants={fadeUp}>
              <StatCard {...card} />
            </Grid>
          ))
        )}
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
          {loading ? (
            <PathSkeleton />
          ) : (
            paths.slice(0, 3).map((path) => {
              const chipColor = DIFFICULTY_COLORS[path.difficulty] || '#00A76F';
              return (
                <Grid size={{ xs: 12, sm: 6, md: 4 }} key={path.id} component={motion.div} variants={fadeUp}>
                  <Card
                    sx={{
                      p: 3,
                      cursor: 'pointer',
                      transition: 'transform 0.2s, box-shadow 0.2s',
                      '&:hover': { transform: 'translateY(-2px)', boxShadow: `0 8px 24px ${chipColor}22` },
                    }}
                    onClick={() => navigate(`/learn/${path.slug}`)}
                  >
                    <Typography variant="h3" sx={{ mb: 1 }}>{path.icon}</Typography>
                    <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 0.5 }}>{path.title}</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <Chip
                        label={DIFFICULTY_LABELS[path.difficulty] || path.difficulty}
                        size="small"
                        sx={{ bgcolor: `${chipColor}22`, color: chipColor, fontWeight: 600 }}
                      />
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        {path.lessons_count} Lektionen
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={path.progress_percent}
                      sx={{
                        height: 6,
                        borderRadius: 3,
                        bgcolor: 'rgba(255,255,255,0.08)',
                        '& .MuiLinearProgress-bar': { bgcolor: chipColor, borderRadius: 3 },
                      }}
                    />
                    <Typography variant="caption" sx={{ color: 'text.secondary', mt: 1, display: 'block' }}>
                      {path.progress_percent}% abgeschlossen
                    </Typography>
                  </Card>
                </Grid>
              );
            })
          )}
        </Grid>
      </Box>

      {/* Zone 3 — Leaderboard + Next Mission */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 7 }}>
          <Card sx={{ p: 3 }}>
            <SectionHeader title="Top Lernende" linkText="Alle anzeigen" linkTo="/leaderboard" />
            {loading ? (
              <Box sx={{ p: 2 }}>
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} height={40} sx={{ mb: 1 }} />
                ))}
              </Box>
            ) : (
              <Table size="small">
                <TableBody>
                  {leaderboard.map((entry, idx) => {
                    const rank = idx + 1;
                    const initials = entry.display_name
                      .split(' ')
                      .map((n) => n[0])
                      .join('')
                      .slice(0, 2);
                    return (
                      <TableRow key={entry.id} sx={{ '&:last-child td': { borderBottom: 0 } }}>
                        <TableCell sx={{ width: 40, pl: 0 }}>
                          <Typography variant="body1">{MEDALS[rank] || String(rank)}</Typography>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <Avatar sx={{ width: 32, height: 32, bgcolor: entry.avatar_color, fontSize: 14 }}>
                              {initials}
                            </Avatar>
                            <Typography variant="body2" fontWeight={600}>{entry.display_name}</Typography>
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
                    );
                  })}
                </TableBody>
              </Table>
            )}
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
              N&auml;chste Mission
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary', mb: 3, maxWidth: 280 }}>
              {nextPath
                ? `${nextPath.icon} ${nextPath.title} — ${nextPath.completed_count}/${nextPath.lessons_count} Lektionen`
                : 'Starte deine Reise mit den AI Grundlagen'}
            </Typography>
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate(nextPath ? `/learn/${nextPath.slug}` : '/learn')}
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
