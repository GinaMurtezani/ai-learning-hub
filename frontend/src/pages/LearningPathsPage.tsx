import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Card,
  Chip,
  Collapse,
  LinearProgress,
  Skeleton,
  Typography,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  ExpandMore as ExpandMoreIcon,
  Lock as LockIcon,
  School as SchoolIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import { fetchPaths } from '../api/endpoints';

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
  order: number;
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

// ── Animation ────────────────────────────────────────────────

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.3 } },
};

const timelineItem = {
  hidden: { opacity: 0, x: -12 },
  show: { opacity: 1, x: 0 },
};

// ── Helpers ──────────────────────────────────────────────────

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('de-CH', {
    day: 'numeric',
    month: 'short',
  });
}

// ── Skeleton ─────────────────────────────────────────────────

function PathSkeleton() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {Array.from({ length: 3 }).map((_, i) => (
        <Card key={i} sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <Skeleton variant="rounded" width={48} height={48} />
            <Box sx={{ flex: 1 }}>
              <Skeleton width="40%" height={28} />
              <Skeleton width="70%" height={16} sx={{ mt: 1 }} />
            </Box>
          </Box>
          <Skeleton height={6} sx={{ borderRadius: 3 }} />
        </Card>
      ))}
    </Box>
  );
}

// ── Timeline Lesson Item ─────────────────────────────────────

