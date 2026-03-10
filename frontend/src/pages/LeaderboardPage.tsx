import { useEffect, useState } from 'react';
import {
  Avatar,
  Box,
  Card,
  Chip,
  Skeleton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from '@mui/material';
import { EmojiEvents as TrophyIcon } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { fetchLeaderboard } from '../api/endpoints';
import { useAuth } from '../contexts/AuthContext';

interface LeaderboardEntry {
  id: number;
  username: string;
  display_name: string;
  xp: number;
  level: number;
  streak_days: number;
  avatar_color: string;
}

const MEDALS: Record<number, string> = { 1: '\u{1F947}', 2: '\u{1F948}', 3: '\u{1F949}' };

const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0 },
};

function AnimatedXP({ value }: { value: number }) {
  const [display, setDisplay] = useState(0);

  useEffect(() => {
    const start = performance.now();
    const duration = 600;
    function tick(now: number) {
      const p = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setDisplay(Math.round(eased * value));
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }, [value]);

  return <>{display}</>;
}

function SkeletonRows() {
  return (
    <>
      {Array.from({ length: 6 }).map((_, i) => (
        <TableRow key={i}>
          <TableCell><Skeleton width={30} /></TableCell>
          <TableCell>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Skeleton variant="circular" width={36} height={36} />
              <Skeleton width={100} />
            </Box>
          </TableCell>
          <TableCell><Skeleton width={60} /></TableCell>
          <TableCell align="right"><Skeleton width={50} /></TableCell>
          <TableCell align="right"><Skeleton width={40} /></TableCell>
        </TableRow>
      ))}
    </>
  );
}

export default function LeaderboardPage() {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const { username } = useAuth();

  useEffect(() => {
    fetchLeaderboard()
      .then(setEntries)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 4 }}>
        <TrophyIcon sx={{ fontSize: 32, color: '#FFC107' }} />
        <Typography variant="h4" fontWeight={700}>
          Leaderboard
        </Typography>
      </Box>

      <Card sx={{ overflow: 'hidden' }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 700, width: 60 }}>Rang</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Name</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Level</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">XP</TableCell>
                <TableCell sx={{ fontWeight: 700 }} align="right">Streak</TableCell>
              </TableRow>
            </TableHead>
            <TableBody
              component={motion.tbody}
              variants={{ hidden: {}, show: { transition: { staggerChildren: 0.06 } } }}
              initial="hidden"
              animate="show"
            >
              {loading ? (
                <SkeletonRows />
              ) : entries.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} sx={{ textAlign: 'center', py: 6, color: 'text.secondary' }}>
                    Noch keine Eintr&auml;ge
                  </TableCell>
                </TableRow>
              ) : (
                entries.map((entry, idx) => {
                  const rank = idx + 1;
                  const isMe = entry.username === username;
                  const initials = entry.display_name
                    .split(' ')
                    .map((n) => n[0])
                    .join('')
                    .slice(0, 2);

                  return (
                    <TableRow
                      key={entry.id}
                      component={motion.tr}
                      variants={fadeUp}
                      transition={{ duration: 0.25 }}
                      sx={{
                        ...(isMe && {
                          bgcolor: 'rgba(0, 167, 111, 0.08)',
                          '& td': { fontWeight: 600 },
                        }),
                        '&:last-child td': { borderBottom: 0 },
                      }}
                    >
                      <TableCell>
                        {MEDALS[rank] ? (
                          <Typography variant="h6">{MEDALS[rank]}</Typography>
                        ) : (
                          <Typography variant="body1" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                            {rank}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                          <Avatar
                            sx={{
                              width: 36,
                              height: 36,
                              bgcolor: entry.avatar_color,
                              fontSize: 14,
                              fontWeight: 700,
                            }}
                          >
                            {initials}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight={600}>
                              {entry.display_name}
                              {isMe && (
                                <Typography
                                  component="span"
                                  variant="caption"
                                  sx={{ ml: 1, color: 'primary.main' }}
                                >
                                  (Du)
                                </Typography>
                              )}
                            </Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`Level ${entry.level}`}
                          size="small"
                          sx={{
                            fontWeight: 600,
                            bgcolor: 'rgba(142, 51, 255, 0.12)',
                            color: '#8E33FF',
                          }}
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" sx={{ color: 'primary.main', fontWeight: 700 }}>
                          <AnimatedXP value={entry.xp} /> XP
                        </Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                          {entry.streak_days > 0 ? `\u{1F525} ${entry.streak_days}` : '-'}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  );
                })
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </motion.div>
  );
}
