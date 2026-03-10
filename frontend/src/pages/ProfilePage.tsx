import { useEffect, useState } from 'react';
import {
  Avatar,
  Box,
  Card,
  Chip,
  CircularProgress,
  Grid,
  LinearProgress,
  Typography,
} from '@mui/material';
import {
  EmojiEvents as TrophyIcon,
  CalendarMonth as CalendarIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { fetchProfile, fetchAchievements, fetchPaths } from '../api/endpoints';

interface ProfileData {
  user: { id: number; username: string; email: string };
  xp: number;
  level: number;
  streak_days: number;
  last_activity: string;
  avatar_color: string;
}

interface AchievementData {
  id: number;
  slug: string;
  name: string;
  icon: string;
  description: string;
  xp_reward: number;
  unlocked: boolean;
  unlocked_at: string | null;
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

const LEVEL_NAMES: Record<number, string> = {
  1: 'Anfaenger',
  2: 'Entdecker',
  3: 'Fortgeschritten',
  4: 'Experte',
  5: 'Meister',
  6: 'Grossmeister',
};

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: '#00A76F',
  intermediate: '#FFC107',
  advanced: '#FF5630',
};

function AnimatedValue({ value }: { value: number }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    const start = performance.now();
    const duration = 600;
    function tick(now: number) {
      const p = Math.min((now - start) / duration, 1);
      setDisplay(Math.round((1 - Math.pow(1 - p, 3)) * value));
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }, [value]);
  return <>{display}</>;
}

function StreakCalendar({ streakDays }: { streakDays: number }) {
  const today = new Date();
  const days: { date: Date; active: boolean; isToday: boolean }[] = [];
  for (let i = 29; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(d.getDate() - i);
    days.push({ date: d, active: i < streakDays, isToday: i === 0 });
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
        <CalendarIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
          Letzte 30 Tage
        </Typography>
      </Box>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(10, 1fr)',
          gap: 0.5,
        }}
      >
        {days.map((d, i) => (
          <Box
            key={i}
            title={d.date.toLocaleDateString('de-CH')}
            sx={{
              width: '100%',
              aspectRatio: '1',
              borderRadius: 0.5,
              bgcolor: d.active ? '#00A76F' : 'rgba(255,255,255,0.04)',
              border: d.isToday ? '2px solid #FFC107' : '2px solid transparent',
              transition: 'background-color 0.2s',
            }}
          />
        ))}
      </Box>
    </Box>
  );
}

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