function TimelineLesson({
  lesson,
  index,
  isLast,
  isCurrent,
  pathSlug,
}: {
  lesson: LessonData;
  index: number;
  isLast: boolean;
  isCurrent: boolean;
  pathSlug: string;
}) {
  const navigate = useNavigate();
  const isCompleted = lesson.completed;
  const isLocked = !isCompleted && !isCurrent;

  const lineColor = isCompleted ? '#00A76F' : 'rgba(255,255,255,0.1)';
  const dotSize = isCurrent ? 28 : 24;

  return (
    <motion.div variants={timelineItem} transition={{ duration: 0.25 }}>
      <Box
        onClick={() => navigate(`/learn/${pathSlug}/${lesson.slug}`)}
        sx={{
          display: 'flex',
          gap: 2,
          cursor: 'pointer',
          position: 'relative',
          opacity: isLocked ? 0.5 : 1,
          transition: 'opacity 0.2s',
          '&:hover': { opacity: isLocked ? 0.65 : 1 },
          pb: isLast ? 0 : 3,
        }}
      >
        {/* Timeline column */}
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: 28,
            flexShrink: 0,
            pt: 0.25,
          }}
        >
          {/* Dot */}
          <Box
            sx={{
              width: dotSize,
              height: dotSize,
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
                animation: 'timelinePulse 2s ease-in-out infinite',
                '@keyframes timelinePulse': {
                  '0%, 100%': { boxShadow: '0 0 0 0 rgba(0,167,111,0.4)' },
                  '50%': { boxShadow: '0 0 0 8px rgba(0,167,111,0)' },
                },
              }),
            }}
          >
            {isCompleted ? (
              <CheckIcon sx={{ fontSize: 16, color: '#fff' }} />
            ) : isLocked ? (
              <LockIcon sx={{ fontSize: 12, color: 'text.secondary' }} />
            ) : null}
          </Box>

          {/* Line */}
          {!isLast && (
            <Box
              sx={{
                width: 2,
                flexGrow: 1,
                mt: 0.5,
                bgcolor: lineColor,
                borderRadius: 1,
              }}
            />
          )}
        </Box>

        {/* Content */}
        <Box
          sx={{
            flex: 1,
            p: 1.5,
            borderRadius: 1.5,
            transition: 'background-color 0.2s',
            ...(isCurrent && {
              bgcolor: 'rgba(0, 167, 111, 0.06)',
              border: '1px solid rgba(0, 167, 111, 0.15)',
            }),
            '&:hover': {
              bgcolor: isCurrent
                ? 'rgba(0, 167, 111, 0.1)'
                : 'rgba(255,255,255,0.03)',
            },
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 1 }}>
            <Typography variant="body2" fontWeight={isCurrent ? 700 : isCompleted ? 500 : 400}>
              {index + 1}. {lesson.title}
            </Typography>
            <Chip
              label={`+${lesson.xp_reward} XP`}
              size="small"
              sx={{
                fontWeight: 600,
                fontSize: 11,
                height: 22,
                flexShrink: 0,
                bgcolor: isCompleted ? 'rgba(0,167,111,0.12)' : 'rgba(255,255,255,0.06)',
                color: isCompleted ? '#00A76F' : 'text.secondary',
              }}
            />
          </Box>

          {lesson.description && (
            <Typography
              variant="caption"
              sx={{
                color: 'text.secondary',
                display: 'block',
                mt: 0.5,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {lesson.description}
            </Typography>
          )}

          {isCompleted && lesson.completed_at && (
            <Typography variant="caption" sx={{ color: '#00A76F', mt: 0.5, display: 'block' }}>
              Abgeschlossen am {formatDate(lesson.completed_at)}
            </Typography>
          )}

          {isCurrent && (
            <Button
              size="small"
              variant="contained"
              sx={{ mt: 1, fontWeight: 600, textTransform: 'none', px: 2 }}
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/learn/${pathSlug}/${lesson.slug}`);
              }}
            >
              Jetzt starten
            </Button>
          )}
        </Box>
      </Box>
    </motion.div>
  );
}

// ── Path Card ────────────────────────────────────────────────

function PathCard({
  path,
  expanded,
  onToggle,
}: {
  path: PathData;
  expanded: boolean;
  onToggle: () => void;
}) {
  const chipColor = DIFFICULTY_COLORS[path.difficulty] || '#00A76F';
  const sortedLessons = [...path.lessons].sort((a, b) => a.order - b.order);
  const firstIncompleteIdx = sortedLessons.findIndex((l) => !l.completed);

  return (
    <Card
      sx={{
        overflow: 'hidden',
        transition: 'box-shadow 0.3s',
        ...(expanded && {
          boxShadow: `0 0 24px ${chipColor}15`,
        }),
      }}
    >
      {/* Header — always visible */}
      <Box
        onClick={onToggle}
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 2,
          p: 3,
          cursor: 'pointer',
          transition: 'background-color 0.2s',
          '&:hover': { bgcolor: 'rgba(255,255,255,0.02)' },
        }}
      >
        <Typography variant="h3" sx={{ lineHeight: 1, flexShrink: 0 }}>
          {path.icon}
        </Typography>

        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 0.5, flexWrap: 'wrap' }}>
            <Typography variant="h6" fontWeight={700} noWrap>
              {path.title}
            </Typography>
            <Chip
              label={DIFFICULTY_LABELS[path.difficulty] || path.difficulty}
              size="small"
              sx={{ bgcolor: `${chipColor}22`, color: chipColor, fontWeight: 600 }}
            />
          </Box>
          <Typography
            variant="body2"
            sx={{ color: 'text.secondary', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
          >
            {path.description}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mt: 1.5 }}>
            <LinearProgress
              variant="determinate"
              value={path.progress_percent}
              sx={{
                flex: 1,
                height: 6,
                borderRadius: 3,
                bgcolor: 'rgba(255,255,255,0.08)',
                '& .MuiLinearProgress-bar': { bgcolor: chipColor, borderRadius: 3 },
              }}
            />
            <Typography variant="caption" sx={{ color: 'text.secondary', flexShrink: 0 }}>
              {path.completed_count}/{path.lessons_count} — {path.progress_percent}%
            </Typography>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 0.5, flexShrink: 0 }}>
          <Chip
            label={`${path.total_xp} XP`}
            size="small"
            sx={{ fontWeight: 700, bgcolor: 'rgba(0,167,111,0.12)', color: '#00A76F' }}
          />
          <ExpandMoreIcon
            sx={{
              color: 'text.secondary',
              transition: 'transform 0.3s',
              transform: expanded ? 'rotate(180deg)' : 'none',
            }}
          />
        </Box>
      </Box>

      {/* Body — collapsible */}
      <Collapse in={expanded} timeout={300}>
        <Box sx={{ px: 3, pb: 3, pt: 1 }}>
          <AnimatePresence>
            {expanded && (
              <motion.div
                initial="hidden"
                animate="show"
                variants={{ hidden: {}, show: { transition: { staggerChildren: 0.05 } } }}
              >
                {sortedLessons.map((lesson, idx) => (
                  <TimelineLesson
                    key={lesson.id}
                    lesson={lesson}
                    index={idx}
                    isLast={idx === sortedLessons.length - 1}
                    isCurrent={idx === firstIncompleteIdx}
                    pathSlug={path.slug}
                  />
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </Box>
      </Collapse>
    </Card>
  );
}

// ── Main Component ───────────────────────────────────────────

export default function LearningPathsPage() {
  const [paths, setPaths] = useState<PathData[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedSlug, setExpandedSlug] = useState<string | null>(null);

  useEffect(() => {
    fetchPaths()
      .then((data: PathData[]) => {
        setPaths(data);
        // Auto-expand first path with progress, or first incomplete
        const withProgress = data.find((p) => p.progress_percent > 0 && p.progress_percent < 100);
        const firstIncomplete = data.find((p) => p.progress_percent < 100);
        setExpandedSlug((withProgress || firstIncomplete || data[0])?.slug ?? null);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const totalLessons = paths.reduce((s, p) => s + p.lessons_count, 0);
  const totalCompleted = paths.reduce((s, p) => s + p.completed_count, 0);
  const overallPercent = totalLessons > 0 ? Math.round((totalCompleted / totalLessons) * 100) : 0;

  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
          <SchoolIcon sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" fontWeight={700}>
            Lernpfade
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ color: 'text.secondary', mb: 2 }}>
          Waehle deinen Lernpfad und starte deine AI-Reise
        </Typography>

        {!loading && totalLessons > 0 && (
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                {totalCompleted} von {totalLessons} Lektionen abgeschlossen
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                {overallPercent}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={overallPercent}
              sx={{
                height: 6,
                borderRadius: 3,
                bgcolor: 'rgba(255,255,255,0.08)',
                '& .MuiLinearProgress-bar': { bgcolor: '#00A76F', borderRadius: 3 },
              }}
            />
          </Box>
        )}
      </Box>

      {/* Path Cards */}
      {loading ? (
        <PathSkeleton />
      ) : (
        <motion.div variants={container} initial="hidden" animate="show">
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {paths.map((path) => (
              <motion.div key={path.id} variants={fadeUp}>
                <PathCard
                  path={path}
                  expanded={expandedSlug === path.slug}
                  onToggle={() =>
                    setExpandedSlug((prev) => (prev === path.slug ? null : path.slug))
                  }
                />
              </motion.div>
            ))}
          </Box>
        </motion.div>
      )}
    </motion.div>
  );
}
