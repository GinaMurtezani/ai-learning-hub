import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Breadcrumbs,
  Button,
  Chip,
  CircularProgress,
  Grid,
  LinearProgress,
  Link,
  Snackbar,
  Alert,
  Typography,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  EmojiEvents as TrophyIcon,
  NavigateNext as NextIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { fetchLesson, fetchPath, completeLesson } from '../api/endpoints';
import ChatPanel from '../components/ChatPanel';

interface LessonData {
  id: number;
  slug: string;
  title: string;
  description: string;
  content: string;
  xp_reward: number;
  ai_system_prompt: string;
}

interface PathLessonData {
  slug: string;
  title: string;
  order: number;
  completed: boolean;
}

interface PathData {
  slug: string;
  title: string;
  icon: string;
  difficulty: string;
  progress_percent: number;
  lessons_count: number;
  completed_count: number;
  lessons: PathLessonData[];
}

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: '#00A76F',
  intermediate: '#FFC107',
  advanced: '#FF5630',
};

const DIFFICULTY_LABELS: Record<string, string> = {
  beginner: 'Einsteiger',
  intermediate: 'Mittel',
  advanced: 'Fortgeschritten',
};

export default function LessonPage() {
  const { pathSlug, lessonSlug } = useParams();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState<LessonData | null>(null);
  const [path, setPath] = useState<PathData | null>(null);
  const [completed, setCompleted] = useState(false);
  const [completing, setCompleting] = useState(false);
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string }>({
    open: false,
    message: '',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [lessonData, pathData] = await Promise.all([
          fetchLesson(lessonSlug!),
          pathSlug ? fetchPath(pathSlug) : null,
        ]);
        setLesson(lessonData);
        setPath(pathData);
      } catch {
        // Error handled by loading state
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [lessonSlug, pathSlug]);

  const handleComplete = async () => {
    if (!lesson || completed || completing) return;
    setCompleting(true);
    try {
      const result = await completeLesson(lesson.slug);
      if (result.already_completed) {
        setCompleted(true);
      } else {
        setCompleted(true);
        setSnackbar({ open: true, message: `+${lesson.xp_reward} XP erhalten!` });
      }
    } catch {
      setSnackbar({ open: true, message: 'Fehler beim Abschliessen.' });
    } finally {
      setCompleting(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!lesson) {
    return <Typography color="error">Lektion nicht gefunden.</Typography>;
  }

  const diffColor = path ? DIFFICULTY_COLORS[path.difficulty] || '#919EAB' : '#919EAB';

  return (
    <>
      <Grid container spacing={3} sx={{ height: 'calc(100vh - 100px)' }}>
        {/* Left: Lesson content */}
        <Grid size={{ xs: 12, md: 7 }}>
          <Box sx={{ height: '100%', overflow: 'auto', pr: { md: 2 } }}>
            {/* Breadcrumb */}
            {path && (
              <Breadcrumbs sx={{ mb: 2 }}>
                <Link component={RouterLink} to="/learn" color="text.secondary" underline="hover">
                  Lernpfade
                </Link>
                <Link
                  component={RouterLink}
                  to={`/learn/${path.slug}`}
                  color="text.secondary"
                  underline="hover"
                >
                  {path.icon} {path.title}
                </Link>
                <Typography color="text.primary">{lesson.title}</Typography>
              </Breadcrumbs>
            )}

            <Typography variant="h4" fontWeight={700} sx={{ mb: 1 }}>
              {lesson.title}
            </Typography>

            {path && (
              <Chip
                label={DIFFICULTY_LABELS[path.difficulty] || path.difficulty}
                size="small"
                sx={{
                  bgcolor: `${diffColor}22`,
                  color: diffColor,
                  fontWeight: 600,
                  mb: 3,
                }}
              />
            )}

            {/* Markdown content */}
            <Box
              sx={{
                '& h2': { mt: 3, mb: 1.5, color: 'text.primary' },
                '& h3': { mt: 2, mb: 1, color: 'text.primary' },
                '& p': { mb: 1.5, color: 'text.secondary', lineHeight: 1.7 },
                '& ul, & ol': { color: 'text.secondary', mb: 1.5 },
                '& li': { mb: 0.5 },
                '& code': {
                  bgcolor: 'background.default',
                  px: 0.5,
                  py: 0.25,
                  borderRadius: 0.5,
                  fontSize: '0.85em',
                },
                '& pre': {
                  bgcolor: 'background.default',
                  p: 2,
                  borderRadius: 1,
                  overflow: 'auto',
                  mb: 2,
                },
                '& blockquote': {
                  borderLeft: '3px solid',
                  borderColor: 'primary.main',
                  pl: 2,
                  ml: 0,
                  color: 'text.secondary',
                  fontStyle: 'italic',
                },
                '& table': {
                  width: '100%',
                  borderCollapse: 'collapse',
                  mb: 2,
                },
                '& th, & td': {
                  border: '1px solid',
                  borderColor: 'divider',
                  px: 1.5,
                  py: 1,
                  textAlign: 'left',
                },
                '& strong': { color: 'text.primary' },
              }}
            >
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {lesson.content}
              </ReactMarkdown>
            </Box>

            {/* Progress + Complete */}
            {path && (() => {
              const sortedLessons = [...path.lessons].sort((a, b) => a.order - b.order);
              const currentIdx = sortedLessons.findIndex((l) => l.slug === lessonSlug);
              const progressValue = completed
                ? Math.round(((path.completed_count + (sortedLessons[currentIdx]?.completed ? 0 : 1)) / path.lessons_count) * 100)
                : path.progress_percent;
              const nextLesson = currentIdx >= 0 && currentIdx < sortedLessons.length - 1
                ? sortedLessons[currentIdx + 1]
                : null;

              return (
                <Box sx={{ mt: 3, mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      Fortschritt: {path.icon} {path.title}
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      {Math.min(progressValue, 100)}%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min(progressValue, 100)}
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      bgcolor: 'rgba(255,255,255,0.08)',
                      mb: 2,
                      '& .MuiLinearProgress-bar': { bgcolor: diffColor, borderRadius: 3 },
                    }}
                  />

                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                    <Button
                      variant="contained"
                      size="large"
                      onClick={handleComplete}
                      disabled={completed || completing}
                      startIcon={completed ? <CheckIcon /> : <TrophyIcon />}
                      sx={{
                        fontWeight: 700,
                        px: 4,
                        ...(completed && {
                          bgcolor: 'rgba(0, 167, 111, 0.16)',
                          color: 'primary.main',
                          '&.Mui-disabled': {
                            bgcolor: 'rgba(0, 167, 111, 0.16)',
                            color: 'primary.main',
                          },
                        }),
                      }}
                    >
                      {completing ? (
                        <CircularProgress size={20} color="inherit" />
                      ) : completed ? (
                        'Abgeschlossen'
                      ) : (
                        `Lektion abschliessen (+${lesson.xp_reward} XP)`
                      )}
                    </Button>

                    {completed && nextLesson && (
                      <Button
                        variant="outlined"
                        size="large"
                        endIcon={<NextIcon />}
                        onClick={() => navigate(`/learn/${path.slug}/${nextLesson.slug}`)}
                        sx={{ fontWeight: 700, px: 4 }}
                      >
                        Nächste Lektion
                      </Button>
                    )}
                  </Box>
                </Box>
              );
            })()}

            {!path && (
              <Button
                variant="contained"
                size="large"
                onClick={handleComplete}
                disabled={completed || completing}
                startIcon={completed ? <CheckIcon /> : <TrophyIcon />}
                sx={{
                  mb: 4,
                  fontWeight: 700,
                  px: 4,
                  ...(completed && {
                    bgcolor: 'rgba(0, 167, 111, 0.16)',
                    color: 'primary.main',
                    '&.Mui-disabled': {
                      bgcolor: 'rgba(0, 167, 111, 0.16)',
                      color: 'primary.main',
                    },
                  }),
                }}
              >
                {completing ? (
                  <CircularProgress size={20} color="inherit" />
                ) : completed ? (
                  'Abgeschlossen'
                ) : (
                  `Lektion abschliessen (+${lesson.xp_reward} XP)`
                )}
              </Button>
            )}
          </Box>
        </Grid>

        {/* Right: Chat */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Box sx={{ height: { xs: 500, md: '100%' } }}>
            <ChatPanel
              lessonId={lesson.id}
              lessonTitle={lesson.title}
              welcomeMessage={`Hallo! Ich bin dein AI-Tutor f\u00fcr diese Lektion. Stelle mir eine Frage!`}
            />
          </Box>
        </Grid>
      </Grid>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          severity="success"
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          sx={{ bgcolor: 'primary.main', color: '#fff' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
}