export default function ProfilePage() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [achievements, setAchievements] = useState<AchievementData[]>([]);
  const [paths, setPaths] = useState<PathData[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([fetchProfile(), fetchAchievements(), fetchPaths()])
      .then(([p, a, pa]) => {
        setProfile(p);
        setAchievements(a);
        setPaths(pa);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', pt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!profile) {
    return (
      <Typography color="error">Profil konnte nicht geladen werden.</Typography>
    );
  }

  const initials = profile.user.username.slice(0, 2).toUpperCase();
  const xpInLevel = profile.xp % 100;
  const xpToNext = 100;
  const levelName = LEVEL_NAMES[profile.level] || `Level ${profile.level}`;
  const unlockedAchievements = achievements
    .filter((a) => a.unlocked)
    .sort((a, b) => {
      if (!a.unlocked_at || !b.unlocked_at) return 0;
      return new Date(b.unlocked_at).getTime() - new Date(a.unlocked_at).getTime();
    })
    .slice(0, 3);

  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={{ hidden: {}, show: { transition: { staggerChildren: 0.1 } } }}
    >
      <Grid container spacing={3}>
        {/* Left Column — Profile Card */}
        <Grid size={{ xs: 12, md: 5 }} component={motion.div} variants={fadeUp}>
          <Card sx={{ p: 4, textAlign: 'center' }}>
            <Avatar
              sx={{
                width: 120,
                height: 120,
                bgcolor: profile.avatar_color,
                fontSize: 48,
                fontWeight: 700,
                mx: 'auto',
                mb: 2,
              }}
            >
              {initials}
            </Avatar>
            <Typography variant="h5" fontWeight={700}>
              {profile.user.username}
            </Typography>
            {profile.user.email && (
              <Typography variant="body2" sx={{ color: 'text.secondary', mt: 0.5 }}>
                {profile.user.email}
              </Typography>
            )}
            <Chip
              label={`Level ${profile.level} — ${levelName}`}
              sx={{
                mt: 2,
                fontWeight: 600,
                bgcolor: 'rgba(142, 51, 255, 0.12)',
                color: '#8E33FF',
              }}
            />
            <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary', mt: 2 }}>
              Zuletzt aktiv: {new Date(profile.last_activity).toLocaleDateString('de-CH')}
            </Typography>
          </Card>
        </Grid>

        {/* Right Column — Stats */}
        <Grid size={{ xs: 12, md: 7 }} component={motion.div} variants={fadeUp}>
          {/* XP & Level */}
          <Card sx={{ p: 3, mb: 3 }}>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
              XP & Level
            </Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                Level {profile.level}
              </Typography>
              <Typography variant="body2" sx={{ color: 'primary.main', fontWeight: 700 }}>
                <AnimatedValue value={profile.xp} /> XP gesamt
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={(xpInLevel / xpToNext) * 100}
              sx={{
                height: 10,
                borderRadius: 5,
                bgcolor: 'rgba(255,255,255,0.08)',
                mb: 1,
                '& .MuiLinearProgress-bar': { bgcolor: '#00A76F', borderRadius: 5 },
              }}
            />
            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
              {xpInLevel} / {xpToNext} XP zum naechsten Level
            </Typography>
          </Card>

          {/* Streak */}
          <Card sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
              <Typography variant="h4">{'\u{1F525}'}</Typography>
              <Box>
                <Typography variant="h5" fontWeight={700} sx={{ color: '#FF5630', lineHeight: 1 }}>
                  {profile.streak_days}
                </Typography>
                <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                  Tage Streak
                </Typography>
              </Box>
            </Box>
            <StreakCalendar streakDays={profile.streak_days} />
          </Card>

          {/* Recent Achievements */}
          <Card sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrophyIcon sx={{ color: '#8E33FF', fontSize: 20 }} />
                <Typography variant="subtitle1" fontWeight={700}>
                  Letzte Achievements
                </Typography>
              </Box>
              <Typography
                variant="body2"
                sx={{ color: 'primary.main', cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
                onClick={() => navigate('/achievements')}
              >
                Alle anzeigen
              </Typography>
            </Box>
            {unlockedAchievements.length === 0 ? (
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                Noch keine Achievements freigeschaltet
              </Typography>
            ) : (
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                {unlockedAchievements.map((a) => (
                  <Card
                    key={a.id}
                    sx={{
                      p: 2,
                      flex: '1 1 0',
                      minWidth: 120,
                      textAlign: 'center',
                      border: '1px solid rgba(142, 51, 255, 0.2)',
                    }}
                  >
                    <Typography variant="h5" sx={{ mb: 0.5 }}>{a.icon}</Typography>
                    <Typography variant="caption" fontWeight={600} sx={{ display: 'block' }}>
                      {a.name}
                    </Typography>
                  </Card>
                ))}
              </Box>
            )}
          </Card>

          {/* Learning Progress */}
          <Card sx={{ p: 3 }}>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 2 }}>
              Lernfortschritt
            </Typography>
            {paths.map((path) => (
              <Box key={path.id} sx={{ mb: 2, '&:last-child': { mb: 0 } }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography>{path.icon}</Typography>
                    <Typography variant="body2" fontWeight={600}>{path.title}</Typography>
                  </Box>
                  <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                    {path.completed_count}/{path.lessons_count} Lektionen
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={path.progress_percent}
                  sx={{
                    height: 6,
                    borderRadius: 3,
                    bgcolor: 'rgba(255,255,255,0.08)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: DIFFICULTY_COLORS[path.difficulty] || '#00A76F',
                      borderRadius: 3,
                    },
                  }}
                />
              </Box>
            ))}
          </Card>
        </Grid>
      </Grid>
    </motion.div>
  );
}
