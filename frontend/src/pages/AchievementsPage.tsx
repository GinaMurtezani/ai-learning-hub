import { useEffect, useState } from 'react';
import {
  Box,
  Card,
  Chip,
  Grid,
  LinearProgress,
  Skeleton,
  Typography,
} from '@mui/material';
import { EmojiEvents as TrophyIcon, Lock as LockIcon } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { fetchAchievements } from '../api/endpoints';

interface AchievementData {
  id: number;
  slug: string;
  name: string;
  description: string;
  icon: string;
  xp_reward: number;
  requirement_type: string;
  requirement_value: number;
  unlocked: boolean;
  unlocked_at: string | null;
  progress: { current: number; target: number };
}

const REQUIREMENT_LABELS: Record<string, string> = {
  lessons_completed: 'Lektionen',
  streak: 'Tage Streak',
  xp_total: 'XP',
  first_chat: 'Chat',
};

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('de-CH', { day: 'numeric', month: 'long', year: 'numeric' });
}

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

function SkeletonCards() {
  return (
    <Grid container spacing={3}>
      {Array.from({ length: 5 }).map((_, i) => (
        <Grid size={{ xs: 12, sm: 6, md: 4 }} key={i}>
          <Card sx={{ p: 3 }}>
            <Skeleton variant="circular" width={48} height={48} sx={{ mb: 2 }} />
            <Skeleton width="60%" height={24} sx={{ mb: 1 }} />
            <Skeleton width="80%" height={16} sx={{ mb: 2 }} />
            <Skeleton width="40%" height={14} />
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}

export default function AchievementsPage() {
  const [achievements, setAchievements] = useState<AchievementData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAchievements()
      .then(setAchievements)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const unlockedCount = achievements.filter((a) => a.unlocked).length;
  const totalCount = achievements.length;
  const progressPercent = totalCount > 0 ? Math.round((unlockedCount / totalCount) * 100) : 0;

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
        <TrophyIcon sx={{ fontSize: 32, color: '#8E33FF' }} />
        <Typography variant="h4" fontWeight={700}>
          Achievements
        </Typography>
      </Box>

      {/* Stats bar */}
      {!loading && totalCount > 0 && (
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              {unlockedCount} von {totalCount} freigeschaltet
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              {progressPercent}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={progressPercent}
            sx={{
              height: 8,
              borderRadius: 4,
              bgcolor: 'rgba(255,255,255,0.08)',
              '& .MuiLinearProgress-bar': { bgcolor: '#8E33FF', borderRadius: 4 },
            }}
          />
        </Box>
      )}

      {/* Grid */}
      {loading ? (
        <SkeletonCards />
      ) : (
        <Grid
          container
          spacing={3}
          component={motion.div}
          variants={container}
          initial="hidden"
          animate="show"
        >
          {achievements.map((a) => (
            <Grid size={{ xs: 12, sm: 6, md: 4 }} key={a.id} component={motion.div} variants={fadeUp}>
              <Card
                sx={{
                  p: 3,
                  position: 'relative',
                  overflow: 'hidden',
                  opacity: a.unlocked ? 1 : 0.5,
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  ...(a.unlocked && {
                    border: '1px solid rgba(142, 51, 255, 0.3)',
                    boxShadow: '0 0 20px rgba(142, 51, 255, 0.08)',
                    '&:hover': {
                      transform: 'scale(1.02)',
                      boxShadow: '0 0 30px rgba(142, 51, 255, 0.15)',
                    },
                  }),
                }}
              >
                {/* Icon */}
                <Box sx={{ position: 'relative', display: 'inline-block', mb: 2 }}>
                  <Typography
                    variant="h3"
                    sx={{
                      filter: a.unlocked ? 'none' : 'grayscale(1)',
                      lineHeight: 1,
                    }}
                  >
                    {a.icon}
                  </Typography>
                  {!a.unlocked && (
                    <LockIcon
                      sx={{
                        position: 'absolute',
                        bottom: -4,
                        right: -8,
                        fontSize: 18,
                        color: 'text.secondary',
                        bgcolor: 'background.paper',
                        borderRadius: '50%',
                        p: 0.25,
                      }}
                    />
                  )}
                </Box>

                {/* Name */}
                <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 0.5 }}>
                  {a.name}
                </Typography>

                {/* Description */}
                <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2, minHeight: 40 }}>
                  {a.description}
                </Typography>

                {/* XP Badge */}
                <Chip
                  label={`+${a.xp_reward} XP`}
                  size="small"
                  sx={{
                    fontWeight: 700,
                    bgcolor: a.unlocked ? 'rgba(0, 167, 111, 0.12)' : 'rgba(255,255,255,0.06)',
                    color: a.unlocked ? '#00A76F' : 'text.secondary',
                    mb: 1.5,
                  }}
                />

                {/* Unlocked date or progress */}
                {a.unlocked && a.unlocked_at ? (
                  <Typography variant="caption" sx={{ display: 'block', color: '#8E33FF' }}>
                    Freigeschaltet am {formatDate(a.unlocked_at)}
                  </Typography>
                ) : (
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        {a.progress.current}/{a.progress.target}{' '}
                        {REQUIREMENT_LABELS[a.requirement_type] || ''}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={
                        a.progress.target > 0
                          ? Math.round((a.progress.current / a.progress.target) * 100)
                          : 0
                      }
                      sx={{
                        height: 4,
                        borderRadius: 2,
                        bgcolor: 'rgba(255,255,255,0.06)',
                        '& .MuiLinearProgress-bar': { bgcolor: 'text.secondary', borderRadius: 2 },
                      }}
                    />
                  </Box>
                )}
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </motion.div>
  );
}
