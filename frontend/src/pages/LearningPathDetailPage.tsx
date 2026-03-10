import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Breadcrumbs,
  Button,
  Card,
  Chip,
  CircularProgress,
  LinearProgress,
  Link,
  Typography,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Lock as LockIcon,
  PlayArrow as PlayIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { fetchPath } from '../api/endpoints';

// ── Types ────────────────────────────────────────────────────

interface LessonData {
  id: number;
  slug: string;
  title: string;
  description: string;
  xp_reward: number;
  order: number;
  completed: boolean;
  completed_at: string | null;
}

interface PathData {
  id: number;
  slug: string;
  title: string;
  description: string;
  icon: string;
  difficulty: string;
  lessons_count: number;
  completed_count: number;
  progress_percent: number;
  total_xp: number;
  lessons: LessonData[];
}

// ── Constants ────────────────────────────────────────────────

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

const READING_TIMES = [5, 7, 8, 6, 10, 7, 5, 8, 6, 9];

// ── Animation ────────────────────────────────────────────────

const timelineItem = {
  hidden: { opacity: 0, x: -16 },
  show: { opacity: 1, x: 0 },
};

// ── Helpers ──────────────────────────────────────────────────

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('de-CH', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

// ── Main Component ───────────────────────────────────────────

export default function LearningPathDetailPage() {
  const { pathSlug } = useParams();
  const navigate = useNavigate();
  const [path, setPath] = useState<PathData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!pathSlug) return;
    fetchPath(pathSlug)
      .then(setPath)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [pathSlug]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', pt: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!path) {
    return <Typography color="error">Lernpfad nicht gefunden.</Typography>;
  }

  const chipColor = DIFFICULTY_COLORS[path.difficulty] || '#00A76F';
  const sortedLessons = [...path.lessons].sort((a, b) => a.order - b.order);
  const firstIncompleteIdx = sortedLessons.findIndex((l) => !l.completed);
  const nextLesson = firstIncompleteIdx >= 0 ? sortedLessons[firstIncompleteIdx] : null;

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
      {/* Breadcrumbs */}
      <Breadcrumbs sx={{ mb: 3 }}>
        <Link component={RouterLink} to="/learn" color="text.secondary" underline="hover">
          Lernpfade
        </Link>
        <Typography color="text.primary">{path.title}</Typography>
      </Breadcrumbs>

      {/* Hero Header */}
      <Card
        sx={{
          p: 4,
          mb: 4,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            inset: 0,
            background: `linear-gradient(135deg, ${chipColor}18 0%, transparent 60%)`,
            pointerEvents: 'none',
          }}
        />
        <Box sx={{ position: 'relative' }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 3, mb: 3 }}>
            <Typography sx={{ fontSize: 64, lineHeight: 1 }}>{path.icon}</Typography>
            <Box sx={{ flex: 1 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1, flexWrap: 'wrap' }}>
                <Typography variant="h4" fontWeight={700}>{path.title}</Typography>
                <Chip
                  label={DIFFICULTY_LABELS[path.difficulty] || path.difficulty}
                  size="small"
                  sx={{ bgcolor: `${chipColor}22`, color: chipColor, fontWeight: 600 }}
                />
                <Chip
                  label={`${path.total_xp} XP`}
                  size="small"
                  sx={{ fontWeight: 700, bgcolor: 'rgba(0,167,111,0.12)', color: '#00A76F' }}
                />
              </Box>
              <Typography variant="body1" sx={{ color: 'text.secondary', mb: 2 }}>
                {path.description}
              </Typography>

              {/* Progress */}
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <LinearProgress
                  variant="determinate"
                  value={path.progress_percent}
                  sx={{
                    flex: 1,
                    height: 8,
                    borderRadius: 4,
                    bgcolor: 'rgba(255,255,255,0.08)',
                    '& .MuiLinearProgress-bar': { bgcolor: chipColor, borderRadius: 4 },
                  }}
                />
                <Typography variant="body2" sx={{ color: 'text.secondary', flexShrink: 0 }}>
                  {path.completed_count}/{path.lessons_count} Lektionen — {path.progress_percent}%
                </Typography>
              </Box>
            </Box>
          </Box>

          {nextLesson && (
            <Button
              variant="contained"
              size="large"
              startIcon={<PlayIcon />}
              onClick={() => navigate(`/learn/${path.slug}/${nextLesson.slug}`)}
              sx={{ fontWeight: 700, px: 4 }}
            >
              Weiterlernen
            </Button>
          )}
          {!nextLesson && path.progress_percent === 100 && (
            <Chip
              label="Alle Lektionen abgeschlossen!"
              sx={{ fontWeight: 700, bgcolor: 'rgba(0,167,111,0.12)', color: '#00A76F', fontSize: 14, py: 2.5 }}
            />
          )}
        </Box>
      </Card>

      {/* Lessons Timeline */}
      <Typography variant="h6" fontWeight={700} sx={{ mb: 3 }}>
        Lektionen
      </Typography>

      <motion.div
        initial="hidden"
        animate="show"
        variants={{ hidden: {}, show: { transition: { staggerChildren: 0.06 } } }}
      >
        {sortedLessons.map((lesson, idx) => {
          const isCompleted = lesson.completed;
          const isCurrent = idx === firstIncompleteIdx;
          const isLocked = !isCompleted && !isCurrent;
          const isLast = idx === sortedLessons.length - 1;
          const lineColor = isCompleted ? '#00A76F' : 'rgba(255,255,255,0.1)';
          const readTime = READING_TIMES[idx % READING_TIMES.length];

          return (
            <motion.div key={lesson.id} variants={timelineItem} transition={{ duration: 0.25 }}>
              <Box
                onClick={() => navigate(`/learn/${path.slug}/${lesson.slug}`)}
                sx={{
                  display: 'flex',
                  gap: 2.5,
                  cursor: 'pointer',
                  position: 'relative',
                  opacity: isLocked ? 0.5 : 1,
                  transition: 'opacity 0.2s',
                  '&:hover': { opacity: isLocked ? 0.65 : 1 },
                  pb: isLast ? 0 : 0,
                }}
              >
                {/* Timeline column */}
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    width: 32,
                    flexShrink: 0,
                    pt: 0.5,
                  }}
                >
                  {/* Dot */}
                  <Box
                    sx={{
                      width: 32,
                      height: 32,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                      bgcolor: isCompleted
                        ? '#00A76F'
                        : isCurrent
                          ? 'transparent'
                          : 'rgba(255,255,255,0.08)',
                      border: isCurrent ? '2px solid #00A76F' : 'none',
                      ...(isCurrent && {
                        animation: 'detailPulse 2s ease-in-out infinite',
                        '@keyframes detailPulse': {
                          '0%, 100%': { boxShadow: '0 0 0 0 rgba(0,167,111,0.4)' },
                          '50%': { boxShadow: '0 0 0 10px rgba(0,167,111,0)' },
                        },
                      }),
                    }}
                  >
                    {isCompleted ? (
                      <CheckIcon sx={{ fontSize: 18, color: '#fff' }} />
                    ) : isLocked ? (
                      <LockIcon sx={{ fontSize: 14, color: 'text.secondary' }} />
                    ) : (
                      <Typography variant="caption" fontWeight={700} sx={{ color: '#00A76F' }}>
                        {idx + 1}
                      </Typography>
                    )}
                  </Box>

                  {/* Line */}
                  {!isLast && (
                    <Box
                      sx={{
                        width: 2,
                        flexGrow: 1,
                        mt: 0.5,
                        minHeight: 24,
                        bgcolor: lineColor,
                        borderRadius: 1,
                      }}
                    />
                  )}
                </Box>

                {/* Content */}
                <Card
                  sx={{
                    flex: 1,
                    p: 2.5,
                    mb: isLast ? 0 : 2,
                    transition: 'background-color 0.2s, border-color 0.2s',
                    border: '1px solid transparent',
                    ...(isCurrent && {
                      bgcolor: 'rgba(0, 167, 111, 0.04)',
                      borderColor: 'rgba(0, 167, 111, 0.2)',
                    }),
                    '&:hover': {
                      bgcolor: isCurrent
                        ? 'rgba(0, 167, 111, 0.08)'
                        : 'rgba(255,255,255,0.02)',
                    },
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 1, mb: 0.5 }}>
                    <Typography variant="subtitle1" fontWeight={isCurrent ? 700 : 600}>
                      {lesson.title}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexShrink: 0 }}>
                      <Chip
                        label={`~${readTime} Min`}
                        size="small"
                        sx={{ fontSize: 11, height: 22, bgcolor: 'rgba(255,255,255,0.06)', color: 'text.secondary' }}
                      />
                      <Chip
                        label={`+${lesson.xp_reward} XP`}
                        size="small"
                        sx={{
                          fontWeight: 600,
                          fontSize: 11,
                          height: 22,
                          bgcolor: isCompleted ? 'rgba(0,167,111,0.12)' : 'rgba(255,255,255,0.06)',
                          color: isCompleted ? '#00A76F' : 'text.secondary',
                        }}
                      />
                    </Box>
                  </Box>

                  {lesson.description && (
                    <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>
                      {lesson.description}
                    </Typography>
                  )}

                  {isCompleted && lesson.completed_at && (
                    <Typography variant="caption" sx={{ color: '#00A76F' }}>
                      Abgeschlossen am {formatDate(lesson.completed_at)}
                    </Typography>
                  )}

                  {isCurrent && (
                    <Button
                      size="small"
                      variant="contained"
                      startIcon={<PlayIcon />}
                      sx={{ mt: 1, fontWeight: 600, textTransform: 'none' }}
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/learn/${path.slug}/${lesson.slug}`);
                      }}
                    >
                      Jetzt starten
                    </Button>
                  )}
                </Card>
              </Box>
            </motion.div>
          );
        })}
      </motion.div>
    </motion.div>
  );
}
